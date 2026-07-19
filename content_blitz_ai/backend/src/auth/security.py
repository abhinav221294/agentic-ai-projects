from datetime import datetime, timedelta, timezone

from jose import jwt,JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from src.core.config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )



def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Payload to include in the token.
              Example: {"sub": "user@example.com"}

        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT token.
    """

    # Copy the payload so we don't modify the original dictionary
    to_encode = data.copy()

    # Determine token expiration
    expire = (
        datetime.now(timezone.utc)
        + (
            expires_delta
            if expires_delta
            else timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    # JWT standard expiration claim
    to_encode.update({"exp": expire})

    # Sign and encode the JWT
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=[ALGORITHM],
    )

    return encoded_jwt

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.
    """

    # Copy the payload
    to_encode = data.copy()

    # Set expiration time
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Add expiration claim
    to_encode["exp"] = expire

    # Encode and sign the JWT
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        )