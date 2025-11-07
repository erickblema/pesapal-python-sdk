from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

from app.schema.todo import TodoCreate, TodoUpdate, TodoResponse
from app.utils.mongo import (
    validate_object_id,
    get_todos_collection,
    todo_to_response,
    add_timestamps
)


router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    """
    Create a new todo item.
    
    - **title**: Todo title (required, 1-200 characters)
    - **description**: Optional description (max 1000 characters)
    - **completed**: Completion status (default: false)
    """
    collection = get_todos_collection()
    
    todo_dict = add_timestamps(todo.model_dump())
    result = await collection.insert_one(todo_dict)
    created_todo = await collection.find_one({"_id": result.inserted_id})
    
    return todo_to_response(created_todo)


@router.get("/", response_model=List[TodoResponse])
async def get_todos(skip: int = 0, limit: int = 100):
    """
    Get all todo items with pagination.
    
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Maximum number of items to return (default: 100)
    """
    collection = get_todos_collection()
    
    cursor = collection.find().skip(skip).limit(limit).sort("created_at", -1)
    todos = await cursor.to_list(length=limit)
    
    return [todo_to_response(todo) for todo in todos]


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str):
    """
    Get a specific todo item by ID.
    
    - **todo_id**: The ID of the todo item
    """
    collection = get_todos_collection()
    object_id = validate_object_id(todo_id)
    
    todo = await collection.find_one({"_id": object_id})
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    
    return todo_to_response(todo)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, todo_update: TodoUpdate):
    """
    Update a todo item.
    
    - **todo_id**: The ID of the todo item to update
    - **title**: Optional new title
    - **description**: Optional new description
    - **completed**: Optional completion status
    """
    collection = get_todos_collection()
    object_id = validate_object_id(todo_id)
    
    # Check if todo exists
    existing_todo = await collection.find_one({"_id": object_id})
    if existing_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    
    # Prepare update data (only include fields that are provided)
    update_data = {
        k: v for k, v in todo_update.model_dump(exclude_unset=True).items() 
        if v is not None
    }
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    await collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    
    updated_todo = await collection.find_one({"_id": object_id})
    return todo_to_response(updated_todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str):
    """
    Delete a todo item.
    
    - **todo_id**: The ID of the todo item to delete
    """
    collection = get_todos_collection()
    object_id = validate_object_id(todo_id)
    
    result = await collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    
    return None

