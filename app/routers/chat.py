from fastapi import APIRouter, status, HTTPException
from pathlib import Path
from typing import Dict, Any
from app.database import update_data_base, query_rag, reload_data_base
from app.gpt.yandex import call_yandex_gpt

import traceback

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent
DATA_PATH = BASE_DIR / "data"
DB_PATH = BASE_DIR / "chroma"

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

        prompt = f"Ответь на вопрос на основе контекста.\n\nКонтекст:\n{context}\n\nВопрос:\n{question}"

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