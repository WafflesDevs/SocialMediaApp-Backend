from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.oauth2 as oauth2
import app.models.models as models
import app.schemas.schemas as schemas
from app.db.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


def _posts_with_votes_stmt():
    return (
        select(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
    )


def _to_post_out(results):
    return [row._mapping for row in results]


@router.get("/", response_model=list[schemas.PostOut])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    stmt = (
        _posts_with_votes_stmt()
        .where(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
    )
    result = await db.execute(stmt)
    return _to_post_out(result.all())


@router.get("/user/{user_id}", response_model=list[schemas.PostOut])
async def get_posts_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    stmt = _posts_with_votes_stmt().where(models.Post.owner_id == user_id)
    result = await db.execute(stmt)
    return _to_post_out(result.all())


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostReponse)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int, db: AsyncSession = Depends(get_db)):
    stmt = _posts_with_votes_stmt().where(models.Post.id == id)
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} not found",
        )
    return row._mapping


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    result = await db.execute(select(models.Post).where(models.Post.id == id))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The id: {id} cannot be deleted since it doesn't exist",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    await db.execute(delete(models.Post).where(models.Post.id == id))
    await db.commit()


@router.put("/{id}", response_model=schemas.PostReponse, status_code=status.HTTP_202_ACCEPTED)
async def update_post(
    id: int,
    post: schemas.PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    result = await db.execute(select(models.Post).where(models.Post.id == id))
    existing = result.scalar_one_or_none()

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} doesn't exist",
        )

    if existing.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to perform action",
        )

    for key, value in post.model_dump().items():
        setattr(existing, key, value)
    await db.commit()
    await db.refresh(existing)
    return existing
