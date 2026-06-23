
from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

class PostBase(BaseModel):
    title: str
    content: str
    published : bool = True

class PostCreate(PostBase):
    pass
class UserReponse(BaseModel):
    id: int
    email: EmailStr
    created_at : datetime
    class Config:
        orm_mode = True
class PostReponse(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode = True
class PostReponse(PostBase):
    owner : PostReponse
    class Config:
        orm_mode = True #SQL database code is now readable! so it works in everything now since SQLAchemly uses SQL so now users see SQL data

class UserCreate(BaseModel):
    email : EmailStr
    password: str

class UserLogin(BaseModel):
        email : EmailStr
        password: str
class Token(BaseModel):
        access_token : str
        token_type: str

class TokenData(BaseModel):
     id : Optional[str]

class UserVote(BaseModel):
    post_id : int
    dir: int = conint(le=1)
    class Config:
        orm_mode = True

# schemas.py

class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id: int
    owner: UserReponse  # if you include owner

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post: Post       # matches the key name from the query tuple
    Votes: int       # matches 'Votes' — wait, case matters! (see note below)

    class Config:
        from_attributes = True

class Profile(BaseModel):
    id: int
    email: str
    posts: list[Post] = []

    class Config:
        from_attributes = True  # orm_mode = True in Pydantic v1