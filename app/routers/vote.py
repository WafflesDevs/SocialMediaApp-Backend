from fastapi import status, HTTPException, Depends, APIRouter
import app.models.models as models
import app.core.oauth2 as oauth2
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.schemas.schemas import UserVote

router = APIRouter(
    prefix="/vote",
    tags=["Vote"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote_post(
    vote: UserVote,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id,
    )
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {vote.post_id} doesnt exist",
        )

    existing_vote = vote_query.first()

    if vote.dir == 1:
        if existing_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Post has been already been voted by user:{current_user.id} under the post {vote.post_id}",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"Message": "Successfuly added vote"}

    if not existing_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote does not exist",
        )
    vote_query.delete(synchronize_session=False)
    db.commit()
    return {"Message": "Vote has been succesfully taken off"}
