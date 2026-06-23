
from fastapi import FastAPI,Response,status, HTTPException,Depends,APIRouter
import app.models.models as models,app.schemas.schemas as schemas,app.core.utils as utils
from app.db.database import  get_db
from sqlalchemy.orm import Session
from app.schemas.schemas import  UserVote
import app.core.oauth2 as oauth2,app.db.database as database,app.schemas.schemas as schemas,app.models.models as models


router = APIRouter(
    prefix="/vote",
    tags=['Vote'] #Swagger UI shows this as diff section!
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote_post(vote: UserVote,db: Session = Depends(get_db), current_user  = Depends(oauth2.get_current_user),): #You need current user to check if user is logged in and for id
    checker = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,models.Vote.user_id == current_user.id)
    posts = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post {vote.post_id} doesnt exist")
        
    if(vote.dir == 1):
        found_vote = checker.first()
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Post has been already been voted by user:{current_user.id} under the post {vote.post_id}")
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id) #Basicaly setting it up
        db.add(new_vote) #adds it
        db.commit()
        return{"Message":"Successfuly added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Vote does not exist")
        found_vote.delete(synchronize_session=False)
        db.commit()
        return{"Message":"Vote has been succesfully taken off"}


