from fastapi import APIRouter, HTTPException, status, Depends
from src.models import UserCreate, UserLogin, UserResponse, Token, APIResponse
from src.database import db_service
from src.auth import authenticate_user_login, create_user_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# PUBLIC_INTERFACE
@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    
    Creates a new user with email and password, returns success confirmation.
    Validates email uniqueness and password requirements.
    """
    try:
        result = await db_service.create_user(user_data)
        
        return APIResponse(
            success=True,
            message="User registered successfully",
            data={
                "user_id": result["user"].id,
                "email": result["user"].email
            }
        )
    
    except Exception as e:
        error_message = str(e)
        if "already registered" in error_message.lower() or "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {error_message}"
        )


# PUBLIC_INTERFACE
@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """
    Authenticate user and return JWT token.
    
    Validates user credentials and returns access token for API authentication.
    Token expires in 30 minutes and must be included in Authorization header.
    """
    user_data = await authenticate_user_login(
        user_credentials.email, 
        user_credentials.password
    )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token_data = create_user_token(user_data["user"].id)
    
    return Token(**token_data)


# PUBLIC_INTERFACE
@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user profile.
    
    Returns user information for the currently authenticated user.
    Requires valid JWT token in Authorization header.
    """
    return current_user
