from fastapi import APIRouter, Depends
from ..services.providers import LLMProvider
from ..auth import current_user
from ..models import User
from ..schemas import ChatCompletionRequest

router = APIRouter(prefix="/api", tags=["models"])

@router.get("/models")
async def list_models():
    provider = LLMProvider()
    return await provider.list_models()

@router.post("/chat/completions")
async def chat_completions(body: ChatCompletionRequest, user: User = Depends(current_user)):
    provider = LLMProvider()
    msgs = [{"role": m.role, "content": m.content} for m in body.messages]
    return await provider.chat_completions({"model": body.model, "messages": msgs})
