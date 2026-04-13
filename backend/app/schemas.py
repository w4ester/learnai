from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Literal
from datetime import datetime

class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str = "member"
    class Config: from_attributes = True

class AuthRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    token: str
    user: UserOut

class ChatOut(BaseModel):
    id: str
    title: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    class Config: from_attributes = True

class MessageIn(BaseModel):
    role: Literal["system","user","assistant","tool"]
    content: str

class MessageOut(BaseModel):
    role: str
    content: str
    createdAt: datetime = Field(validation_alias="created_at")
    metadata: Optional[dict] = Field(default=None, validation_alias="message_metadata")

    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    items: List[ChatOut]

class ThreadResponse(BaseModel):
    chat: ChatOut
    messages: List[MessageOut]

class ChatCreateRequest(BaseModel):
    title: Optional[str] = None

class FileRef(BaseModel):
    type: Literal["file","collection"]
    id: str

class AppendMessageRequest(BaseModel):
    model: Optional[str] = None
    profile_id: Optional[str] = None
    message: MessageIn
    files: Optional[List[FileRef]] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[MessageIn]
    files: Optional[List[FileRef]] = None
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: Optional[str] = None
    model: Optional[str] = None
    choices: Optional[List[dict]] = None

class RagUploadResponse(BaseModel):
    id: str
    filename: str
    size: int

class AddFileToKnowledgeRequest(BaseModel):
    file_id: str

class PromptIn(BaseModel):
    name: str
    template: str

class PromptOut(BaseModel):
    id: str
    name: str
    template: str
    created_at: datetime
    class Config: from_attributes = True

class ModelProfileIn(BaseModel):
    name: str
    base_model: str
    system_prompt: Optional[str] = None
    params: Optional[dict] = None

class ModelProfileOut(BaseModel):
    id: str
    name: str
    base_model: str
    system_prompt: Optional[str] = None
    params: Optional[dict] = None
    created_at: datetime
    class Config: from_attributes = True

class SkillIn(BaseModel):
    name: str
    triggers: str
    system_prompt: str
    examples: Optional[list] = None
    output_schema: Optional[dict] = None
    token_budget: int = 800
    model_min: Optional[str] = "7B"
    enabled: bool = True

class SkillOut(BaseModel):
    id: str
    name: str
    triggers: str
    system_prompt: str
    examples: Optional[list] = None
    output_schema: Optional[dict] = None
    token_budget: int = 800
    model_min: Optional[str] = None
    enabled: bool = True
    created_at: datetime
    class Config: from_attributes = True

class Error(BaseModel):
    message: str
    code: Optional[str] = None
    details: Optional[dict] = None
