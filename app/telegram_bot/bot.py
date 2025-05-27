import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from config import settings


# Настройка бота:
# Получите токен бота у @BotFather
# Вставить полученный токен в файл .env
# Убедиться что API доступно по указанному в .env URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


async def send_to_api(question: str) -> dict:
    async with httpx.AsyncClient(base_url=settings.API_BASE_URL) as client:
        try:
            response = await client.get(
                "/ask",
                params={"question": question},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            return {"error": str(e)}


@dp.message(Command("start"))
async def handle_start(message: Message):
    text = (
        "Привет! Я бот поддержки.\n"
        "Задайте мне вопрос о платформе, и я постараюсь помочь!"
    )
    await message.answer(text)


@dp.message()
async def handle_message(message: Message):
    question = message.text
    response = await send_to_api(question)

    if "error" in response:
        await message.answer("⚠️ Ошибка при обработке запроса. Попробуйте позже.")
        return

    if not response.get("results"):
        await message.answer("❌ Не нашел подходящего ответа. Попробуйте переформулировать вопрос.")
        return

    answers = [res["document"] for res in response["results"]]
    full_answer = "\n\n".join(answers)[:4096]  # Ограничение Telegram на длину сообщения
    await message.answer(full_answer)


async def start_bot():
    await dp.start_polling(bot)