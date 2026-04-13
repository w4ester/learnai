import httpx
from typing import List, Dict, Any, Optional
from ..config import settings

def _filter_visible(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    allowed = [m.strip() for m in settings.visible_models.split(",") if m.strip()]
    if not allowed:
        return models
    return [m for m in models if m.get("id") in allowed]

class LLMProvider:
    async def list_models(self) -> Dict[str, Any]:
        if settings.model_provider == "ollama":
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(f"{settings.ollama_base_url}/api/tags")
                r.raise_for_status()
                data = r.json()
                models = [{"id": m.get("name")} for m in data.get("models", [])]
                return {"data": _filter_visible(models)}
        elif settings.model_provider == "openai":
            headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
            async with httpx.AsyncClient(timeout=30, headers=headers) as client:
                r = await client.get("https://api.openai.com/v1/models")
                r.raise_for_status()
                data = r.json()
                models = [{"id": m.get("id")} for m in data.get("data", [])]
                return {"data": _filter_visible(models)}
        return {"data": []}

    async def chat_completions(self, body: Dict[str, Any]) -> Dict[str, Any]:
        messages = body.get("messages", [])
        # Provider-specific call
        if settings.model_provider == "ollama":
            payload = {"model": body["model"], "messages": messages, "stream": False}
            opts = body.get("params")
            if opts:
                payload["options"] = opts
            async with httpx.AsyncClient(timeout=300) as client:
                r = await client.post(f"{settings.ollama_base_url}/api/chat", json=payload)
                r.raise_for_status()
                data = r.json()
                content = data.get("message", {}).get("content", "")
                return {"choices":[{"message":{"role":"assistant","content":content}}]}
        elif settings.model_provider == "openai":
            headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
            async with httpx.AsyncClient(timeout=120, headers=headers) as client:
                r = await client.post("https://api.openai.com/v1/chat/completions", json=body)
                r.raise_for_status()
                return r.json()
        return {"choices":[{"message":{"role":"assistant","content":"No provider configured."}}]}

    async def embed(self, texts: List[str]) -> List[List[float]]:
        if settings.model_provider == "ollama":
            model = "embeddinggemma:latest"
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(f"{settings.ollama_base_url}/api/embeddings", json={"model": model, "input": texts})
                r.raise_for_status()
                data = r.json()
                if "embeddings" in data:
                    return data["embeddings"]
                if "embedding" in data:
                    return [data["embedding"]]
                return []
        elif settings.model_provider == "openai":
            headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
            body = {"model": "text-embedding-3-small", "input": texts}
            async with httpx.AsyncClient(timeout=120, headers=headers) as client:
                r = await client.post("https://api.openai.com/v1/embeddings", json=body)
                r.raise_for_status()
                data = r.json()
                return [d["embedding"] for d in data.get("data", [])]
        return []
