from fastapi import FastAPI
from app.routers import chat

app = FastAPI()

@app.get("/", tags=["Root"])
async def root() -> dict:
    return {"msg": "Hello World!"}

app.include_router(chat.router)