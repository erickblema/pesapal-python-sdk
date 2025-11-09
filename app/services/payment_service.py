"""Payment service layer."""

import logging
from typing import Optional
from decimal import Decimal
from datetime import datetime

from pesapal import PesapalClient
from pesapal.models import PaymentRequest, PaymentResponse, PaymentStatus
from pesapal.exceptions import PesapalError

from app.repositories.payment_repository import PaymentRepository
from app.models.payment import Payment
from app.config.settings import settings

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment operations."""
    
    def __init__(self):
        self.repository = PaymentRepository()
        self._client: Optional[PesapalClient] = None
    
    def _get_client(self) -> PesapalClient:
        """Get or create Pesapal client."""
        if not self._client:
            if not settings.pesapal_consumer_key or not settings.pesapal_consumer_secret:
                raise ValueError(
                    "Pesapal credentials not configured. "
                    "Set PESAPAL_CONSUMER_KEY and PESAPAL_CONSUMER_SECRET in environment variables."
                )
            
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
        existing = await self.repository.get_by_order_id(order_id)
        if existing:
            if existing.status == "COMPLETED":
                raise ValueError("Payment already completed")
            return existing
        
        payment = Payment(
            order_id=order_id,
            amount=amount,
            currency=currency,
            description=description,
            customer=customer,
            billing_address=billing_address
        )
        
        payment.add_event(
            event_type="CREATED",
            status="PENDING",
            source="CREATION",
            metadata={
                "order_id": order_id,
                "amount": str(amount),
                "currency": currency,
                "description": description
            }
        )
        
        payment = await self.repository.create(payment)
        
        try:
            client = self._get_client()
            callback_url = settings.pesapal_callback_url
            if not callback_url:
                callback_url = "https://payment-helper.onrender.com/payments/callback"
            
            notification_id = settings.pesapal_ipn_id
            if not notification_id:
                raise ValueError(
                    "PESAPAL_IPN_ID is required. "
                    "Set it in your .env file. "
                    "You can register an IPN URL in Pesapal dashboard to get an IPN ID."
                )
            
            payment_request = PaymentRequest(
                id=order_id,
                amount=amount,
                currency=currency,
                description=description,
                callback_url=callback_url,
                notification_id=notification_id,
                redirect_mode=None,
                cancellation_url=None,
                branch=None,
                customer=customer,
                billing_address=billing_address
            )
            
            response: PaymentResponse = await client.submit_order(payment_request)
            
            if not response.order_tracking_id and not response.redirect_url:
                raise PesapalError(
                    f"Pesapal API returned invalid response: {response.model_dump()}. "
                    f"Missing order_tracking_id and redirect_url."
                )
            
            old_status = payment.status
            payment.order_tracking_id = response.order_tracking_id
            payment.redirect_url = response.redirect_url
            payment.status = response.status or "200"
            payment.provider_response = response.model_dump()
            
            payment.add_status_change(
                old_status=old_status,
                new_status=payment.status,
                source="CREATION",
                reason="Submitted to Pesapal",
                metadata={
                    "order_tracking_id": payment.order_tracking_id,
                    "redirect_url": payment.redirect_url,
                    "pesapal_status": response.status
                }
            )
            
            payment.add_event(
                event_type="SUBMITTED_TO_PESAPAL",
                status=payment.status,
                source="CREATION",
                metadata={
                    "order_tracking_id": payment.order_tracking_id,
                    "redirect_url": payment.redirect_url,
                    "pesapal_status": response.status
                }
            )
            
            logger.info(f"Payment initiated successfully: order_id={order_id}, tracking_id={payment.order_tracking_id}")
            
            payment.payment_state = payment.get_payment_state()
            
            await self.repository.collection.update_one(
                {"_id": payment._id},
                {
                    "$set": {
                        "order_tracking_id": payment.order_tracking_id,
                        "redirect_url": payment.redirect_url,
                        "status": payment.status,
                        "payment_state": payment.payment_state,
                        "provider_response": payment.provider_response,
                        "status_history": payment.status_history,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {"events": payment.events[-1].to_dict()}
                }
            )
            
            return payment
            
        except PesapalError as e:
            logger.error(f"Pesapal API error for order {order_id}: {str(e)}")
            await self.repository.collection.update_one(
                {"_id": payment._id},
                {"$set": {"status": "FAILED", "updated_at": datetime.utcnow()}}
            )
            raise ValueError(f"Failed to initiate payment with Pesapal: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error initiating payment for order {order_id}: {str(e)}", exc_info=True)
            await self.repository.collection.update_one(
                {"_id": payment._id},
                {"$set": {"status": "FAILED", "updated_at": datetime.utcnow()}}
            )
            raise ValueError(f"Failed to initiate payment: {str(e)}")
    
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
            
            old_status = payment.status
            
            if status.status_code is not None:
                status_code_map = {
                    0: "INVALID",
                    1: "200",
                    2: "FAILED",
                    3: "REVERSED"
                }
                new_status = status_code_map.get(status.status_code, payment.status)
            elif status.payment_status_description:
                desc = status.payment_status_description.upper()
                if desc == "COMPLETED":
                    new_status = "200"
                elif desc == "FAILED":
                    new_status = "FAILED"
                elif desc == "INVALID":
                    new_status = "INVALID"
                elif desc == "REVERSED":
                    new_status = "REVERSED"
                else:
                    new_status = payment.status
            else:
                new_status = payment.status
            
            if status.payment_method:
                payment.payment_method = status.payment_method
            if status.confirmation_code:
                payment.confirmation_code = status.confirmation_code
            payment.last_status_check = datetime.utcnow()
            payment.provider_response.update(status.model_dump())
            
            logger.info(
                f"Payment status from Pesapal: "
                f"status_code={status.status_code}, "
                f"payment_status_description={status.payment_status_description}, "
                f"payment_method={status.payment_method}, "
                f"confirmation_code={status.confirmation_code}, "
                f"mapped_status={new_status}"
            )
            
            if old_status != new_status:
                payment.add_status_change(
                    old_status=old_status,
                    new_status=new_status,
                    source="MANUAL_CHECK",
                    reason=status.payment_status_description or "Status checked from Pesapal",
                    metadata={
                        "payment_method": status.payment_method,
                        "confirmation_code": status.confirmation_code,
                        "pesapal_status_description": status.payment_status_description,
                        "message": status.message
                    }
                )
            
            event_metadata = {
                "old_status": old_status,
                "new_status": new_status,
                "payment_method": status.payment_method,
                "confirmation_code": status.confirmation_code,
                "pesapal_status_description": status.payment_status_description,
                "message": status.message
            }
            
            event = {
                "event_type": "STATUS_CHECKED",
                "status": new_status,
                "source": "MANUAL_CHECK",
                "metadata": event_metadata,
                "timestamp": datetime.utcnow()
            }
            
            updated = await self.repository.update_status(
                order_id,
                new_status,
                status.payment_method,
                status.confirmation_code,
                event=event
            )
            
            payment.payment_state = payment.get_payment_state()
            
            update_fields = {
                "last_status_check": payment.last_status_check,
                "provider_response": payment.provider_response,
                "status_history": payment.status_history,
                "status": new_status,
                "payment_state": payment.payment_state
            }
            
            if status.payment_method is not None:
                update_fields["payment_method"] = status.payment_method
            if status.confirmation_code is not None:
                update_fields["confirmation_code"] = status.confirmation_code
            
            result = await self.repository.collection.update_one(
                {"order_id": order_id},
                {"$set": update_fields}
            )
            
            logger.info(f"Database update result: modified={result.modified_count}, matched={result.matched_count}")
            
            if result.modified_count == 0:
                logger.warning(f"No documents were updated for order_id={order_id}. Payment may not exist in database.")
            
            logger.info(f"Payment status checked: order_id={order_id}, status={old_status} -> {new_status}")
            
            final_payment = await self.repository.get_by_order_id(order_id)
            if final_payment:
                return final_payment
            return updated or payment
            
        except PesapalError as e:
            logger.error(f"Failed to check payment status for order {order_id}: {str(e)}", exc_info=True)
            return payment
        except Exception as e:
            logger.error(f"Unexpected error checking payment status for order {order_id}: {str(e)}", exc_info=True)
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
        payment_state = None
        if status:
            status_upper = status.upper()
            if status_upper in ["PENDING", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED"]:
                payment_state = status_upper
                status = None
        
        return await self.repository.list_payments(skip, limit, status, payment_state)

