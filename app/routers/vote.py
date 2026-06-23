from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.oauth2 as oauth2
import app.models.models as models
from app.db.database import get_db
from app.schemas.schemas import UserVote

router = APIRouter(
    prefix="/vote",
    tags=["Vote"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote_post(
    vote: UserVote,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post_result = await db.execute(
        select(models.Post).where(models.Post.id == vote.post_id)
    )
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {vote.post_id} doesnt exist",
        )

    vote_result = await db.execute(
        select(models.Vote).where(
            models.Vote.post_id == vote.post_id,
            models.Vote.user_id == current_user.id,
        )
    )
    existing_vote = vote_result.scalar_one_or_none()

    if vote.dir == 1:
        if existing_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Post has been already been voted by user:{current_user.id} "
                    f"under the post {vote.post_id}"
                ),
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        await db.commit()
        return {"Message": "Successfuly added vote"}

    if not existing_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote does not exist",
        )
    await db.execute(
        delete(models.Vote).where(
            models.Vote.post_id == vote.post_id,
            models.Vote.user_id == current_user.id,
        )
    )
    await db.commit()
    return {"Message": "Vote has been succesfully taken off"}
