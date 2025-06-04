from fastapi import APIRouter, status
from typing import Dict, Any
from app.database import update_data_base, query_rag, reload_data_base
from app.gpt.yandex import call_yandex_gpt

import traceback

router = APIRouter()

DATA_PATH = "data"
DB_PATH = "chroma"

from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/update")
async def update_database():
    try:
        await update_data_base(str(DB_PATH), str(DATA_PATH))
        return {"status": "ok", "message": "Database updated"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"500: Database update failed\n{str(e)}")

@router.get(
    "/ask",
    status_code=status.HTTP_200_OK,
    summary="Поиск ответа в FAQ",
    operation_id="search_faq"
)
async def ask_question(question: str) -> Dict[str, Any]:
    try:
        results = await query_rag(str(DB_PATH), question)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No results found"
            )

        context = "\n\n".join([r["document"] for r in results])

        prompt = f"""
        Ты — AI-ассистент, который отвечает на вопросы строго на основе предоставленного контекста. 
        Основные правила:
        1. Если вопрос содержит приветствие ("привет", "добрый день" и т.п.) — ответь вежливым приветствием
        2. Если вопрос содержит прощание ("пока", "до свидания" и т.п.) — ответь вежливым прощанием
        3. Во всех остальных случаях отвечай ТОЛЬКО на основе контекста
        4. Если ответа нет в контексте — так и скажи, не придумывай

        Контекст:
        {context}

        Вопрос:
        {question}

        Дай точный и лаконичный ответ. Если в контексте несколько подходящих вариантов — суммируй главное.
        Примеры:
        - На "Привет" → "Здравствуйте! Чем могу помочь?"
        - На "Пока" → "До свидания! Обращайтесь, если будут вопросы."
        - На вопрос без ответа в контексте → "В предоставленной информации нет ответа на этот вопрос"
        """

        answer = await call_yandex_gpt(prompt)

        return {
            "question": question,
            "answer": answer,
            "context": context,
            "raw_results": results
        }

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        )


@router.post("/reload")
async def reload_database():
    try:
        await reload_data_base(str(DB_PATH), str(DATA_PATH))
        return {"status": "ok", "message": "Database reloaded"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"500: Database reload failed\n{str(e)}")