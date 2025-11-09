"""IPN (Instant Payment Notification) management API routes."""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from pesapal import PesapalClient
from pesapal.models import IPNRegistration
from app.config.settings import settings

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/ipn", tags=["ipn"])


def get_pesapal_client() -> PesapalClient:
    """Dependency to get Pesapal client."""
    if not settings.pesapal_consumer_key or not settings.pesapal_consumer_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pesapal credentials not configured"
        )
    
    return PesapalClient(
        consumer_key=settings.pesapal_consumer_key,
        consumer_secret=settings.pesapal_consumer_secret,
        sandbox=settings.pesapal_sandbox
    )


@router.post("/register", response_model=IPNRegistration)
async def register_ipn(
    ipn_url: str,
    ipn_notification_type: str = "GET",
    client: PesapalClient = Depends(get_pesapal_client)
):
    """
    Register an IPN (Instant Payment Notification) URL with Pesapal.
    
    According to Pesapal docs:
    1. Register your IPN URL → you get a notification_id
    2. Use this notification_id when submitting orders
    
    The IPN URL must be publicly accessible (HTTPS) because PesaPal will POST/GET to it.
    
    - **ipn_url**: Your IPN callback URL (must be publicly accessible via HTTPS)
    - **ipn_notification_type**: Notification type - "GET" or "POST" (default: "GET")
    
    Returns:
        IPNRegistration with notification_id that you should save and use in payment requests
    """
    try:
        registration = await client.register_ipn(
            ipn_url=ipn_url,
            ipn_notification_type=ipn_notification_type
        )
        
        logger.info(f"IPN registered: notification_id={registration.notification_id}, url={ipn_url}")
        
        return registration
    except Exception as e:
        logger.error(f"Error registering IPN: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register IPN: {str(e)}"
        )


@router.get("/list", response_model=List[IPNRegistration])
async def list_registered_ipns(
    client: PesapalClient = Depends(get_pesapal_client)
):
    """
    Get list of registered IPN URLs.
    
    According to Pesapal docs, this endpoint returns all registered IPN URLs
    for your merchant account. Useful for verifying your IPN registrations.
    
    Returns:
        List of registered IPN URLs with their notification_ids
    """
    try:
        ipn_list = await client.get_registered_ipns()
        return ipn_list
    except Exception as e:
        logger.error(f"Error fetching IPN list: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch IPN list: {str(e)}"
        )

