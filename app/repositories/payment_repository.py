"""Payment repository for MongoDB operations."""

from typing import Optional, List
from bson import ObjectId
from datetime import datetime

from app.database.db import get_database
from app.models.payment import Payment


class PaymentRepository:
    """Repository for payment database operations."""
    
    def __init__(self):
        self.collection = get_database().payments
    
    async def create(self, payment: Payment) -> Payment:
        """Create a new payment record."""
        data = payment.to_dict()
        result = await self.collection.insert_one(data)
        payment._id = result.inserted_id
        return payment
    
    async def get_by_order_id(self, order_id: str) -> Optional[Payment]:
        """Get payment by order ID."""
        doc = await self.collection.find_one({"order_id": order_id})
        if doc:
            return Payment.from_dict(doc)
        return None
    
    async def get_by_tracking_id(self, order_tracking_id: str) -> Optional[Payment]:
        """Get payment by Pesapal tracking ID."""
        doc = await self.collection.find_one({"order_tracking_id": order_tracking_id})
        if doc:
            return Payment.from_dict(doc)
        return None
    
    async def update_status(
        self,
        order_id: str,
        status: str,
        payment_method: Optional[str] = None,
        confirmation_code: Optional[str] = None,
        event: Optional[dict] = None
    ) -> Optional[Payment]:
        """Update payment status with event tracking."""
        # Get current payment to check if status changed
        current_payment = await self.get_by_order_id(order_id)
        if not current_payment:
            return None
        
        # Build update operation
        update_operation = {
            "$set": {
                "status": status,
                "updated_at": datetime.utcnow()
            }
        }
        
        if payment_method:
            update_operation["$set"]["payment_method"] = payment_method
        if confirmation_code:
            update_operation["$set"]["confirmation_code"] = confirmation_code
        
        # Add event to events array if provided
        if event:
            update_operation["$push"] = {"events": event}
        
        result = await self.collection.update_one(
            {"order_id": order_id},
            update_operation
        )
        
        if result.modified_count > 0:
            return await self.get_by_order_id(order_id)
        return None
    
    async def add_event(
        self,
        order_id: str,
        event: dict
    ) -> Optional[Payment]:
        """Add an event to payment history."""
        result = await self.collection.update_one(
            {"order_id": order_id},
            {
                "$push": {"events": event},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            return await self.get_by_order_id(order_id)
        return None
    
    async def list_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Payment]:
        """List payments with optional filtering."""
        query = {}
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [Payment.from_dict(doc) for doc in docs]

