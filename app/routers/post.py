from typing import Optional
from fastapi import status, HTTPException, Depends, APIRouter
import app.models.models as models
import app.schemas.schemas as schemas
import app.core.oauth2 as oauth2
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


def _posts_with_votes_query(db: Session):
    return (
        db.query(models.Post, func.count(models.Vote.post_id).label("Votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
    )


def _to_post_out(results):
    return [row._mapping for row in results]


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    results = (
        _posts_with_votes_query(db)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return _to_post_out(results)


@router.get("/user/{user_id}", response_model=list[schemas.PostOut])
def get_posts_by_user(user_id: int, db: Session = Depends(get_db)):
    results = (
        _posts_with_votes_query(db)
        .filter(models.Post.owner_id == user_id)
        .all()
    )
    return _to_post_out(results)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostReponse)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    result = (
        _posts_with_votes_query(db)
        .filter(models.Post.id == id)
        .first()
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} not found",
        )
    return result._mapping


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

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
    post_query.delete(synchronize_session=False)
    db.commit()


@router.put("/{id}", response_model=schemas.PostReponse, status_code=status.HTTP_202_ACCEPTED)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing = post_query.first()

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
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(existing)
    return existing
