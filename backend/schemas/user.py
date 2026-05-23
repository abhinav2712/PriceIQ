## This file defines API request/response shapes and database models related to users. 
# It includes Pydantic models for validation and SQLAlchemy models for ORM.

from pydantic import BaseModel, EmailStr


## SQLAlchemy models represent database tables.
## Pydantic schemas represent request and response bodies.


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "viewer" # default role is viewer

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"