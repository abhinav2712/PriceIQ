## This file has business logic related to authentication, such as user registration, login, and token generation.

## After login, the backend creates a signed JWT containing the user id and role. 
# The frontend stores that token and sends it in the Authorization header for protected routes.


import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

## These constants are used for JWT token generation and password hashing.
#  They are loaded from environment variables for security reasons.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

## The pwd_context is used to hash and verify passwords securely using the bcrypt algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    ## This function takes a plain password and returns a hashed version using the pwd_context.
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    ## This function verifies that a plain password matches the hashed password.
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    ## This function creates a JWT access token with the given data and expiration time.
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    ## The jwt.encode function generates a JWT token by encoding the data with the SECRET_KEY and ALGORITHM.
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token
