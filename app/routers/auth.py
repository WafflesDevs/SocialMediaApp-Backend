from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.oauth2 as oauth2
import app.core.utils as utils
import app.models.models as models
import app.schemas.schemas as schemas
from app.db.database import get_db

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token, status_code=status.HTTP_200_OK)
async def user_login(
    login: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.User).where(models.User.email == login.username)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid login",
        )

    if not utils.verify(login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid login",
        )
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
