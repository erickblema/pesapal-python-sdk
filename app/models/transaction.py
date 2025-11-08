"""Transaction models for comprehensive payment tracking."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from bson import ObjectId
from enum import Enum


class TransactionType(str, Enum):
    """Transaction types."""
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"
    CHARGEBACK = "CHARGEBACK"
    REVERSAL = "REVERSAL"
    FEE = "FEE"
    SETTLEMENT = "SETTLEMENT"


class TransactionStatus(str, Enum):
    """Transaction statuses."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    CHARGEBACK = "CHARGEBACK"
    REVERSED = "REVERSED"


class Transaction:
    """Transaction model for detailed payment tracking."""
    
    def __init__(
        self,
        payment_id: str,  # Reference to payment order_id
        transaction_type: str,
        amount: Decimal,
        currency: str,
        status: str = "PENDING",
        transaction_reference: Optional[str] = None,  # Pesapal tracking ID or other reference
        payment_method: Optional[str] = None,
        payment_provider: str = "PESAPAL",
        provider_transaction_id: Optional[str] = None,
        confirmation_code: Optional[str] = None,
        fees: Optional[Decimal] = None,
        net_amount: Optional[Decimal] = None,  # amount - fees
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        initiated_by: Optional[str] = None,  # User/system that initiated
        processed_at: Optional[datetime] = None,
        settled_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id
        self.payment_id = payment_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.currency = currency
        self.status = status
        self.transaction_reference = transaction_reference
        self.payment_method = payment_method
        self.payment_provider = payment_provider
        self.provider_transaction_id = provider_transaction_id
        self.confirmation_code = confirmation_code
        self.fees = fees
        self.net_amount = net_amount or amount
        self.description = description
        self.metadata = metadata or {}
        self.initiated_by = initiated_by
        self.processed_at = processed_at
        self.settled_at = settled_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB."""
        data = {
            "payment_id": self.payment_id,
            "transaction_type": self.transaction_type,
            "amount": str(self.amount),
            "currency": self.currency,
            "status": self.status,
            "transaction_reference": self.transaction_reference,
            "payment_method": self.payment_method,
            "payment_provider": self.payment_provider,
            "provider_transaction_id": self.provider_transaction_id,
            "confirmation_code": self.confirmation_code,
            "fees": str(self.fees) if self.fees else None,
            "net_amount": str(self.net_amount),
            "description": self.description,
            "metadata": self.metadata,
            "initiated_by": self.initiated_by,
            "processed_at": self.processed_at,
            "settled_at": self.settled_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create Transaction from MongoDB document."""
        return cls(
            _id=data.get("_id"),
            payment_id=data["payment_id"],
            transaction_type=data["transaction_type"],
            amount=Decimal(data["amount"]),
            currency=data["currency"],
            status=data.get("status", "PENDING"),
            transaction_reference=data.get("transaction_reference"),
            payment_method=data.get("payment_method"),
            payment_provider=data.get("payment_provider", "PESAPAL"),
            provider_transaction_id=data.get("provider_transaction_id"),
            confirmation_code=data.get("confirmation_code"),
            fees=Decimal(data["fees"]) if data.get("fees") else None,
            net_amount=Decimal(data["net_amount"]) if data.get("net_amount") else Decimal(data["amount"]),
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            initiated_by=data.get("initiated_by"),
            processed_at=data.get("processed_at"),
            settled_at=data.get("settled_at"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

