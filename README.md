# LearnAI

Learn AI by building with it. A self-hosted platform for running local AI models, chatting, uploading documents for retrieval, building tools, and creating skills — all from your own machine.

## Prerequisites

- **Docker** — [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [OrbStack](https://orbstack.dev/) (Mac)
- **Ollama** — [ollama.com](https://ollama.com/) — pull at least one model: `ollama pull gemma3:4b`

## Quick Start

```bash
git clone https://github.com/w4ester/learnai.git learnai
cd learnai
cp .env.example .env
docker compose up --build
```

Open [http://localhost:9180](http://localhost:9180). Your Ollama models appear in the model dropdown.

**Linux users:** change `OLLAMA_BASE_URL` in `.env` to `http://172.17.0.1:11434` (Docker containers on Linux cannot reach `host.docker.internal`).

## What's Inside

LearnAI has six core features — each one teaches a different AI building pattern:

| Feature | What it does | What you learn |
|---------|-------------|----------------|
| **Chat** | Talk to any local or cloud model | Basic LLM interaction, model selection |
| **RAG** | Upload documents, ask questions grounded in them | Retrieval-augmented generation, embeddings, chunking |
| **Tools** | Built-in calculator, YouTube transcripts, PowerPoint generator — plus build your own | Function calling, code generation, tool use |
| **Profiles** | Save model presets with system prompts and sampling parameters | System prompts, temperature, top_p, persona design |
| **Prompts** | Reusable text templates you can insert into any chat | Prompt engineering, template reuse |
| **Skills** | Auto-routing rules that catch keywords and reshape responses | Orchestration, keyword routing, JSON schema validation |

## Workshop

Go to **Workshops** in the sidebar for a self-paced guide: **Run AI Locally: Start to Finish** (20 min, Mac/Windows/Linux).

## Guides

Detailed setup and learning resources are in the `guides/` folder:

- `guides/setup-ollama-mac.md` — Ollama + Docker setup for Mac
- `guides/setup-ollama-linux.md` — Ollama + Docker setup for Linux
- `guides/setup-ollama-windows.md` — Ollama + Docker setup for Windows
- `guides/setup-unsloth-studio.md` — Fine-tune your own model with Unsloth, export to GGUF, run in Ollama + LearnAI

## Cloud Models (Optional)

To use OpenAI, Claude, or Gemini instead of local Ollama:

```bash
# In .env:
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

Any OpenAI-compatible API works (LiteLLM, Together, Groq, etc.).

## Stopping

```bash
docker compose down        # stop containers, keep data
docker compose down -v     # stop and delete all data (fresh start)
```
