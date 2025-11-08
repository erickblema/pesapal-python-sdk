"""Payment models for MongoDB."""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from bson import ObjectId


class Payment:
    """Payment document model."""
    
    def __init__(
        self,
        order_id: str,
        amount: Decimal,
        currency: str,
        description: str,
        status: str = "PENDING",
        order_tracking_id: Optional[str] = None,
        redirect_url: Optional[str] = None,
        payment_method: Optional[str] = None,
        confirmation_code: Optional[str] = None,
        customer: Optional[dict] = None,
        billing_address: Optional[dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id
        self.order_id = order_id
        self.amount = amount
        self.currency = currency
        self.description = description
        self.status = status
        self.order_tracking_id = order_tracking_id
        self.redirect_url = redirect_url
        self.payment_method = payment_method
        self.confirmation_code = confirmation_code
        self.customer = customer or {}
        self.billing_address = billing_address or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB."""
        data = {
            "order_id": self.order_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "description": self.description,
            "status": self.status,
            "order_tracking_id": self.order_tracking_id,
            "redirect_url": self.redirect_url,
            "payment_method": self.payment_method,
            "confirmation_code": self.confirmation_code,
            "customer": self.customer,
            "billing_address": self.billing_address,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Payment":
        """Create Payment from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            order_id=data["order_id"],
            amount=Decimal(data["amount"]),
            currency=data["currency"],
            description=data["description"],
            status=data.get("status", "PENDING"),
            order_tracking_id=data.get("order_tracking_id"),
            redirect_url=data.get("redirect_url"),
            payment_method=data.get("payment_method"),
            confirmation_code=data.get("confirmation_code"),
            customer=data.get("customer", {}),
            billing_address=data.get("billing_address", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

