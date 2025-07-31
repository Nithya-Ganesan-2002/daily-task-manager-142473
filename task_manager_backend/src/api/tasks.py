from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from datetime import datetime
from src.models import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, 
    TaskFilter, TaskStatus, TaskPriority, APIResponse, UserResponse
)
from src.database import db_service
from src.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# PUBLIC_INTERFACE
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new task.
    
    Creates a task with title, description, priority, and optional due date.
    Task is automatically assigned to the authenticated user.
    """
    try:
        task = await db_service.create_task(current_user.id, task_data)
        
        return TaskResponse(
            id=task["id"],
            title=task["title"],
            description=task["description"],
            priority=task["priority"],
            due_date=datetime.fromisoformat(task["due_date"]) if task["due_date"] else None,
            status=task["status"],
            user_id=task["user_id"],
            created_at=datetime.fromisoformat(task["created_at"]),
            updated_at=datetime.fromisoformat(task["updated_at"]),
            completed_at=datetime.fromisoformat(task["completed_at"]) if task["completed_at"] else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task creation failed: {str(e)}"
        )


# PUBLIC_INTERFACE
@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    search: Optional[str] = Query(None, max_length=100, description="Search in title and description"),
    due_date_from: Optional[datetime] = Query(None, description="Filter tasks due from this date"),
    due_date_to: Optional[datetime] = Query(None, description="Filter tasks due until this date"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get tasks with filtering and pagination.
    
    Retrieves user's tasks with optional filtering by status, priority, due date,
    and text search. Supports pagination for large task lists.
    """
    try:
        task_filter = TaskFilter(
            status=status,
            priority=priority,
            search=search,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            page=page,
            per_page=per_page
        )
        
        result = await db_service.get_tasks(current_user.id, task_filter)
        
        tasks = []
        for task_data in result["tasks"]:
            tasks.append(TaskResponse(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                due_date=datetime.fromisoformat(task_data["due_date"]) if task_data["due_date"] else None,
                status=task_data["status"],
                user_id=task_data["user_id"],
                created_at=datetime.fromisoformat(task_data["created_at"]),
                updated_at=datetime.fromisoformat(task_data["updated_at"]),
                completed_at=datetime.fromisoformat(task_data["completed_at"]) if task_data["completed_at"] else None
            ))
        
        return TaskListResponse(
            tasks=tasks,
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


# PUBLIC_INTERFACE
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a specific task by ID.
    
    Retrieves detailed information for a single task.
    Only returns tasks owned by the authenticated user.
    """
    task = await db_service.get_task_by_id(current_user.id, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=task["id"],
        title=task["title"],
        description=task["description"],
        priority=task["priority"],
        due_date=datetime.fromisoformat(task["due_date"]) if task["due_date"] else None,
        status=task["status"],
        user_id=task["user_id"],
        created_at=datetime.fromisoformat(task["created_at"]),
        updated_at=datetime.fromisoformat(task["updated_at"]),
        completed_at=datetime.fromisoformat(task["completed_at"]) if task["completed_at"] else None
    )


# PUBLIC_INTERFACE
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update a task.
    
    Updates task fields including title, description, priority, due date, and status.
    Only allows updating tasks owned by the authenticated user.
    """
    try:
        task = await db_service.update_task(current_user.id, task_id, task_data)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return TaskResponse(
            id=task["id"],
            title=task["title"],
            description=task["description"],
            priority=task["priority"],
            due_date=datetime.fromisoformat(task["due_date"]) if task["due_date"] else None,
            status=task["status"],
            user_id=task["user_id"],
            created_at=datetime.fromisoformat(task["created_at"]),
            updated_at=datetime.fromisoformat(task["updated_at"]),
            completed_at=datetime.fromisoformat(task["completed_at"]) if task["completed_at"] else None
        )
    
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task update failed: {str(e)}"
        )


# PUBLIC_INTERFACE
@router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a task.
    
    Permanently removes a task from the user's task list.
    Only allows deleting tasks owned by the authenticated user.
    """
    success = await db_service.delete_task(current_user.id, task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return APIResponse(
        success=True,
        message="Task deleted successfully"
    )


# PUBLIC_INTERFACE
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def mark_task_complete(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Mark a task as completed.
    
    Updates task status to completed and sets completion timestamp.
    Only allows completing tasks owned by the authenticated user.
    """
    try:
        task = await db_service.mark_task_complete(current_user.id, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return TaskResponse(
            id=task["id"],
            title=task["title"],
            description=task["description"],
            priority=task["priority"],
            due_date=datetime.fromisoformat(task["due_date"]) if task["due_date"] else None,
            status=task["status"],
            user_id=task["user_id"],
            created_at=datetime.fromisoformat(task["created_at"]),
            updated_at=datetime.fromisoformat(task["updated_at"]),
            completed_at=datetime.fromisoformat(task["completed_at"]) if task["completed_at"] else None
        )
    
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to mark task complete: {str(e)}"
        )
