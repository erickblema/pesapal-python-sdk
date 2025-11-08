"""Pydantic schemas for payment API."""

from pydantic import BaseModel, Field
from typing import Optional
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
    """Schema for payment response."""
    id: str = Field(..., alias="_id", description="Payment ID")
    order_id: str = Field(..., description="Order identifier")
    amount: Decimal = Field(..., description="Payment amount")
    currency: str = Field(..., description="Currency code")
    description: str = Field(..., description="Payment description")
    status: str = Field(..., description="Payment status")
    order_tracking_id: Optional[str] = Field(None, description="Pesapal tracking ID")
    redirect_url: Optional[str] = Field(None, description="Payment redirect URL")
    payment_method: Optional[str] = Field(None, description="Payment method used")
    confirmation_code: Optional[str] = Field(None, description="Confirmation code")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class PaymentStatusResponse(BaseModel):
    """Schema for payment status check response."""
    order_id: str = Field(..., description="Order identifier")
    status: str = Field(..., description="Payment status")
    order_tracking_id: Optional[str] = Field(None, description="Pesapal tracking ID")
    payment_method: Optional[str] = Field(None, description="Payment method")
    confirmation_code: Optional[str] = Field(None, description="Confirmation code")
    updated_at: datetime = Field(..., description="Last update timestamp")

