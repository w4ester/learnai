from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..tools import REGISTRY, register_tool
from ..services.providers import LLMProvider
from ..auth import current_user, get_db
from ..models import User, Tool
from sqlalchemy.orm import Session
import json
import re
import os

router = APIRouter(prefix="/api/tools", tags=["tools"])

GENERATE_PROMPT = """You are a tool generator. Given a plain English description, create a real Python tool function.

RULES:
1. Output ONLY valid JSON with exactly these fields: name, description, schema, fn_name, code
2. The "name" should be a short snake_case identifier
3. The "schema" is a JSON Schema object with properties and required fields
4. The "fn_name" must match the function name in "code"
5. The "code" must define ONE function that takes a single dict argument "args" and returns a dict
6. You have FULL Python available. These are already imported in the runtime:
   - httpx (HTTP client — use httpx.Client() for sync requests)
   - json, math, re, os, datetime, timedelta
   - urlparse, parse_qs (from urllib.parse)
7. You CAN import additional stdlib modules inside the function if needed
8. For HTTP requests, use: client = httpx.Client(timeout=30, follow_redirects=True); resp = client.get(url)
9. The function must handle errors gracefully and return {"error": "message"} on failure
10. The function must be SYNCHRONOUS (not async)
11. IMPORTANT: NEVER require API keys. Always use free, public, no-auth approaches:
    - Scrape public web pages instead of using paid APIs
    - Use public RSS feeds, open data endpoints, or page scraping
    - Parse HTML/JSON from public pages using re or string methods
    - If no free approach exists, explain in the description that an API key is needed
12. Set follow_redirects=True and a User-Agent header for web scraping

EXAMPLE:
Description: "fetch a webpage title from a URL"
Output:
{"name":"fetch_page_title","description":"Fetch the title of a webpage","schema":{"type":"object","properties":{"url":{"type":"string","description":"The URL to fetch"}},"required":["url"]},"fn_name":"tool_fetch_page_title","code":"def tool_fetch_page_title(args):\\n    try:\\n        url = args.get('url', '')\\n        if not url.startswith('http'):\\n            url = 'https://' + url\\n        client = httpx.Client(timeout=30, follow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})\\n        resp = client.get(url)\\n        match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)\\n        title = match.group(1).strip() if match else 'No title found'\\n        return {'title': title, 'url': url, 'status': resp.status_code}\\n    except Exception as e:\\n        return {'error': str(e)}"}

Now generate a tool for this description:"""


@router.get("")
def list_tools():
    return {"items": [{"name": name, "schema": spec["schema"], "generated": spec.get("generated", False)} for name, spec in REGISTRY.items()]}


class ToolCall(BaseModel):
    name: str
    args: Dict[str, Any]


@router.post("/call")
def call_tool(body: ToolCall):
    spec = REGISTRY.get(body.name)
    if not spec:
        return {"error": "tool not found"}
    return spec["fn"](body.args)


class GenerateRequest(BaseModel):
    description: str
    model: Optional[str] = None


@router.post("/generate")
async def generate_tool(body: GenerateRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    provider = LLMProvider()
    # Always use a fast model for code generation — ignore user's selected model
    model = "qwen3:8b"

    resp = await provider.chat_completions({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise code generator. Output ONLY valid JSON. No markdown, no explanation."},
            {"role": "user", "content": f"{GENERATE_PROMPT}\n\"{body.description}\""}
        ]
    })

    raw = resp.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Extract JSON from response
    json_match = re.search(r'\{[\s\S]*\}', raw)
    if not json_match:
        raise HTTPException(400, f"Model did not return valid JSON. Raw: {raw[:500]}")

    try:
        spec = json.loads(json_match.group())
    except json.JSONDecodeError:
        raise HTTPException(400, f"Invalid JSON from model. Raw: {raw[:500]}")

    required = ["name", "schema", "fn_name", "code"]
    missing = [f for f in required if f not in spec]
    if missing:
        raise HTTPException(400, f"Missing fields: {missing}. Got: {list(spec.keys())}")

    # Try to register the tool
    try:
        register_tool(spec["name"], spec["schema"], spec["code"], spec["fn_name"])
    except Exception as e:
        raise HTTPException(400, f"Failed to compile tool: {e}")

    # Persist to DB
    db_tool = Tool(name=spec["name"], schema=spec["schema"])
    db.add(db_tool)
    db.commit()

    return {
        "name": spec["name"],
        "description": spec.get("description", ""),
        "schema": spec["schema"],
        "code": spec["code"],
    }


@router.get("/download/{file_id}")
def download_tool_output(file_id: str):
    """Serve generated tool output files (e.g. pptx from powerpoint_creator)."""
    # Basic safety: no path traversal
    if "/" in file_id or ".." in file_id:
        raise HTTPException(400, "Invalid file id")
    output_dir = "/app/storage/tool_outputs"
    filepath = os.path.join(output_dir, file_id)
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise HTTPException(404, "File not found")
    # Determine content type from extension
    media_type = "application/octet-stream"
    if file_id.endswith(".pptx"):
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif file_id.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif file_id.endswith(".pdf"):
        media_type = "application/pdf"
    # Strip the file_id prefix from the download filename
    parts = file_id.split("_", 1)
    download_name = parts[1] if len(parts) == 2 else file_id
    return FileResponse(filepath, media_type=media_type, filename=download_name)


@router.delete("/{tool_name}", status_code=204)
def delete_tool(tool_name: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if tool_name == "calculator":
        raise HTTPException(400, "Cannot delete built-in tools")
    spec = REGISTRY.get(tool_name)
    if not spec:
        raise HTTPException(404, "Tool not found")
    if not spec.get("generated"):
        raise HTTPException(400, "Cannot delete built-in tools")
    del REGISTRY[tool_name]
    db_tool = db.query(Tool).filter_by(name=tool_name).first()
    if db_tool:
        db.delete(db_tool)
        db.commit()
