from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.library.library_router import router as library_router
from app.loan_management.book_loans_router import router as book_loans_router
from app.ai.chatbot_router import router as chatbot_router
from app.database.initialize_db import initialize_database
from app.server_config import ServerConfig
from app.user.user_router import router as user_router
from app.file_paths import DATABASE_PATH, LIBRARY_DB_PATH
from app.facial_recognition.facial_recognition_router import (
    router as facial_recognition_router,
)
from app.library import library_db


class QuestionRequest(BaseModel):
    question: str


server_config = ServerConfig()

app = FastAPI()

origins = [server_config.get_origins()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router)
app.include_router(user_router)
app.include_router(facial_recognition_router)
app.include_router(library_router)
app.include_router(book_loans_router)


@app.get("/ping")
async def ping():
    return {"ping": "pong"}


initialize_database(DATABASE_PATH)
library_db.initialize_database(LIBRARY_DB_PATH)
