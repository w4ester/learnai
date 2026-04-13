from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import get_db, current_user
from ..models import Skill, User
from ..schemas import SkillIn, SkillOut

router = APIRouter(prefix="/api/skills", tags=["skills"])

@router.get("", response_model=list[SkillOut])
def list_skills(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Skill).filter(Skill.user_id == user.id).order_by(Skill.created_at.desc()).all()
    return [SkillOut.model_validate(r) for r in rows]

@router.post("", response_model=SkillOut, status_code=201)
def create_skill(body: SkillIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    s = Skill(
        user_id=user.id, name=body.name, triggers=body.triggers,
        system_prompt=body.system_prompt, examples=body.examples,
        output_schema=body.output_schema, token_budget=body.token_budget,
        model_min=body.model_min, enabled=body.enabled
    )
    db.add(s); db.commit()
    return SkillOut.model_validate(s)

@router.get("/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    s = db.query(Skill).filter_by(id=skill_id, user_id=user.id).first()
    if not s: raise HTTPException(404, "Not found")
    return SkillOut.model_validate(s)

@router.patch("/{skill_id}", response_model=SkillOut)
def update_skill(skill_id: str, body: SkillIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    s = db.query(Skill).filter_by(id=skill_id, user_id=user.id).first()
    if not s: raise HTTPException(404, "Not found")
    s.name = body.name
    s.triggers = body.triggers
    s.system_prompt = body.system_prompt
    s.examples = body.examples
    s.output_schema = body.output_schema
    s.token_budget = body.token_budget
    s.model_min = body.model_min
    s.enabled = body.enabled
    db.commit()
    return SkillOut.model_validate(s)

@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    s = db.query(Skill).filter_by(id=skill_id, user_id=user.id).first()
    if not s: raise HTTPException(404, "Not found")
    db.delete(s); db.commit()
