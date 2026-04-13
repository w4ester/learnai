"""Skill routing and context injection for LearnAI.

Layer 2: Route user messages to the right skill via keyword matching.
Layer 3: Build skill context (system prompt + examples).
Layer 5: Validate output against skill schema and retry once if needed.
"""
import json
import re
from typing import Optional
from sqlalchemy.orm import Session
from ..models import Skill


def route_skill(db: Session, user_id: str, user_message: str) -> Optional[Skill]:
    """Fast-path keyword router. Scores each skill's triggers against the message."""
    skills = db.query(Skill).filter(
        Skill.user_id == user_id, Skill.enabled == True
    ).all()
    if not skills:
        return None

    msg_lower = user_message.lower()
    best_skill = None
    best_score = 0

    for skill in skills:
        triggers = [t.strip().lower() for t in str(skill.triggers).split(',')]
        score = 0
        for t in triggers:
            if not t:
                continue
            if t in msg_lower:
                # longer triggers are more specific, weight them higher
                score += len(t)
        if score > best_score:
            best_score = score
            best_skill = skill

    # Require at least one trigger match (min 3 chars matched)
    return best_skill if best_score >= 3 else None


def build_skill_context(skill: Skill) -> list[dict]:
    """Build the system messages for a matched skill."""
    messages = [{"role": "system", "content": str(skill.system_prompt)}]

    if skill.examples:
        examples = skill.examples if isinstance(skill.examples, list) else json.loads(str(skill.examples))
        for ex in examples:
            if isinstance(ex, dict) and 'user' in ex and 'assistant' in ex:
                messages.append({"role": "user", "content": ex['user']})
                messages.append({"role": "assistant", "content": ex['assistant']})

    if skill.output_schema:
        schema = skill.output_schema if isinstance(skill.output_schema, dict) else json.loads(str(skill.output_schema))
        messages[0]["content"] += f"\n\nOutput must be valid JSON matching this schema:\n{json.dumps(schema)}"

    return messages


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def validate_output(raw: str, schema: dict) -> str | bool:
    """Validate model output against a skill's JSON schema."""
    # Try to extract JSON from the response
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if not json_match:
        return "no JSON found in output"
    try:
        parsed = json.loads(json_match.group())
        for field in schema:
            if field not in parsed:
                return f"missing field: {field}"
        return True
    except json.JSONDecodeError:
        return "invalid JSON"
