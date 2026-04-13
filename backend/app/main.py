from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routes import auth, models, chats, rag, tools, prompts, profiles, skills
from .config import settings

app = FastAPI(title=f"{settings.project_name} API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router)
app.include_router(models.router)
app.include_router(chats.router)
app.include_router(rag.router)
app.include_router(tools.router)
app.include_router(prompts.router)
app.include_router(profiles.router)
app.include_router(skills.router)
