from fastapi import APIRouter, status

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_chat():
    return {"msg": "Created"}

@router.get("/{chat_id}", status_code=status.HTTP_200_OK)
async def get_chat(chat_id: int) -> dict:
    return {"chat_id": chat_id}

@router.put("/{chat_id}", status_code=status.HTTP_200_OK)
async def edit_chat(chat_id: int, message: str) -> dict:
    return {
        "chat_id": chat_id,
        "message": message
    }
    
@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(chat_id: int) -> dict:
    return {"msg": f"chat {chat_id} was deleted!"}