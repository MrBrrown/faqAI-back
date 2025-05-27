from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import chat
from app.telegram_bot.bot import start_bot
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем телеграм-бота в фоне
    asyncio.create_task(start_bot())
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/", tags=["Root"])
async def root() -> dict:
    return {"msg": "Hello World!"}

app.include_router(chat.router)