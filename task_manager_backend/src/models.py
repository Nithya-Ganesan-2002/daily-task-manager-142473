from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# User Models
class UserBase(BaseModel):
    """Base user model with common fields"""
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name")


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=6, description="User password (minimum 6 characters)")


class UserLogin(BaseModel):
    """User login model"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """User response model (without password)"""
    id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    model_config = ConfigDict(from_attributes=True)


# Task Models
class TaskBase(BaseModel):
    """Base task model with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Task due date")


class TaskCreate(TaskBase):
    """Task creation model"""
    pass


class TaskUpdate(BaseModel):
    """Task update model (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Optional[TaskPriority] = Field(None, description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    status: Optional[TaskStatus] = Field(None, description="Task status")


class TaskResponse(TaskBase):
    """Task response model"""
    id: str = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Task status")
    user_id: str = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    
    model_config = ConfigDict(from_attributes=True)


# Authentication Models
class Token(BaseModel):
    """JWT token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None


# API Response Models
class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")


class TaskListResponse(BaseModel):
    """Task list response model"""
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")


# Filter Models
class TaskFilter(BaseModel):
    """Task filtering model"""
    status: Optional[TaskStatus] = Field(None, description="Filter by task status")
    priority: Optional[TaskPriority] = Field(None, description="Filter by task priority")
    search: Optional[str] = Field(None, max_length=100, description="Search in title and description")
    due_date_from: Optional[datetime] = Field(None, description="Filter tasks due from this date")
    due_date_to: Optional[datetime] = Field(None, description="Filter tasks due until this date")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page (max 100)")
