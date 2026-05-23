## This file defines the authentication-related API endpoints, such as /register and /login.
#  It uses the auth_service for business logic and dependencies for checks.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from services.auth_service import hash_password, verify_password, create_access_token
from dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["Auth"])

## This decorator defines a POST endpoint at /auth/register that accepts a UserRegister request body
#  and returns a UserResponse.
@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    ## Check if the user already exists in the database by querying with the provided email.
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        ## If a user with the same email already exists, raise an HTTP 400 Bad Request error.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    allowed_roles = ["admin", "analyst", "viewer"]

    if user_data.role not in allowed_roles:
        ## If the provided role is not in the list of allowed roles, raise an HTTP 400 Bad Request error.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role must be one of {allowed_roles}")

    ## If the email is not taken, create a new User instance with the provided email, hashed password, and role.
    new_user = User(
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )
    ## Add the new user to the database session and commit the transaction to save it to the database.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    ## This endpoint handles user login. It accepts a UserLogin request body and returns a TokenResponse.
    ## It checks if the user exists and if the password is correct, then generates a JWT token.

    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        ## If the user does not exist or the password is incorrect, raise an HTTP 401 Unauthorized error.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    ## If the credentials are valid, create a JWT access token containing the user's id and role.
    # "sub" is the standard JWT subject claim, and get_current_user reads this field.
    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    ## The token is returned in the response body as a TokenResponse,
    # which includes the access token and its type (bearer).
    return TokenResponse(access_token=token)


## This endpoint is a protected route that returns the current user's information. It uses the get_current_user dependency to retrieve the user based on the JWT token provided in the Authorization header.

# /auth/me checks if token is valid and returns logged-in user info.

# Frontend will use this after refresh to restore session.
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
