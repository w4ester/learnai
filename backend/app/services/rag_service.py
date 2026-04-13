from typing import List, Tuple
import os, uuid, io
from sqlalchemy.orm import Session
from ..models import RagFile, KnowledgeCollection, KnowledgeDoc
from ..utils.chunker import split_text
from .providers import LLMProvider

FILES_DIR = "storage/files"

def _ensure_dirs():
    os.makedirs(FILES_DIR, exist_ok=True)

async def ingest_file(db: Session, user_id: str, upload_bytes: bytes, filename: str, collection_id: str | None = None) -> Tuple[RagFile, str]:
    _ensure_dirs()
    file_id = str(uuid.uuid4())
    path = os.path.join(FILES_DIR, f"{file_id}_{filename}")
    with open(path, "wb") as f:
        f.write(upload_bytes)

    rf = RagFile(id=file_id, user_id=user_id, filename=filename, path=path)
    db.add(rf)

    if not collection_id:
        collection_id = str(uuid.uuid4())
        kc = KnowledgeCollection(id=collection_id, user_id=user_id, name=f"default-{file_id[:8]}")
        db.add(kc)
        db.flush()
    else:
        kc = db.query(KnowledgeCollection).filter_by(id=collection_id, user_id=user_id).first()
        if not kc:
            raise ValueError("Collection not found or not owned by user")

    text = ""
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(upload_bytes))
            extracted_pages = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                extracted_pages.append(page_text)
            text = "\n\n".join(extracted_pages).strip()
        except Exception:
            text = ""

    if not text:
        try:
            text = upload_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    text = text.replace("\x00", "")

    chunks = split_text(text)
    provider = LLMProvider()
    if chunks:
        embeddings = await provider.embed(chunks)
    else:
        embeddings = []

    for i, chunk in enumerate(chunks):
        emb = embeddings[i] if i < len(embeddings) else None
        doc = KnowledgeDoc(collection_id=collection_id, file_id=file_id, chunk_id=i, text=chunk, embedding=emb)
        db.add(doc)

    db.commit()
    return rf, collection_id

def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    import math
    dot = sum(x*y for x, y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na==0 or nb==0: return -1.0
    return dot/(na*nb)

async def retrieve_context(db: Session, user_id: str, query: str, selectors: list[dict] | None, k: int = 5) -> str:
    provider = LLMProvider()
    q_embs = await provider.embed([query])
    q_emb = q_embs[0] if q_embs else []

    q = db.query(KnowledgeDoc)
    if selectors:
        col_ids = [s["id"] for s in selectors if s["type"]=="collection"]
        file_ids = [s["id"] for s in selectors if s["type"]=="file"]
        if col_ids:
            q = q.filter(KnowledgeDoc.collection_id.in_(col_ids))
        if file_ids:
            q = q.filter(KnowledgeDoc.file_id.in_(file_ids))

    docs = q.limit(2000).all()
    scored = []
    for d in docs:
        score = _cosine(q_emb, d.embedding or [])
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [d for _, d in scored[:k]]
    context = "\n\n".join([t.text for t in top])
    return context
