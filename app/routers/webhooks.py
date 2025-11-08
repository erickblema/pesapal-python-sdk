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
async def pesapal_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    service: WebhookService = Depends(get_webhook_service)
):
    """
    Receive webhook notifications from Pesapal.
    
    This endpoint receives IPN (Instant Payment Notification) callbacks from Pesapal
    when payment status changes.
    """
    try:
        # Get webhook data (can be form data or JSON)
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            webhook_data = await request.json()
        else:
            # Form data
            form = await request.form()
            webhook_data = dict(form)
        
        # Get signature from headers
        signature = request.headers.get("X-Pesapal-Signature") or request.headers.get("pesapal-signature")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing webhook signature"
            )
        
        # Verify signature
        if not service.verify_signature(webhook_data, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Process webhook in background
        background_tasks.add_task(process_webhook_background, webhook_data, service)
        logger.info("Webhook received and queued for processing")
        
        return {
            "status": "received",
            "message": "Webhook received and queued for processing"
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
    Receive webhook notifications from Pesapal (GET method).
    
    Pesapal may send webhooks via GET request with query parameters.
    """
    try:
        # Get webhook data from query parameters
        webhook_data = dict(request.query_params)
        
        # Get signature from headers or query params
        signature = (
            request.headers.get("X-Pesapal-Signature") or
            request.headers.get("pesapal-signature") or
            webhook_data.get("signature")
        )
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing webhook signature"
            )
        
        # Remove signature from data for verification
        if "signature" in webhook_data:
            del webhook_data["signature"]
        
        # Verify signature
        if not service.verify_signature(webhook_data, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Process webhook in background
        background_tasks.add_task(process_webhook_background, webhook_data, service)
        logger.info("Webhook received and queued for processing (GET)")
        
        return {
            "status": "received",
            "message": "Webhook received and queued for processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook (GET): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

