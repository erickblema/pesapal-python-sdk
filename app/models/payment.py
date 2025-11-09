"""Payment models for MongoDB."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from bson import ObjectId
from enum import Enum


class PaymentState(str, Enum):
    """Clear payment states."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentEvent:
    """Represents a payment event/status change."""
    
    def __init__(
        self,
        event_type: str,
        status: str,
        source: str,  # "CREATION", "CALLBACK", "WEBHOOK", "MANUAL_CHECK"
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.event_type = event_type  # "CREATED", "STATUS_CHANGED", "CALLBACK_RECEIVED", "WEBHOOK_RECEIVED"
        self.status = status
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "status": self.status,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PaymentEvent":
        """Create PaymentEvent from dictionary."""
        return cls(
            event_type=data.get("event_type", "STATUS_CHANGED"),
            status=data.get("status", "PENDING"),
            source=data.get("source", "UNKNOWN"),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.utcnow())
        )


class Payment:
    """Payment document model with comprehensive event tracking - Fintech grade."""
    
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
        merchant_id: Optional[str] = None,
        branch: Optional[str] = None,
        fees: Optional[Decimal] = None,
        net_amount: Optional[Decimal] = None,
        total_amount: Optional[Decimal] = None,  # amount + fees
        payment_provider: str = "PESAPAL",
        provider_response: Optional[dict] = None,  # Full response from provider
        callback_received: bool = False,
        callback_received_at: Optional[datetime] = None,
        webhook_received: bool = False,
        webhook_received_at: Optional[datetime] = None,
        last_status_check: Optional[datetime] = None,
        status_history: Optional[List[Dict[str, Any]]] = None,  # Status change history
        events: Optional[List[PaymentEvent]] = None,
        metadata: Optional[Dict[str, Any]] = None,
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
        self.merchant_id = merchant_id
        self.branch = branch
        self.fees = fees
        self.net_amount = net_amount or amount
        self.total_amount = total_amount or amount
        self.payment_provider = payment_provider
        self.provider_response = provider_response or {}
        self.callback_received = callback_received
        self.callback_received_at = callback_received_at
        self.webhook_received = webhook_received
        self.webhook_received_at = webhook_received_at
        self.last_status_check = last_status_check
        self.status_history = status_history or []
        self.events = events or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def add_event(
        self,
        event_type: str,
        status: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a payment event to the history."""
        event = PaymentEvent(event_type, status, source, metadata)
        self.events.append(event)
        self.updated_at = datetime.utcnow()
        return event
    
    def add_status_change(
        self,
        old_status: str,
        new_status: str,
        source: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a status change to history."""
        status_entry = {
            "old_status": old_status,
            "new_status": new_status,
            "source": source,
            "reason": reason,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        }
        self.status_history.append(status_entry)
        self.status = new_status
        self.updated_at = datetime.utcnow()
        return status_entry
    
    def get_payment_state(self) -> str:
        """
        Get clear payment state based on status code and payment completion indicators.
        
        IMPORTANT: 
        - Pesapal returns "200" when payment is submitted, NOT when completed
        - A payment is only COMPLETED when it has payment_method or confirmation_code
        - Status codes: "200" (submitted/completed), "FAILED", "INVALID", "REVERSED"
        
        Returns:
            PaymentState enum value (PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED)
        """
        status_code = str(self.status).upper()
        
        # Check if payment is actually completed (has payment method or confirmation code)
        is_actually_completed = bool(self.payment_method or self.confirmation_code)
        
        # Handle different status codes
        if status_code == "200":
            # "200" from Pesapal can mean:
            # 1. Payment submitted to Pesapal (not yet paid) - should be PENDING
            # 2. Payment completed by customer (has payment_method/confirmation_code) - should be COMPLETED
            if is_actually_completed:
                return PaymentState.COMPLETED.value
            else:
                # Submitted but not yet paid - customer still needs to complete payment
                return PaymentState.PENDING.value
        elif status_code == "REVERSED":
            # Payment was reversed
            return PaymentState.FAILED.value
        elif status_code in ["FAILED", "ERROR", "INVALID", "0"]:
            return PaymentState.FAILED.value
        elif status_code in ["PENDING", "PROCESSING"]:
            return PaymentState.PROCESSING.value
        elif status_code == "CANCELLED":
            return PaymentState.CANCELLED.value
        else:
            # Default to pending if status is unclear
            return PaymentState.PENDING.value
    
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.get_payment_state() == PaymentState.COMPLETED.value
    
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.get_payment_state() == PaymentState.FAILED.value
    
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.get_payment_state() == PaymentState.PENDING.value
    
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
            "merchant_id": self.merchant_id,
            "branch": self.branch,
            "fees": str(self.fees) if self.fees else None,
            "net_amount": str(self.net_amount),
            "total_amount": str(self.total_amount),
            "payment_provider": self.payment_provider,
            "provider_response": self.provider_response,
            "callback_received": self.callback_received,
            "callback_received_at": self.callback_received_at,
            "webhook_received": self.webhook_received,
            "webhook_received_at": self.webhook_received_at,
            "last_status_check": self.last_status_check,
            "status_history": self.status_history,
            "events": [event.to_dict() for event in self.events],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Payment":
        """Create Payment from MongoDB document."""
        events = []
        if "events" in data and data["events"]:
            events = [PaymentEvent.from_dict(e) for e in data["events"]]
        
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
            merchant_id=data.get("merchant_id"),
            branch=data.get("branch"),
            fees=Decimal(data["fees"]) if data.get("fees") else None,
            net_amount=Decimal(data["net_amount"]) if data.get("net_amount") else Decimal(data["amount"]),
            total_amount=Decimal(data["total_amount"]) if data.get("total_amount") else Decimal(data["amount"]),
            payment_provider=data.get("payment_provider", "PESAPAL"),
            provider_response=data.get("provider_response", {}),
            callback_received=data.get("callback_received", False),
            callback_received_at=data.get("callback_received_at"),
            webhook_received=data.get("webhook_received", False),
            webhook_received_at=data.get("webhook_received_at"),
            last_status_check=data.get("last_status_check"),
            status_history=data.get("status_history", []),
            events=events,
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

