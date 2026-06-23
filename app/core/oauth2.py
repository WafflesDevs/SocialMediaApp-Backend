from jose import jwt,JWTError
from datetime import datetime,timedelta
import app.schemas.schemas as schemas,app.db.database as database,app.models.models as models
from sqlalchemy.orm import Session
from fastapi import Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
#SECRET_KEY #RUN openssl rand -hex 32
#ALGO
# EXPIRE TOKEN TIME

SECRET_KEY = settings.secret_key
ALGO =  settings.algorithm
TOKEN_EXPIRE_TIME = settings.access_token_expire_minutes

def create_access_token(data:dict): #Data  #Makes a new JWT TOKEN
    to_encode = data.copy() #We needa copy always
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGO) #THe data we wanna put into jwt, the SECERT_KEY and the algo always COPY the data
    return encoded_jwt

def verify_access_token(token:str,credit_exception): #CHECKS FOR ID IN TOKEN AND RETURNS IT
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGO)
        id:str = payload.get("user_id")
        if id is None:
            raise credit_exception
        token_data = schemas.TokenData(id=str(id))
    except JWTError: #Any errors verifying 
        raise credit_exception
    return token_data
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == int(token_data.id)).first()
    if user is None:
        raise credentials_exception
    return user


    