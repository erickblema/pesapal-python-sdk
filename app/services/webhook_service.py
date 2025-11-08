"""Webhook processing service."""

import logging
from typing import Dict, Any
from datetime import datetime

from pesapal.utils import verify_webhook_signature
from pesapal.exceptions import PesapalError

from app.repositories.payment_repository import PaymentRepository
from app.config.settings import settings

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for processing Pesapal webhooks."""
    
    def __init__(self):
        self.repository = PaymentRepository()
    
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
        # Pesapal v3 uses different field names - handle both variations
        # Try camelCase first (v3), then fallback to other formats
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
        
        # Get payment by tracking ID or order ID
        payment = None
        if order_tracking_id:
            payment = await self.repository.get_by_tracking_id(order_tracking_id)
        if not payment and order_merchant_reference:
            payment = await self.repository.get_by_order_id(order_merchant_reference)
        
        if not payment:
            logger.warning(f"Webhook received for unknown payment: tracking_id={order_tracking_id}, order_id={order_merchant_reference}")
            return False
        
        # Determine status based on notification type
        status_map = {
            "IPN_CHANGE": order_status or payment.status,
            "IPN": order_status or payment.status,
            "PAYMENT": "COMPLETED",
            "COMPLETED": "COMPLETED",
            "FAILED": "FAILED",
            "CANCELLED": "CANCELLED",
        }
        
        new_status = status_map.get(order_notification_type, order_status or payment.status)
        
        # Update payment status
        await self.repository.update_status(
            payment.order_id,
            new_status,
            payment_method,
            confirmation_code
        )
        
        logger.info(f"Payment status updated via webhook: order_id={payment.order_id}, status={new_status}")
        return True

