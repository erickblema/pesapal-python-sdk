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
        Process webhook notification from Pesapal.
        
        Args:
            webhook_data: Webhook payload from Pesapal
            
        Returns:
            True if processed successfully
        """
        order_tracking_id = webhook_data.get("OrderTrackingId")
        order_merchant_reference = webhook_data.get("OrderMerchantReference")
        order_notification_type = webhook_data.get("OrderNotificationType")
        
        if not order_tracking_id or not order_merchant_reference:
            raise ValueError("Invalid webhook data: missing required fields")
        
        # Get payment by tracking ID or order ID
        payment = await self.repository.get_by_tracking_id(order_tracking_id)
        if not payment:
            payment = await self.repository.get_by_order_id(order_merchant_reference)
        
        if not payment:
            logger.warning(f"Webhook received for unknown payment: tracking_id={order_tracking_id}, order_id={order_merchant_reference}")
            return False
        
        # Determine status based on notification type
        status_map = {
            "IPN_CHANGE": webhook_data.get("OrderStatus", payment.status),
            "PAYMENT": "COMPLETED",
            "FAILED": "FAILED",
        }
        
        new_status = status_map.get(order_notification_type, webhook_data.get("OrderStatus", payment.status))
        
        # Update payment status
        await self.repository.update_status(
            payment.order_id,
            new_status,
            webhook_data.get("PaymentMethod"),
            webhook_data.get("ConfirmationCode")
        )
        
        logger.info(f"Payment status updated via webhook: order_id={payment.order_id}, status={new_status}")
        return True

