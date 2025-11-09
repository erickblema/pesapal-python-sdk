"""Pydantic models for Pesapal API requests and responses."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal

from pesapal.constants import SUPPORTED_CURRENCIES, SUPPORTED_PAYMENT_METHODS


class PaymentRequest(BaseModel):
    """Model for initiating a payment request."""
    
    id: str = Field(..., description="Unique order ID (merchant reference), max 50 characters")
    currency: str = Field(..., description="Currency code (KES, TZS, UGX, RWF, USD)")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    description: str = Field(..., max_length=100, description="Order description, max 100 characters")
    callback_url: str = Field(..., description="Callback URL for payment status")
    redirect_mode: Optional[str] = Field(None, description="Redirect mode: TOP_WINDOW or PARENT_WINDOW (default: TOP_WINDOW)")
    cancellation_url: Optional[str] = Field(None, description="URL to redirect if customer cancels payment")
    notification_id: Optional[str] = Field(None, description="IPN notification ID (required for API 3.0)")
    branch: Optional[str] = Field(None, description="Store/branch name for this payment")
    billing_address: Optional[dict] = Field(None, description="Billing address information (required by Pesapal)")
    customer: Optional[dict] = Field(None, description="Customer information")
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        currency = v.upper()
        if currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {v}. Supported: {SUPPORTED_CURRENCIES}")
        return currency
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class PaymentResponse(BaseModel):
    """Model for payment initiation response."""
    
    order_tracking_id: Optional[str] = Field(None, description="Pesapal order tracking ID")
    merchant_reference: Optional[str] = Field(None, description="Merchant reference (order ID)")
    redirect_url: Optional[str] = Field(None, description="URL to redirect customer for payment")
    status: Optional[str] = Field(None, description="Payment status")
    error: Optional[int] = Field(None, description="Error code (null if successful)")
    message: Optional[str] = Field(None, description="Response message")
    
    # Allow extra fields from Pesapal API
    class Config:
        extra = "allow"


class PaymentStatus(BaseModel):
    """Model for payment status response from GetTransactionStatus API.
    
    According to Pesapal docs:
    - status_code: 0=INVALID, 1=COMPLETED, 2=FAILED, 3=REVERSED
    - payment_status_description: "INVALID", "FAILED", "COMPLETED", or "REVERSED"
    """
    
    payment_method: Optional[str] = Field(None, description="Payment method used (Visa, MPESA, MTN, etc.)")
    amount: Optional[Decimal] = Field(None, description="Amount paid by customer")
    created_date: Optional[datetime] = Field(None, description="Date the payment was made")
    confirmation_code: Optional[str] = Field(None, description="Confirmation code from payment provider")
    payment_status_description: Optional[str] = Field(None, description="Status: INVALID, FAILED, COMPLETED, or REVERSED")
    description: Optional[str] = Field(None, description="Description of payment status")
    message: Optional[str] = Field(None, description="Message showing if transaction was processed successfully")
    payment_account: Optional[str] = Field(None, description="Masked card number or phone number used")
    call_back_url: Optional[str] = Field(None, description="Callback URL")
    status_code: Optional[int] = Field(None, description="Pesapal status code: 0=INVALID, 1=COMPLETED, 2=FAILED, 3=REVERSED")
    merchant_reference: Optional[str] = Field(None, description="Merchant reference (order_id)")
    currency: Optional[str] = Field(None, description="Currency code (ISO)")
    order_tracking_id: Optional[str] = Field(None, description="Order tracking ID")
    error: Optional[dict] = Field(None, description="Error object with error_type, code, message, call_back_url")
    status: Optional[str] = Field(None, description="HTTP status code (200 = successful request)")


class IPNRegistration(BaseModel):
    """Model for IPN (Instant Payment Notification) registration."""
    
    notification_id: str = Field(..., description="IPN notification ID")
    ipn_notification_type: str = Field("GET", description="Notification type (GET or POST)")
    ipn_url: str = Field(..., description="IPN callback URL")

