"""Payment API routes."""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import List, Optional
from decimal import Decimal

from app.schema.payment import PaymentCreateRequest, PaymentResponse, PaymentStatusResponse
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_service() -> PaymentService:
    """Dependency to get payment service."""
    return PaymentService()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: PaymentCreateRequest,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Initiate a new payment.
    
    - **order_id**: Unique order identifier
    - **amount**: Payment amount (must be > 0)
    - **currency**: Currency code (KES, TZS, UGX, RWF, USD)
    - **description**: Payment description
    - **customer**: Optional customer information
    - **billing_address**: Optional billing address
    """
    try:
        # Validate currency before processing
        currency_upper = request.currency.upper()
        if currency_upper not in ["KES", "TZS", "UGX", "RWF", "USD"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency: {request.currency}. Supported: KES, TZS, UGX, RWF, USD"
            )
        
        payment = await service.initiate_payment(
            order_id=request.order_id,
            amount=request.amount,
            currency=currency_upper,
            description=request.description,
            customer=request.customer,
            billing_address=request.billing_address
        )
        
        # Check if payment was successfully initiated
        if not payment.order_tracking_id or not payment.redirect_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment initiation failed: No tracking ID or redirect URL received. Check Pesapal credentials and API status."
            )
        
        return PaymentResponse(
            _id=str(payment._id),
            order_id=payment.order_id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            status=payment.status,
            order_tracking_id=payment.order_tracking_id,
            redirect_url=payment.redirect_url,
            payment_method=payment.payment_method,
            confirmation_code=payment.confirmation_code,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate payment: {str(e)}"
        )


@router.get("/{order_id}", response_model=PaymentResponse)
async def get_payment(
    order_id: str,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Get payment details by order ID.
    
    - **order_id**: Order identifier
    """
    payment = await service.get_payment(order_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment not found: {order_id}"
        )
    
    return PaymentResponse(
        _id=str(payment._id),
        order_id=payment.order_id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        status=payment.status,
        order_tracking_id=payment.order_tracking_id,
        redirect_url=payment.redirect_url,
        payment_method=payment.payment_method,
        confirmation_code=payment.confirmation_code,
        created_at=payment.created_at,
        updated_at=payment.updated_at
    )


@router.get("/{order_id}/status", response_model=PaymentStatusResponse)
async def check_payment_status(
    order_id: str,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Check payment status from Pesapal.
    
    - **order_id**: Order identifier
    """
    try:
        payment = await service.check_payment_status(order_id)
        
        return PaymentStatusResponse(
            order_id=payment.order_id,
            status=payment.status,
            order_tracking_id=payment.order_tracking_id,
            payment_method=payment.payment_method,
            confirmation_code=payment.confirmation_code,
            updated_at=payment.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check payment status: {str(e)}"
        )


@router.get("/status/transaction", response_model=PaymentStatusResponse)
async def get_transaction_status(
    orderTrackingId: str,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Get transaction status from Pesapal using OrderTrackingId.
    
    This endpoint corresponds to Pesapal v3 GetTransactionStatus API.
    Use this after receiving a callback or IPN notification.
    
    - **orderTrackingId**: Pesapal order tracking ID (from callback/IPN)
    
    Returns payment status information from Pesapal.
    """
    try:
        # Find payment by tracking ID
        payment = await service.repository.get_by_tracking_id(orderTrackingId)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment not found for tracking ID: {orderTrackingId}"
            )
        
        # Get fresh status from Pesapal
        updated_payment = await service.check_payment_status(payment.order_id)
        
        return PaymentStatusResponse(
            order_id=updated_payment.order_id,
            status=updated_payment.status,
            order_tracking_id=updated_payment.order_tracking_id,
            payment_method=updated_payment.payment_method,
            confirmation_code=updated_payment.confirmation_code,
            updated_at=updated_payment.updated_at
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transaction status: {str(e)}"
        )


@router.get("/callback")
async def payment_callback(
    request: Request,
    OrderTrackingId: Optional[str] = None,
    OrderNotificationType: Optional[str] = None,
    OrderMerchantReference: Optional[str] = None,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Handle payment callback from Pesapal.
    
    Pesapal redirects customers to this URL after payment with query parameters:
    - **OrderTrackingId**: Pesapal order tracking ID
    - **OrderNotificationType**: Always "CALLBACKURL" for callbacks
    - **OrderMerchantReference**: Your order ID
    
    This endpoint automatically fetches the payment status from Pesapal.
    """
    try:
        # Get query parameters (Pesapal sends them in camelCase)
        order_tracking_id = OrderTrackingId or request.query_params.get("OrderTrackingId")
        order_notification_type = OrderNotificationType or request.query_params.get("OrderNotificationType")
        order_merchant_reference = OrderMerchantReference or request.query_params.get("OrderMerchantReference")
        
        logger.info(
            f"Payment callback received: tracking_id={order_tracking_id}, "
            f"type={order_notification_type}, reference={order_merchant_reference}"
        )
        
        if not order_tracking_id and not order_merchant_reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameters: OrderTrackingId or OrderMerchantReference"
            )
        
        # Find payment by tracking ID or order ID
        payment = None
        if order_tracking_id:
            payment = await service.repository.get_by_tracking_id(order_tracking_id)
        if not payment and order_merchant_reference:
            payment = await service.repository.get_by_order_id(order_merchant_reference)
        
        if not payment:
            logger.warning(f"Callback received for unknown payment: tracking_id={order_tracking_id}, order_id={order_merchant_reference}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment not found for tracking ID: {order_tracking_id or order_merchant_reference}"
            )
        
        # Automatically fetch fresh status from Pesapal (as per Pesapal docs)
        try:
            updated_payment = await service.check_payment_status(payment.order_id)
            logger.info(f"Payment status updated via callback: order_id={payment.order_id}, status={updated_payment.status}")
        except Exception as e:
            logger.error(f"Error fetching payment status from Pesapal: {e}")
            # Continue with existing payment data if status check fails
        
        # Return payment status information
        # In a real app, you'd redirect to a success/failure page
        return {
            "message": "Payment callback received",
            "order_id": payment.order_id,
            "order_tracking_id": payment.order_tracking_id,
            "status": payment.status,
            "redirect_url": payment.redirect_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing callback: {str(e)}"
        )


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    service: PaymentService = Depends(get_payment_service)
):
    """
    List payments with optional filtering.
    
    - **skip**: Number of items to skip
    - **limit**: Maximum number of items to return
    - **status_filter**: Optional status filter (PENDING, COMPLETED, FAILED)
    """
    payments = await service.list_payments(skip, limit, status_filter)
    
    return [
        PaymentResponse(
            _id=str(p._id),
            order_id=p.order_id,
            amount=p.amount,
            currency=p.currency,
            description=p.description,
            status=p.status,
            order_tracking_id=p.order_tracking_id,
            redirect_url=p.redirect_url,
            payment_method=p.payment_method,
            confirmation_code=p.confirmation_code,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in payments
    ]

