
from fastapi import status, HTTPException,Depends,APIRouter
import app.models.models as models,app.schemas.schemas as schemas,app.core.utils as utils,app.core.oauth2 as oauth2
from app.db.database import  get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(
    tags =["Authentication"] #MAKE SURE TO PUT IN MAINPY TO!
)

@router.post("/login",response_model=schemas.Token)
def user_login(login : OAuth2PasswordRequestForm = Depends() ,db: Session = Depends(get_db), status_code=status.HTTP_202_ACCEPTED):
    user = db.query(models.User).filter(models.User.email == login.username).first() #INCLUDES PASS,USER and ID!
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid login")
    
    if not utils.verify(login.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid login")
    access_token = oauth2.create_access_token(data = {"user_id":user.id}) #ONLY USER NOT PASSWORD
    return {"access_token": access_token, "token_type": "bearer"}
    
    

