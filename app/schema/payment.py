"""Pydantic schemas for payment API."""

from pydantic import BaseModel, Field, model_serializer
from typing import Optional, Any, List, Dict
from datetime import datetime
from decimal import Decimal


class PaymentCreateRequest(BaseModel):
    """Schema for creating a payment."""
    order_id: str = Field(..., description="Unique order identifier")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: str = Field(..., description="Currency code (KES, TZS, UGX, RWF, USD)")
    description: str = Field(..., max_length=100, description="Payment description")
    customer: Optional[dict] = Field(None, description="Customer information")
    billing_address: Optional[dict] = Field(None, description="Billing address")


class PaymentResponse(BaseModel):
    """Schema for payment response - uses Pesapal v3 camelCase format."""
    id: str = Field(..., alias="_id", description="Payment ID")
    order_id: str = Field(..., description="Order identifier")
    amount: Decimal = Field(..., description="Payment amount")  # Keep as Decimal internally
    currency: str = Field(..., description="Currency code")
    description: str = Field(..., description="Payment description")
    status: str = Field(..., description="Payment status code from Pesapal (e.g., '200', 'PENDING')")
    payment_state: str = Field(..., description="Clear payment state: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED")
    order_tracking_id: Optional[str] = Field(None, description="Pesapal tracking ID")
    redirect_url: Optional[str] = Field(None, description="Payment redirect URL")
    payment_method: Optional[str] = Field(None, description="Payment method used")
    confirmation_code: Optional[str] = Field(None, description="Confirmation code")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @model_serializer
    def serialize_model(self) -> dict:
        """Serialize model with OrderTrackingId in camelCase and amount as string."""
        # Determine payment state from status
        status_code = str(self.status).upper()
        if status_code == "200":
            payment_state = "COMPLETED"
        elif status_code in ["PENDING", "PROCESSING"]:
            payment_state = "PROCESSING"
        elif status_code in ["FAILED", "ERROR", "0"]:
            payment_state = "FAILED"
        elif status_code == "CANCELLED":
            payment_state = "CANCELLED"
        else:
            payment_state = "PENDING"
        
        data = {
            "_id": self.id,  # Use self.id (which is aliased from _id)
            "order_id": self.order_id,
            "amount": str(self.amount),  # Convert Decimal to string as per Pesapal format
            "currency": self.currency,
            "description": self.description,
            "status": self.status,
            "payment_state": payment_state,  # Clear state indicator
            "OrderTrackingId": self.order_tracking_id,  # Use camelCase for Pesapal v3
            "redirect_url": self.redirect_url,
            "payment_method": self.payment_method,
            "confirmation_code": self.confirmation_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        # Keep all fields, including None values for optional fields
        return data
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaymentEventResponse(BaseModel):
    """Schema for payment event in history."""
    event_type: str = Field(..., description="Event type (CREATED, STATUS_CHANGED, CALLBACK_RECEIVED, etc.)")
    status: str = Field(..., description="Status at time of event")
    source: str = Field(..., description="Event source (CREATION, CALLBACK, WEBHOOK, MANUAL_CHECK)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")
    timestamp: datetime = Field(..., description="Event timestamp")


class PaymentStatusResponse(BaseModel):
    """Schema for payment status check response."""
    order_id: str = Field(..., description="Order identifier")
    status: str = Field(..., description="Payment status")
    order_tracking_id: Optional[str] = Field(None, description="Pesapal tracking ID")
    payment_method: Optional[str] = Field(None, description="Payment method")
    confirmation_code: Optional[str] = Field(None, description="Confirmation code")
    updated_at: datetime = Field(..., description="Last update timestamp")
    events: Optional[List[PaymentEventResponse]] = Field(None, description="Payment event history")

