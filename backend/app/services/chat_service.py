from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json, re
from ..models import Chat, Message, ModelProfile
from ..schemas import MessageIn
from .providers import LLMProvider
from .rag_service import retrieve_context
from .skill_router import route_skill, build_skill_context, validate_output
from ..tools import REGISTRY as TOOLS

TOOL_BLOCK_RE = re.compile(r"```tool\s*(\{[\s\S]*?\})\s*```", re.MULTILINE)

DEFAULT_SYSTEM_PROMPT = (
    "Write in clear, plain language that humans can easily read. "
    "Do not use markdown formatting — no headers, bullet points, bold, "
    "italic, code blocks, or numbered lists — unless the user specifically "
    "asks for markdown or formatted output. Use natural paragraphs and "
    "conversational sentences. Keep responses concise and direct."
)


def _apply_profile(
    db: Session, messages: List[dict], profile_id: Optional[str]
) -> dict:
    params = None
    model = None
    has_system_prompt = False
    if profile_id:
        prof = db.query(ModelProfile).filter_by(id=profile_id).first()
        if prof:
            model = prof.base_model
            if prof.system_prompt:
                has_system_prompt = True
                messages = [
                    {"role": "system", "content": prof.system_prompt}
                ] + messages
            params = prof.params or None
    # Always prepend a default plain-text instruction when no profile
    # provides its own system prompt
    if not has_system_prompt:
        messages = [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT}
        ] + messages
    return {"messages": messages, "model": model, "params": params}


def _maybe_call_tool(assistant_text: str) -> Optional[dict]:
    m = TOOL_BLOCK_RE.search(assistant_text or "")
    if not m:
        return None
    try:
        spec = json.loads(m.group(1))
        name = spec.get("tool") or spec.get("name")
        args = spec.get("args", {})
        return {"name": name, "args": args}
    except Exception:
        return None


async def chat_with_model(
    db: Session,
    chat: Chat,
    model: str,
    user_msg: MessageIn,
    files: Optional[List[dict]] = None,
    profile_id: Optional[str] = None,
) -> Dict[str, Any]:
    # Save user message
    m_user = Message(chat_id=chat.id, role=user_msg.role, content=user_msg.content)
    db.add(m_user)
    db.flush()

    # Build messages from history
    msgs = [
        {"role": m.role, "content": m.content}
        for m in db.query(Message)
        .filter_by(chat_id=chat.id)
        .order_by(Message.created_at.asc())
        .all()
    ]

    # RAG augmentation
    if files:
        context = await retrieve_context(
            db, user_id=chat.user_id, query=user_msg.content, selectors=files, k=5
        )
        if context:
            msgs = [
                {
                    "role": "system",
                    "content": "Use the provided CONTEXT. If insufficient, say so.",
                },
                {"role": "system", "content": f"CONTEXT:\n{context}"},
            ] + msgs

    # Skill routing (Layer 2+3)
    matched_skill = route_skill(db, chat.user_id, user_msg.content)
    if matched_skill:
        skill_msgs = build_skill_context(matched_skill)
        msgs = skill_msgs + msgs
        # Store which skill was used in the user message metadata
        m_user.message_metadata = {"skill": str(matched_skill.name)}
        db.flush()

    # Apply model profile (system prompt + params)
    profile_applied = _apply_profile(db, msgs, profile_id)
    msgs = profile_applied["messages"]
    params = profile_applied["params"]
    if profile_applied["model"]:
        model = profile_applied["model"]

    provider = LLMProvider()
    resp = await provider.chat_completions(
        {"model": model, "messages": msgs, "params": params}
    )
    content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Output validation (Layer 5) — if skill has a schema, validate and retry once
    if matched_skill and matched_skill.output_schema:
        schema = matched_skill.output_schema if isinstance(matched_skill.output_schema, dict) else json.loads(str(matched_skill.output_schema))
        result = validate_output(content, schema)
        if result is not True:
            retry_msgs = msgs + [
                {"role": "assistant", "content": content},
                {"role": "user", "content": f"Your output failed validation: {result}. Try again, output ONLY valid JSON."},
            ]
            resp2 = await provider.chat_completions(
                {"model": model, "messages": retry_msgs, "params": params}
            )
            content = resp2.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Tool calling (one-shot)
    tool_req = _maybe_call_tool(content)
    if tool_req:
        spec = TOOLS.get(tool_req["name"])
        tool_result = {"error": "tool not found"}
        if spec:
            try:
                tool_result = spec["fn"](tool_req["args"])
            except Exception as e:
                tool_result = {"error": str(e)}
        # Save tool message
        m_tool = Message(
            chat_id=chat.id,
            role="tool",
            content=json.dumps({"tool": tool_req["name"], "result": tool_result}),
        )
        db.add(m_tool)
        db.flush()

        # Re-ask with tool result appended
        msgs2 = msgs + [
            {"role": "assistant", "content": content},
            {"role": "tool", "content": json.dumps(tool_result)},
        ]
        resp2 = await provider.chat_completions(
            {"model": model, "messages": msgs2, "params": params}
        )
        content = resp2.get("choices", [{}])[0].get("message", {}).get("content", "")

    m_assistant = Message(chat_id=chat.id, role="assistant", content=content)
    db.add(m_assistant)
    db.commit()

    # Rebuild thread
    msgs_out = [
        {
            "role": m.role,
            "content": m.content,
            "createdAt": m.created_at,
            "metadata": m.message_metadata,
        }
        for m in db.query(Message)
        .filter_by(chat_id=chat.id)
        .order_by(Message.created_at.asc())
        .all()
    ]
    return {
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "messages": msgs_out,
    }
