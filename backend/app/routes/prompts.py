from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import get_db, current_user
from ..models import Prompt, User
from ..schemas import PromptIn, PromptOut

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

@router.get("", response_model=list[PromptOut])
def list_prompts(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Prompt).filter((Prompt.user_id == None) | (Prompt.user_id == user.id)).order_by(Prompt.created_at.desc()).all()
    return [PromptOut.model_validate(r) for r in rows]

@router.post("", response_model=PromptOut, status_code=201)
def create_prompt(body: PromptIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = Prompt(user_id=user.id, name=body.name, template=body.template)
    db.add(p); db.commit()
    return PromptOut.model_validate(p)

@router.delete("/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Prompt).filter_by(id=prompt_id, user_id=user.id).first()
    if not p: raise HTTPException(404, "Not found")
    db.delete(p); db.commit()
    return {}
