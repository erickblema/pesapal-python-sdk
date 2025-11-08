"""Payment service layer."""

from typing import Optional
from decimal import Decimal

from pesapal import PesapalClient
from pesapal.models import PaymentRequest, PaymentResponse, PaymentStatus
from pesapal.exceptions import PesapalError

from app.repositories.payment_repository import PaymentRepository
from app.models.payment import Payment
from app.config.settings import settings


class PaymentService:
    """Service for payment operations."""
    
    def __init__(self):
        self.repository = PaymentRepository()
        self._client: Optional[PesapalClient] = None
    
    def _get_client(self) -> PesapalClient:
        """Get or create Pesapal client."""
        if not self._client:
            if not settings.pesapal_consumer_key or not settings.pesapal_consumer_secret:
                raise ValueError("Pesapal credentials not configured")
            
            self._client = PesapalClient(
                consumer_key=settings.pesapal_consumer_key,
                consumer_secret=settings.pesapal_consumer_secret,
                sandbox=settings.pesapal_sandbox
            )
        return self._client
    
    async def initiate_payment(
        self,
        order_id: str,
        amount: Decimal,
        currency: str,
        description: str,
        customer: Optional[dict] = None,
        billing_address: Optional[dict] = None
    ) -> Payment:
        """
        Initiate a payment.
        
        Args:
            order_id: Unique order identifier
            amount: Payment amount
            currency: Currency code
            description: Payment description
            customer: Optional customer information
            billing_address: Optional billing address
            
        Returns:
            Payment object with redirect URL
        """
        # Check if payment already exists
        existing = await self.repository.get_by_order_id(order_id)
        if existing:
            if existing.status == "COMPLETED":
                raise ValueError("Payment already completed")
            return existing
        
        # Create payment record
        payment = Payment(
            order_id=order_id,
            amount=amount,
            currency=currency,
            description=description,
            customer=customer,
            billing_address=billing_address
        )
        
        # Save to database
        payment = await self.repository.create(payment)
        
        # Initiate payment with Pesapal
        try:
            client = self._get_client()
            # Use configured callback URL or default
            callback_url = settings.pesapal_callback_url
            if not callback_url:
                # Default callback URL (should be set in production)
                callback_url = "https://payment-helper.onrender.com/payments/callback"
            
            payment_request = PaymentRequest(
                id=order_id,
                amount=amount,
                currency=currency,
                description=description,
                callback_url=callback_url,
                customer=customer,
                billing_address=billing_address
            )
            
            response: PaymentResponse = await client.submit_order(payment_request)
            
            # Update payment with tracking ID and redirect URL
            payment.order_tracking_id = response.order_tracking_id
            payment.redirect_url = response.redirect_url
            payment.status = response.status or "PENDING"
            
            # Update in database
            from datetime import datetime
            await self.repository.collection.update_one(
                {"_id": payment._id},
                {"$set": {
                    "order_tracking_id": payment.order_tracking_id,
                    "redirect_url": payment.redirect_url,
                    "status": payment.status,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return payment
            
        except PesapalError as e:
            # Update payment status to failed
            from datetime import datetime
            await self.repository.collection.update_one(
                {"_id": payment._id},
                {"$set": {"status": "FAILED", "updated_at": datetime.utcnow()}}
            )
            raise
    
    async def check_payment_status(self, order_id: str) -> Payment:
        """
        Check payment status from Pesapal.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Updated Payment object
        """
        payment = await self.repository.get_by_order_id(order_id)
        if not payment:
            raise ValueError(f"Payment not found: {order_id}")
        
        if not payment.order_tracking_id:
            raise ValueError("Payment not yet submitted to Pesapal")
        
        try:
            client = self._get_client()
            status: PaymentStatus = await client.get_payment_status(
                payment.order_tracking_id,
                order_id
            )
            
            # Update payment status
            new_status = status.status_code or payment.status
            updated = await self.repository.update_status(
                order_id,
                new_status,
                status.payment_method,
                status.confirmation_code
            )
            
            return updated or payment
            
        except PesapalError as e:
            # Return current payment status if check fails
            return payment
    
    async def get_payment(self, order_id: str) -> Optional[Payment]:
        """Get payment by order ID."""
        return await self.repository.get_by_order_id(order_id)
    
    async def list_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> list[Payment]:
        """List payments."""
        return await self.repository.list_payments(skip, limit, status)

