from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..auth import get_db, current_user
from ..models import User, RagFile, KnowledgeDoc
from ..schemas import RagUploadResponse, AddFileToKnowledgeRequest
from ..services.rag_service import ingest_file
import os

router = APIRouter(prefix="/api/rag", tags=["rag"])

@router.get("/files")
def list_files(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(RagFile).filter(RagFile.user_id == user.id).order_by(RagFile.created_at.desc()).all()
    return {"items": [{"id": r.id, "filename": r.filename, "size": os.path.getsize(r.path) if os.path.exists(r.path) else 0} for r in rows]}

@router.post("/files", response_model=RagUploadResponse, status_code=201)
async def upload_file(file: UploadFile = File(...), collection_id: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")
    rag_file, col = await ingest_file(db, user.id, content, file.filename, collection_id=collection_id)
    return {"id": rag_file.id, "filename": rag_file.filename, "size": len(content)}

@router.delete("/files/{file_id}", status_code=204)
def delete_file(file_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    f = db.query(RagFile).filter_by(id=file_id, user_id=user.id).first()
    if not f: raise HTTPException(404, "Not found")
    db.query(KnowledgeDoc).filter_by(file_id=f.id).delete()
    if os.path.exists(f.path):
        os.remove(f.path)
    db.delete(f); db.commit()

@router.delete("/files", status_code=204)
def delete_all_files(db: Session = Depends(get_db), user: User = Depends(current_user)):
    files = db.query(RagFile).filter(RagFile.user_id == user.id).all()
    for f in files:
        db.query(KnowledgeDoc).filter_by(file_id=f.id).delete()
        if os.path.exists(f.path):
            os.remove(f.path)
        db.delete(f)
    db.commit()
