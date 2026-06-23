from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.utils as utils
import app.models.models as models
import app.schemas.schemas as schemas
from app.db.database import get_db
from app.schemas.schemas import UserCreate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserReponse)
async def create_user(info: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(models.User.email == info.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_226_IM_USED,
            detail=f"The email {info.email} is already in use!",
        )

    info.password = utils.hash(info.password)
    new_user = models.User(**info.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.Profile)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user with id:{id} is not found",
        )

    posts_result = await db.execute(
        select(models.Post).where(models.Post.owner_id == id)
    )
    user.posts = posts_result.scalars().all()
    return user
