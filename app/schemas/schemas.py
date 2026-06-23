from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserReponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class PostReponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserReponse

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class UserVote(BaseModel):
    post_id: int
    dir: int = Field(ge=0, le=1)


class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id: int
    owner: UserReponse

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post: Post
    Votes: int

    class Config:
        from_attributes = True


class Profile(BaseModel):
    id: int
    email: str
    posts: list[Post] = []

    class Config:
        from_attributes = True
