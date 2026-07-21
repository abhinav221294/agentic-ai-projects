from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)