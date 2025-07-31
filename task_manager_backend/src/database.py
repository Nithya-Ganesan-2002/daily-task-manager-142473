import os
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from src.models import TaskCreate, TaskUpdate, TaskFilter, TaskStatus, UserCreate


class DatabaseService:
    """Database service for Supabase integration"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    # User Operations
    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            # Create user in Supabase Auth
            auth_response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            })
            
            if auth_response.user:
                # Insert user profile in users table
                profile_data = {
                    "id": auth_response.user.id,
                    "email": user_data.email,
                    "full_name": user_data.full_name,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                profile_response = self.client.table("users").insert(profile_data).execute()
                return {
                    "user": auth_response.user,
                    "profile": profile_response.data[0] if profile_response.data else None
                }
            
            raise Exception("Failed to create user")
            
        except Exception as e:
            raise Exception(f"User creation failed: {str(e)}")
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        try:
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user and auth_response.session:
                # Get user profile
                profile_response = self.client.table("users").select("*").eq("id", auth_response.user.id).single().execute()
                
                return {
                    "user": auth_response.user,
                    "session": auth_response.session,
                    "profile": profile_response.data if profile_response.data else None
                }
            
            raise Exception("Invalid credentials")
            
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).single().execute()
            return response.data if response.data else None
        except Exception:
            return None
    
    # Task Operations
    async def create_task(self, user_id: str, task_data: TaskCreate) -> Dict[str, Any]:
        """Create a new task"""
        try:
            task_dict = {
                "title": task_data.title,
                "description": task_data.description,
                "priority": task_data.priority.value,
                "due_date": task_data.due_date.isoformat() if task_data.due_date else None,
                "status": TaskStatus.PENDING.value,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("tasks").insert(task_dict).execute()
            
            if response.data:
                return response.data[0]
            
            raise Exception("Failed to create task")
            
        except Exception as e:
            raise Exception(f"Task creation failed: {str(e)}")
    
    async def get_tasks(self, user_id: str, task_filter: TaskFilter) -> Dict[str, Any]:
        """Get tasks with filtering and pagination"""
        try:
            query = self.client.table("tasks").select("*").eq("user_id", user_id)
            
            # Apply filters
            if task_filter.status:
                query = query.eq("status", task_filter.status.value)
            
            if task_filter.priority:
                query = query.eq("priority", task_filter.priority.value)
            
            if task_filter.search:
                # Search in title and description
                search_term = f"%{task_filter.search}%"
                query = query.or_(f"title.ilike.{search_term},description.ilike.{search_term}")
            
            if task_filter.due_date_from:
                query = query.gte("due_date", task_filter.due_date_from.isoformat())
            
            if task_filter.due_date_to:
                query = query.lte("due_date", task_filter.due_date_to.isoformat())
            
            # Get total count
            count_response = query.execute()
            total = len(count_response.data) if count_response.data else 0
            
            # Apply pagination
            offset = (task_filter.page - 1) * task_filter.per_page
            query = query.order("created_at", desc=True).range(offset, offset + task_filter.per_page - 1)
            
            response = query.execute()
            
            return {
                "tasks": response.data if response.data else [],
                "total": total,
                "page": task_filter.page,
                "per_page": task_filter.per_page
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch tasks: {str(e)}")
    
    async def get_task_by_id(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID"""
        try:
            response = self.client.table("tasks").select("*").eq("id", task_id).eq("user_id", user_id).single().execute()
            return response.data if response.data else None
        except Exception:
            return None
    
    async def update_task(self, user_id: str, task_id: str, task_data: TaskUpdate) -> Optional[Dict[str, Any]]:
        """Update a task"""
        try:
            update_dict = {"updated_at": datetime.utcnow().isoformat()}
            
            # Only update provided fields
            if task_data.title is not None:
                update_dict["title"] = task_data.title
            if task_data.description is not None:
                update_dict["description"] = task_data.description
            if task_data.priority is not None:
                update_dict["priority"] = task_data.priority.value
            if task_data.due_date is not None:
                update_dict["due_date"] = task_data.due_date.isoformat()
            if task_data.status is not None:
                update_dict["status"] = task_data.status.value
                if task_data.status == TaskStatus.COMPLETED:
                    update_dict["completed_at"] = datetime.utcnow().isoformat()
                elif task_data.status == TaskStatus.PENDING:
                    update_dict["completed_at"] = None
            
            response = self.client.table("tasks").update(update_dict).eq("id", task_id).eq("user_id", user_id).execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            raise Exception(f"Task update failed: {str(e)}")
    
    async def delete_task(self, user_id: str, task_id: str) -> bool:
        """Delete a task"""
        try:
            response = self.client.table("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
            return len(response.data) > 0 if response.data else False
        except Exception:
            return False
    
    async def mark_task_complete(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Mark a task as completed"""
        try:
            update_dict = {
                "status": TaskStatus.COMPLETED.value,
                "completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("tasks").update(update_dict).eq("id", task_id).eq("user_id", user_id).execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            raise Exception(f"Failed to mark task complete: {str(e)}")


# Global database service instance
db_service = DatabaseService()
