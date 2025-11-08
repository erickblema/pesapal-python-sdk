"""Transaction repository for MongoDB operations."""

from typing import Optional, List
from bson import ObjectId
from datetime import datetime

from app.database.db import get_database
from app.models.transaction import Transaction


class TransactionRepository:
    """Repository for transaction database operations."""
    
    def __init__(self):
        self.collection = get_database().transactions
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction record."""
        data = transaction.to_dict()
        result = await self.collection.insert_one(data)
        transaction._id = result.inserted_id
        return transaction
    
    async def get_by_payment_id(self, payment_id: str) -> List[Transaction]:
        """Get all transactions for a payment."""
        cursor = self.collection.find({"payment_id": payment_id}).sort("created_at", 1)
        docs = await cursor.to_list(length=1000)
        return [Transaction.from_dict(doc) for doc in docs]
    
    async def get_by_reference(self, transaction_reference: str) -> Optional[Transaction]:
        """Get transaction by reference (e.g., Pesapal tracking ID)."""
        doc = await self.collection.find_one({"transaction_reference": transaction_reference})
        if doc:
            return Transaction.from_dict(doc)
        return None
    
    async def get_by_provider_id(self, provider_transaction_id: str) -> Optional[Transaction]:
        """Get transaction by provider transaction ID."""
        doc = await self.collection.find_one({"provider_transaction_id": provider_transaction_id})
        if doc:
            return Transaction.from_dict(doc)
        return None
    
    async def update_status(
        self,
        transaction_id: ObjectId,
        status: str,
        confirmation_code: Optional[str] = None,
        processed_at: Optional[datetime] = None
    ) -> Optional[Transaction]:
        """Update transaction status."""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if confirmation_code:
            update_data["confirmation_code"] = confirmation_code
        if processed_at:
            update_data["processed_at"] = processed_at
        
        result = await self.collection.update_one(
            {"_id": transaction_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            doc = await self.collection.find_one({"_id": transaction_id})
            if doc:
                return Transaction.from_dict(doc)
        return None
    
    async def list_transactions(
        self,
        payment_id: Optional[str] = None,
        status: Optional[str] = None,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """List transactions with optional filtering."""
        query = {}
        if payment_id:
            query["payment_id"] = payment_id
        if status:
            query["status"] = status
        if transaction_type:
            query["transaction_type"] = transaction_type
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [Transaction.from_dict(doc) for doc in docs]

