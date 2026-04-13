from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime
import uuid

from .db import Base


def uuid4_str():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uuid4_str)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    role = Column(String, nullable=False, default="member")  # member|admin
    provider = Column(String, nullable=True)
    provider_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chats = relationship("Chat", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(String, primary_key=True, default=uuid4_str)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=uuid4_str)
    chat_id = Column(String, ForeignKey("chats.id"), index=True, nullable=False)
    role = Column(String, nullable=False)  # system|user|assistant|tool
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column(JSON, nullable=True)

    chat = relationship("Chat", back_populates="messages")


class RagFile(Base):
    __tablename__ = "rag_files"
    id = Column(String, primary_key=True, default=uuid4_str)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeCollection(Base):
    __tablename__ = "knowledge_collections"
    id = Column(String, primary_key=True, default=uuid4_str)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"
    id = Column(String, primary_key=True, default=uuid4_str)
    collection_id = Column(
        String, ForeignKey("knowledge_collections.id"), index=True, nullable=False
    )
    file_id = Column(String, ForeignKey("rag_files.id"), nullable=True)
    chunk_id = Column(Integer, nullable=False, default=0)
    text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(String, primary_key=True, default=uuid4_str)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=True)
    name = Column(String, nullable=False)
    template = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelProfile(Base):
    __tablename__ = "model_profiles"
    id = Column(String, primary_key=True, default=uuid4_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    base_model = Column(String, nullable=False)  # e.g., llama3.1
    system_prompt = Column(Text, nullable=True)
    params = Column(JSON, nullable=True)  # temperature, top_p, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


class Skill(Base):
    __tablename__ = "skills"
    id = Column(String, primary_key=True, default=uuid4_str)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    triggers = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    examples = Column(JSON, nullable=True)
    output_schema = Column(JSON, nullable=True)
    token_budget = Column(Integer, nullable=False, default=800)
    model_min = Column(String, nullable=True, default="7B")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Tool(Base):
    __tablename__ = "tools"
    id = Column(String, primary_key=True, default=uuid4_str)
    name = Column(String, unique=True, nullable=False)
    schema = Column(JSON, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
