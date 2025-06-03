from fastapi import APIRouter, status, HTTPException
from pathlib import Path
from typing import Dict, Any
from app.database import update_data_base, query_rag

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
        return {"results": results}
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        )
