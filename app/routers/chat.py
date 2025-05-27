from fastapi import APIRouter, status, HTTPException
from pathlib import Path
from typing import Dict, Any
from app.database import update_data_base, query_rag

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent
DATA_PATH = BASE_DIR / "data"
DB_PATH = BASE_DIR / "chroma"

@router.get(
    "/update",
    status_code=status.HTTP_200_OK,
    summary="Updating the database",
    operation_id="update_faq_database"
)
def update_database():
    try:
        success = update_data_base(str(DB_PATH), str(DATA_PATH))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database update failed"
            )
        return {"message": "Database updated successfully"}
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        )

@router.get(
    "/ask",
    status_code=status.HTTP_200_OK,
    summary="Поиск ответа в FAQ",
    operation_id="search_faq"
)
def ask_question(question: str) -> Dict[str, Any]:
    try:
        results = query_rag(str(DB_PATH), question)
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