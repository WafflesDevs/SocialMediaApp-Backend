from typing import Optional,List
from fastapi import status, HTTPException,Depends,APIRouter
import app.models.models as models,app.schemas.schemas as schemas,app.core.oauth2 as oauth2
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.schemas.schemas import PostCreate,PostReponse,PostOut
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts'] #Swagger UI shows this as diff section!
)
#@router.get("/",response_model=List[PostReponse])
@router.get("/",response_model=list[schemas.PostOut] )
def root(db: Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user),limit : int = 10,skip: int  = 0, search : Optional[str] = ""):
     # posts  = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() #models.post is the database in database.py and all() is everything in the table
     results = db.query(models.Post,func.count(models.Vote.post_id).label("Votes")).join(models.Vote, models.Vote.post_id  == models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() #Basically we are joining the post_id and id is to show the votes in the post and label means renaming the colunum
     results = list ( map (lambda x : x._mapping, results) ) #turns the query result into somthing the schema can read
     return results

@router.get("/{id}",response_model=List[PostOut])
def root(id :int,db: Session = Depends(get_db)):
    #posts  = db.query(models.Post).filter(models.Post.owner_id == id).all() #models.post is the database in database.py and all() is everything in the table, db.query is a a
    post = db.query(models.Post,func.count(models.Vote.post_id).label("Votes")).join(models.Vote, models.Vote.post_id  == models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.owner_id == id).all()
    return post



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostReponse) #Return 201 when ran sucessful + return it in the schema I MADE! thats what it says
def create_post(post : schemas.PostCreate ,db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)): #It takes from body and converts into dict and into payload and checks if user_id is active
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post) #Adds onto Db
    db.commit() # Finalizes it
    db.refresh(new_post) #Retreive it and store it back into new_post!
    return new_post

@router.get("/{id}", response_model=schemas.PostReponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                           detail=f"Post with id: {id} not found")
    return post  # not {"Post": post}

   
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"The id: {id} cannot be deleted since it doesn't exist")

    if post.owner_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    post_query.delete(synchronize_session=False)
    db.commit()
@router.put("/{id}", response_model=schemas.PostReponse,status_code=status.HTTP_202_ACCEPTED)
def update_post(id: int, post: PostCreate, db: Session = Depends(get_db), user_id : int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    checker = post_query.first()
    
    if checker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f"Post with id: {id} doesn't exist")
    
    if checker.owner_id != user_id.id:
         return HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not allowed to peform action")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    db.refresh(checker)
    return checker  # just return the object directly, not wrapped in a dict
