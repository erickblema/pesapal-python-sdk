"""Webhook processing service."""

import logging
from typing import Dict, Any
from datetime import datetime

from pesapal.utils import verify_webhook_signature
from pesapal.exceptions import PesapalError

from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService
from app.config.settings import settings

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for processing Pesapal webhooks."""
    
    def __init__(self):
        self.repository = PaymentRepository()
        self.payment_service = PaymentService()
    
    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verify webhook signature.
        
        Args:
            data: Webhook data
            signature: Signature to verify
            
        Returns:
            True if signature is valid
        """
        if not settings.pesapal_consumer_secret:
            raise ValueError("Pesapal consumer secret not configured")
        
        return verify_webhook_signature(data, signature, settings.pesapal_consumer_secret)
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Process webhook notification from Pesapal v3.
        
        Args:
            webhook_data: Webhook payload from Pesapal
            
        Returns:
            True if processed successfully
        """
        order_tracking_id = (
            webhook_data.get("OrderTrackingId") or
            webhook_data.get("order_tracking_id") or
            webhook_data.get("orderTrackingId") or
            webhook_data.get("tracking_id")
        )
        
        order_merchant_reference = (
            webhook_data.get("OrderMerchantReference") or
            webhook_data.get("order_merchant_reference") or
            webhook_data.get("orderMerchantReference") or
            webhook_data.get("merchant_reference") or
            webhook_data.get("OrderReference") or
            webhook_data.get("order_reference")
        )
        
        order_notification_type = (
            webhook_data.get("OrderNotificationType") or
            webhook_data.get("order_notification_type") or
            webhook_data.get("orderNotificationType") or
            webhook_data.get("notification_type")
        )
        
        order_status = (
            webhook_data.get("OrderStatus") or
            webhook_data.get("order_status") or
            webhook_data.get("orderStatus") or
            webhook_data.get("status")
        )
        
        payment_method = (
            webhook_data.get("PaymentMethod") or
            webhook_data.get("payment_method") or
            webhook_data.get("paymentMethod")
        )
        
        confirmation_code = (
            webhook_data.get("ConfirmationCode") or
            webhook_data.get("confirmation_code") or
            webhook_data.get("confirmationCode")
        )
        
        logger.info(f"Processing webhook: tracking_id={order_tracking_id}, order_ref={order_merchant_reference}, type={order_notification_type}")
        
        if not order_tracking_id and not order_merchant_reference:
            logger.error(f"Invalid webhook data: missing required fields. Data: {webhook_data}")
            raise ValueError("Invalid webhook data: missing OrderTrackingId or OrderMerchantReference")
        
        payment = None
        if order_tracking_id:
            payment = await self.repository.get_by_tracking_id(order_tracking_id)
        if not payment and order_merchant_reference:
            payment = await self.repository.get_by_order_id(order_merchant_reference)
        
        if not payment:
            logger.warning(f"Webhook received for unknown payment: tracking_id={order_tracking_id}, order_id={order_merchant_reference}")
            return False
        
        await self.repository.collection.update_one(
            {"order_id": payment.order_id},
            {
                "$set": {
                    "webhook_received": True,
                    "webhook_received_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        webhook_event = {
            "event_type": "WEBHOOK_RECEIVED",
            "status": payment.status,
            "source": "WEBHOOK",
            "metadata": {
                "order_tracking_id": order_tracking_id,
                "order_notification_type": order_notification_type,
                "order_merchant_reference": order_merchant_reference,
                "webhook_data": webhook_data
            },
            "timestamp": datetime.utcnow()
        }
        await self.repository.add_event(payment.order_id, webhook_event)
        
        try:
            logger.info(f"Fetching payment status from Pesapal for order_id={payment.order_id}")
            old_status = payment.status
            updated_payment = await self.payment_service.check_payment_status(payment.order_id)
            
            status_update_event = {
                "event_type": "STATUS_UPDATED_VIA_WEBHOOK",
                "status": updated_payment.status,
                "source": "WEBHOOK",
                "metadata": {
                    "old_status": old_status,
                    "new_status": updated_payment.status,
                    "payment_method": updated_payment.payment_method,
                    "confirmation_code": updated_payment.confirmation_code,
                    "triggered_by": "GetTransactionStatus API"
                },
                "timestamp": datetime.utcnow()
            }
            await self.repository.add_event(payment.order_id, status_update_event)
            
            logger.info(f"Payment status updated via webhook: order_id={payment.order_id}, status={old_status} -> {updated_payment.status}")
            return True
        except Exception as e:
            logger.error(f"Error fetching payment status from Pesapal: {e}")
            if order_status:
                await self.repository.update_status(
                    payment.order_id,
                    order_status,
                    payment_method,
                    confirmation_code
                )
                logger.info(f"Payment status updated via webhook (fallback): order_id={payment.order_id}, status={order_status}")
                return True
            return False

