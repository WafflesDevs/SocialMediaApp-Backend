
from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
import app.models.models as models,app.schemas.schemas as schemas,app.core.utils as utils
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.schemas.schemas import UserCreate

router = APIRouter(
    prefix="/users",
    tags=['Users'] #Swagger UI shows this as diff section!
)



@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.UserReponse)
def create_user(info : UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == info.email).first():
        raise HTTPException(status_code=status.HTTP_226_IM_USED,detail=f"The email {info.email} is already in use!")

    info.password = utils.hash(info.password)
    new_user = models.User(**info.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.get("/{id}", response_model=schemas.Profile)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The user with id:{id} is not found")
    
    user.posts = db.query(models.Post).filter(models.Post.owner_id == id).all()
    return user