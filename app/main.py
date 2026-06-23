from fastapi import FastAPI
from app.models import models
from app.db.database import engine
from app.routers import post, user, auth, vote
from app.core.config import Settings
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine) NO LONGER NEEDED BCZ OF ALMEBIC!
app = FastAPI()
origins = [ #wHERE YOUR APP CAN RUN ON AND GET DATA! 
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"Sup": "Waffleo"}

settings = Settings()