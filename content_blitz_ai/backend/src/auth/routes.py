from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from src.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from src.memory.models import User
from src.memory.database import get_db



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    # Check if email already exists
    email_exists = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    username_exists = (
        db.query(User)
        .filter(User.username == request.username)
        .first()
    )

    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Hash the password
    hashed_password = hash_password(request.password)

    # Create a new user
    user = User(
        username=request.username,
        email=request.email,
        password=hashed_password,
    )

    # Save to database
    db.add(user)
    db.commit()
    db.refresh(user)

    # Return response
    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    # Email not found
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Wrong password
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT
    access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user