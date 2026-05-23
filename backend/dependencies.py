## This file contains reusable FastAPI checks like auth/roles

import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import get_db
from models.user import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# get_current_user
# does this:

# 1. Reads token from Authorization header
# 2. Decodes JWT
# 3. Extracts user id from token
# 4. Fetches user from database
# 5. Returns user object to endpoints that depend on it. If any step fails, it raises an HTTP 401 error.


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    ## This function is a dependency that retrieves the current user based on the JWT token provided in the Authorization header.
    ## It decodes the token, extracts the user id, and fetches the user from the database.

    ## Depends(oauth2_scheme) tells FastAPI to use the OAuth2PasswordBearer dependency to extract the 
    # token from the request.
    ## Depends(get_db) provides a database session to the function.

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    return user

def require_role(*allowed_roles):
    ## This function is a dependency factory that checks if the current user has one of the allowed roles.
    ## It uses the get_current_user dependency to get the user and then checks their role against the allowed roles.

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return role_checker
