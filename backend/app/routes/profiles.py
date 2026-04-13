from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import get_db, current_user
from ..models import ModelProfile, User
from ..schemas import ModelProfileIn, ModelProfileOut

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

@router.get("", response_model=list[ModelProfileOut])
def list_profiles(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(ModelProfile).filter((ModelProfile.user_id == None) | (ModelProfile.user_id == user.id)).order_by(ModelProfile.created_at.desc()).all()
    return [ModelProfileOut.model_validate(r) for r in rows]

@router.post("", response_model=ModelProfileOut, status_code=201)
def create_profile(body: ModelProfileIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    mp = ModelProfile(user_id=user.id, name=body.name, base_model=body.base_model, system_prompt=body.system_prompt, params=body.params)
    db.add(mp); db.commit()
    return ModelProfileOut.model_validate(mp)

@router.get("/{profile_id}", response_model=ModelProfileOut)
def get_profile(profile_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    mp = db.query(ModelProfile).filter_by(id=profile_id).first()
    if not mp: raise HTTPException(404, "Not found")
    return ModelProfileOut.model_validate(mp)

@router.patch("/{profile_id}", response_model=ModelProfileOut)
def update_profile(profile_id: str, body: ModelProfileIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    mp = db.query(ModelProfile).filter_by(id=profile_id, user_id=user.id).first()
    if not mp: raise HTTPException(404, "Not found")
    mp.name = body.name
    mp.base_model = body.base_model
    mp.system_prompt = body.system_prompt
    mp.params = body.params
    db.commit()
    return ModelProfileOut.model_validate(mp)

@router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    mp = db.query(ModelProfile).filter_by(id=profile_id, user_id=user.id).first()
    if not mp: raise HTTPException(404, "Not found")
    db.delete(mp); db.commit()
    return {}
