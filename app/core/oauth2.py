from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.database as database
import app.models.models as models
import app.schemas.schemas as schemas
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGO = settings.algorithm
TOKEN_EXPIRE_TIME = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_TIME)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return schemas.TokenData(id=str(user_id))
    except JWTError:
        raise credentials_exception


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(database.get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    result = await db.execute(
        select(models.User).where(models.User.id == int(token_data.id))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
