from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.auth.security import decode_access_token
from src.memory.database import get_db
from src.memory.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Authenticate the current user using the JWT token.
    """

    payload = decode_access_token(token)

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        details="Invalid authentication credentials",
        )

    user = (
    db.query(User)
    .filter(User.id == int(user_id))
    .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="User not found"
        )
    
    return user

def get_current_admin(
        current_user:User = Depends(get_current_user)
):
    """
    Ensure the authenticated user is an administrator.
    """

    if not current_user.is_admin:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           details="Administrator access required"
       )

    return current_user      