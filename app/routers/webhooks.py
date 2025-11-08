"""Webhook API routes."""

import logging
from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks, Depends
from typing import Dict, Any

from app.services.webhook_service import WebhookService
from app.config.settings import settings

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def get_webhook_service() -> WebhookService:
    """Dependency to get webhook service."""
    return WebhookService()


async def process_webhook_background(webhook_data: Dict[str, Any], service: WebhookService):
    """Background task to process webhook."""
    try:
        await service.process_webhook(webhook_data)
        logger.info("Webhook processed successfully")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)


@router.post("/pesapal")
async def pesapal_webhook_post(
    request: Request,
    background_tasks: BackgroundTasks,
    service: WebhookService = Depends(get_webhook_service)
):
    """
    Receive IPN webhook notifications from Pesapal (POST method).
    
    This endpoint receives IPN (Instant Payment Notification) callbacks from Pesapal
    when payment status changes.
    
    Pesapal v3 sends webhooks as JSON data:
    {
        "OrderNotificationType": "IPNCHANGE",
        "OrderTrackingId": "b945e4af-80a5-4ec1-8706-e03f8332fb04",
        "OrderMerchantReference": "your-order-id"
    }
    
    Note: IPN does NOT contain payment status. You must call GetTransactionStatus API.
    """
    try:
        # Log all headers for debugging
        logger.info(f"Webhook headers: {dict(request.headers)}")
        
        # Get webhook data - Pesapal v3 sends JSON
        content_type = request.headers.get("content-type", "").lower()
        
        # Read raw body first - IMPORTANT: body can only be read once
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8') if body_bytes else ''
        logger.info(f"Webhook raw body: {body_str}")
        logger.info(f"Content-Type: {content_type}")
        
        webhook_data = {}
        
        # Prioritize JSON parsing (Pesapal v3 standard)
        if "application/json" in content_type or not content_type:
            try:
                import json
                webhook_data = json.loads(body_str) if body_str else {}
            except Exception as e:
                logger.error(f"Error parsing JSON: {e}")
                # Try to parse as form data as fallback
                if body_str:
                    try:
                        from urllib.parse import parse_qs
                        parsed = parse_qs(body_str, keep_blank_values=True)
                        webhook_data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                    except Exception:
                        webhook_data = {}
        elif "application/x-www-form-urlencoded" in content_type:
            # Form data fallback
            try:
                from urllib.parse import parse_qs
                parsed = parse_qs(body_str, keep_blank_values=True)
                webhook_data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            except Exception as e:
                logger.error(f"Error parsing form data: {e}")
                webhook_data = {}
        else:
            # Try JSON first, then form data
            try:
                import json
                webhook_data = json.loads(body_str) if body_str else {}
            except Exception:
                try:
                    from urllib.parse import parse_qs
                    if body_str:
                        parsed = parse_qs(body_str, keep_blank_values=True)
                        webhook_data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                except Exception as e:
                    logger.error(f"Error parsing webhook data: {e}")
                    webhook_data = {}
        
        logger.info(f"Webhook data received: {webhook_data}")
        
        # Check if webhook data is empty
        # Instead of throwing error, return IPN response with status 500 (as per Pesapal spec)
        if not webhook_data:
            logger.warning(f"Empty webhook data received. Body: {body_str}, Content-Type: {content_type}")
            # Return IPN response format even for empty data (status 500 indicates issue)
            return {
                "orderNotificationType": "",
                "orderTrackingId": "",
                "orderMerchantReference": "",
                "status": 500
            }
        
        # Get signature from headers - check multiple possible header names
        # Pesapal v3 may use different header names
        signature = (
            request.headers.get("X-Pesapal-Signature") or
            request.headers.get("x-pesapal-signature") or
            request.headers.get("Pesapal-Signature") or
            request.headers.get("pesapal-signature") or
            request.headers.get("X-Pesapal-Authorization") or
            request.headers.get("Authorization") or
            webhook_data.get("signature") or
            webhook_data.get("Signature")
        )
        
        # Remove signature from data if it was in the payload
        if "signature" in webhook_data:
            del webhook_data["signature"]
        if "Signature" in webhook_data:
            del webhook_data["Signature"]
        
        # Verify signature if present
        if signature:
            if not service.verify_signature(webhook_data, signature):
                logger.warning("Invalid webhook signature")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature"
                )
        else:
            # Log warning but don't fail - some Pesapal configurations may not send signature
            logger.warning("Webhook received without signature - processing anyway")
            # In production, you might want to make this stricter
            # For now, we'll process without signature verification
        
        # Extract required fields for IPN response
        order_tracking_id = (
            webhook_data.get("OrderTrackingId") or
            webhook_data.get("order_tracking_id") or
            webhook_data.get("orderTrackingId") or
            webhook_data.get("OrderTrackingID") or
            webhook_data.get("OrderTrackingId") or
            None
        )
        
        order_merchant_reference = (
            webhook_data.get("OrderMerchantReference") or
            webhook_data.get("order_merchant_reference") or
            webhook_data.get("orderMerchantReference") or
            webhook_data.get("OrderMerchantRef") or
            webhook_data.get("merchant_reference") or
            webhook_data.get("OrderReference") or
            None
        )
        
        # Extract order notification type from webhook data - use only what Pesapal sends
        order_notification_type = (
            webhook_data.get("OrderNotificationType") or
            webhook_data.get("order_notification_type") or
            webhook_data.get("orderNotificationType") or
            None
        )
        
        # Normalize the notification type if present (no default/mock data)
        if order_notification_type:
            order_notification_type = order_notification_type.upper().replace("_", "")
        else:
            # Return empty string if not provided by Pesapal (no mock data)
            order_notification_type = ""
            logger.warning("OrderNotificationType not found in webhook data from Pesapal")
        
        # Process webhook only if we have required data
        ipn_status = 500
        if order_tracking_id or order_merchant_reference:
            try:
                # IPN does NOT contain payment status - must call GetTransactionStatus
                # Process webhook (which will call GetTransactionStatus internally)
                success = await service.process_webhook(webhook_data)
                ipn_status = 200 if success else 500
                logger.info(f"Webhook processed successfully. Status: {ipn_status}")
            except Exception as e:
                logger.error(f"Error processing webhook synchronously: {e}")
                # Queue for background processing
                background_tasks.add_task(process_webhook_background, webhook_data, service)
                ipn_status = 500  # Received but processing issue
        else:
            logger.warning("Webhook received but missing required fields (OrderTrackingId or OrderMerchantReference)")
            # Still return 500 status but don't try to process
        
        # Return IPN response in Pesapal v3 format
        # Format: {"orderNotificationType":"IPNCHANGE","orderTrackingId":"...","orderMerchantReference":"...","status":200}
        # Use the actual value from Pesapal, not hardcoded
        return {
            "orderNotificationType": order_notification_type,
            "orderTrackingId": order_tracking_id or "",
            "orderMerchantReference": order_merchant_reference or "",
            "status": ipn_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


@router.get("/pesapal")
async def pesapal_webhook_get(
    request: Request,
    background_tasks: BackgroundTasks,
    service: WebhookService = Depends(get_webhook_service)
):
    """
    Receive IPN webhook notifications from Pesapal (GET method).
    
    Pesapal may send IPN via GET request with query parameters:
    - OrderTrackingId
    - OrderNotificationType (IPNCHANGE)
    - OrderMerchantReference
    
    Note: IPN does NOT contain payment status. You must call GetTransactionStatus API.
    """
    try:
        # Log all headers for debugging
        logger.info(f"Webhook GET headers: {dict(request.headers)}")
        
        # Get webhook data from query parameters
        webhook_data = dict(request.query_params)
        
        # Convert MultiDict values to single values if needed
        webhook_data = {k: v if isinstance(v, str) else v[0] if len(v) > 0 else "" for k, v in webhook_data.items()}
        
        logger.info(f"Webhook GET data received: {webhook_data}")
        
        # Get signature from headers or query params - check multiple variations
        signature = (
            request.headers.get("X-Pesapal-Signature") or
            request.headers.get("x-pesapal-signature") or
            request.headers.get("Pesapal-Signature") or
            request.headers.get("pesapal-signature") or
            request.headers.get("X-Pesapal-Authorization") or
            request.headers.get("Authorization") or
            webhook_data.get("signature") or
            webhook_data.get("Signature")
        )
        
        # Remove signature from data for verification
        if "signature" in webhook_data:
            del webhook_data["signature"]
        if "Signature" in webhook_data:
            del webhook_data["Signature"]
        
        # Verify signature if present
        if signature:
            if not service.verify_signature(webhook_data, signature):
                logger.warning("Invalid webhook signature (GET)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature"
                )
        else:
            # Log warning but don't fail
            logger.warning("Webhook GET received without signature - processing anyway")
        
        # Extract required fields for IPN response
        order_tracking_id = (
            webhook_data.get("OrderTrackingId") or
            webhook_data.get("order_tracking_id") or
            webhook_data.get("orderTrackingId") or
            webhook_data.get("OrderTrackingID") or
            None
        )
        
        order_merchant_reference = (
            webhook_data.get("OrderMerchantReference") or
            webhook_data.get("order_merchant_reference") or
            webhook_data.get("orderMerchantReference") or
            webhook_data.get("OrderMerchantRef") or
            webhook_data.get("merchant_reference") or
            webhook_data.get("OrderReference") or
            None
        )
        
        # Extract order notification type from webhook data - use only what Pesapal sends
        order_notification_type = (
            webhook_data.get("OrderNotificationType") or
            webhook_data.get("order_notification_type") or
            webhook_data.get("orderNotificationType") or
            None
        )
        
        # Normalize the notification type if present (no default/mock data)
        if order_notification_type:
            order_notification_type = order_notification_type.upper().replace("_", "")
        else:
            # Return empty string if not provided by Pesapal (no mock data)
            order_notification_type = ""
            logger.warning("OrderNotificationType not found in webhook data (GET) from Pesapal")
        
        # Process webhook only if we have required data
        ipn_status = 500
        if order_tracking_id or order_merchant_reference:
            try:
                # IPN does NOT contain payment status - must call GetTransactionStatus
                # Process webhook (which will call GetTransactionStatus internally)
                success = await service.process_webhook(webhook_data)
                ipn_status = 200 if success else 500
                logger.info(f"Webhook GET processed successfully. Status: {ipn_status}")
            except Exception as e:
                logger.error(f"Error processing webhook synchronously (GET): {e}")
                # Queue for background processing
                background_tasks.add_task(process_webhook_background, webhook_data, service)
                ipn_status = 500  # Received but processing issue
        else:
            logger.warning("Webhook GET received but missing required fields (OrderTrackingId or OrderMerchantReference)")
            # Still return 500 status but don't try to process
        
        # Return IPN response in Pesapal v3 format
        # Format: {"orderNotificationType":"IPNCHANGE","orderTrackingId":"...","orderMerchantReference":"...","status":200}
        # Use the actual value from Pesapal, not hardcoded
        return {
            "orderNotificationType": order_notification_type,
            "orderTrackingId": order_tracking_id or "",
            "orderMerchantReference": order_merchant_reference or "",
            "status": ipn_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook (GET): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


