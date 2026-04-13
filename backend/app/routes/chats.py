from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from ..auth import get_db, current_user
from ..models import Chat, Message, User
from ..schemas import ChatListResponse, ChatCreateRequest, ThreadResponse, AppendMessageRequest, MessageOut
from ..services.chat_service import chat_with_model

router = APIRouter(prefix="/api/chats", tags=["chats"])

@router.get("", response_model=ChatListResponse)
def list_chats(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Chat).filter(Chat.user_id==user.id).order_by(Chat.updated_at.desc()).all()
    items = [{"id": c.id, "title": c.title, "createdAt": c.created_at, "updatedAt": c.updated_at} for c in rows]
    return {"items": items}

@router.post("", response_model=dict, status_code=201)
def create_chat(body: Optional[ChatCreateRequest] = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = Chat(user_id=user.id, title=(body.title if body else None))
    db.add(c); db.commit()
    return {"id": c.id, "title": c.title}

@router.delete("/{chat_id}", status_code=204)
def delete_chat(chat_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(Chat).filter_by(id=chat_id, user_id=user.id).first()
    if not c: raise HTTPException(404, "Not found")
    db.query(Message).filter_by(chat_id=c.id).delete()
    db.delete(c); db.commit()

@router.patch("/{chat_id}", response_model=dict)
def rename_chat(chat_id: str, body: ChatCreateRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(Chat).filter_by(id=chat_id, user_id=user.id).first()
    if not c: raise HTTPException(404, "Not found")
    c.title = body.title
    db.commit()
    return {"id": c.id, "title": c.title}

@router.get("/{chat_id}", response_model=ThreadResponse)
def get_chat(chat_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(Chat).filter_by(id=chat_id, user_id=user.id).first()
    if not c: raise HTTPException(404, "Not found")
    msgs = db.query(Message).filter_by(chat_id=c.id).order_by(Message.created_at.asc()).all()
    out = [MessageOut.model_validate(m) for m in msgs]
    return {"chat": {"id": c.id, "title": c.title, "createdAt": c.created_at, "updatedAt": c.updated_at}, "messages": out}

def _title_from_message(text: str) -> str:
    """Extract first 2 to 4 words from the user message as a title."""
    words = text.strip().split()
    title = " ".join(words[:4])
    if len(title) > 40:
        title = title[:40].rsplit(" ", 1)[0]
    return title or "Chat"

@router.post("/{chat_id}/message", response_model=ThreadResponse)
async def append_message(chat_id: str, body: AppendMessageRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(Chat).filter_by(id=chat_id, user_id=user.id).first()
    if not c: raise HTTPException(404, "Not found")
    model = body.model or "llama3.1"
    if not c.title:
        c.title = _title_from_message(body.message.content)
    result = await chat_with_model(db, c, model, body.message, files=[f.model_dump() for f in (body.files or [])], profile_id=body.profile_id)
    c.updated_at = datetime.utcnow(); db.commit()
    msgs = db.query(Message).filter_by(chat_id=c.id).order_by(Message.created_at.asc()).all()
    out = [MessageOut.model_validate(m) for m in msgs]
    return {"chat": {"id": c.id, "title": c.title, "createdAt": c.created_at, "updatedAt": c.updated_at}, "messages": out}
