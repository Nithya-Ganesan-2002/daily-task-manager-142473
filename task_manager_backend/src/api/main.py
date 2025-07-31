from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.models import APIResponse

# OpenAPI configuration
app = FastAPI(
    title="Task Manager API",
    description="""
    A comprehensive REST API for managing daily tasks with user authentication.
    
    ## Features
    
    * **User Authentication**: Register and login with JWT tokens
    * **Task Management**: Create, read, update, and delete tasks
    * **Task Completion**: Mark tasks as completed with timestamps
    * **Filtering & Search**: Filter tasks by status, priority, due date, and text search
    * **Pagination**: Handle large task lists with pagination support
    
    ## Authentication
    
    Most endpoints require authentication using JWT Bearer tokens.
    1. Register a new account or login to get an access token
    2. Include the token in the Authorization header: `Bearer <token>`
    3. Tokens expire after 30 minutes and need to be refreshed
    
    ## Usage Examples
    
    ### Register a new user
    ```
    POST /auth/register
    {
        "email": "user@example.com",
        "password": "securepassword",
        "full_name": "John Doe"
    }
    ```
    
    ### Login and get token
    ```
    POST /auth/login
    {
        "email": "user@example.com", 
        "password": "securepassword"
    }
    ```
    
    ### Create a task
    ```
    POST /tasks/
    Authorization: Bearer <token>
    {
        "title": "Complete project",
        "description": "Finish the task manager implementation",
        "priority": "high",
        "due_date": "2024-02-01T10:00:00Z"
    }
    ```
    
    ### Get tasks with filtering
    ```
    GET /tasks/?status=pending&priority=high&search=project&page=1&per_page=10
    Authorization: Bearer <token>
    ```
    """,
    version="1.0.0",
    contact={
        "name": "Task Manager API Support",
        "email": "support@taskmanager.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)

# PUBLIC_INTERFACE
@app.get("/", response_model=APIResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns API status and basic information.
    Use this endpoint to verify the API is running correctly.
    """
    return APIResponse(
        success=True,
        message="Task Manager API is running",
        data={
            "version": "1.0.0",
            "status": "healthy",
            "endpoints": {
                "auth": "/auth",
                "tasks": "/tasks",
                "docs": "/docs",
                "openapi": "/openapi.json"
            }
        }
    )
