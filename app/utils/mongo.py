"""MongoDB utility functions."""
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database.db import get_database
from app.schema.todo import TodoResponse


def validate_object_id(todo_id: str) -> ObjectId:
    """
    Validate and convert string ID to ObjectId.
    
    Args:
        todo_id: String representation of MongoDB ObjectId
        
    Returns:
        ObjectId instance
        
    Raises:
        HTTPException: If the ID format is invalid
    """
    try:
        return ObjectId(todo_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid todo ID format"
        )


def get_todos_collection() -> AsyncIOMotorCollection:
    """Get the todos collection from database."""
    db = get_database()
    return db.todos


def todo_to_response(todo: Dict[str, Any]) -> TodoResponse:
    """
    Convert MongoDB todo document to TodoResponse.
    
    Args:
        todo: MongoDB document dictionary
        
    Returns:
        TodoResponse instance
    """
    # Convert _id to string and create a copy to avoid mutating the original
    todo_dict = dict(todo)
    todo_dict["_id"] = str(todo_dict["_id"])
    return TodoResponse(**todo_dict)


def add_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add created_at and updated_at timestamps to data dictionary.
    
    Args:
        data: Dictionary to add timestamps to
        
    Returns:
        Dictionary with timestamps added
    """
    now = datetime.utcnow()
    data["created_at"] = now
    data["updated_at"] = now
    return data

