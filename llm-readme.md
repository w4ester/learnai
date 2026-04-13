# LLM Setup Guide for LearnAI

> **For the attendee:** Paste this entire document into Claude, ChatGPT, or any AI assistant and say:
> "Help me set up LearnAI on my machine using these instructions."
> The AI will ask you questions and walk you through it step by step.

> **For the AI assistant reading this:** You are helping someone set up LearnAI for the first time. They may have never used Docker, Ollama, or the command line before. Be patient. Go one step at a time. Ask them to confirm each step worked before moving to the next. Celebrate small wins. If something fails, ask them to paste the exact error message.

---

## What is LearnAI?

LearnAI is a self-hosted AI platform that runs on your own machine. It lets you:
- Chat with AI models running locally (no data leaves your computer)
- Upload documents and ask questions about them (RAG)
- Build custom tools that the AI can call
- Create model presets (Profiles) with different personalities and settings
- Save reusable prompt templates
- Set up auto-routing rules (Skills) that trigger on keywords

The repo is at: https://github.com/w4ester/learnai

## Setup assistant instructions

Follow this sequence. Ask the user about their situation BEFORE giving commands. Do not dump all steps at once.

### Step 0: Ask about their operating system

Ask: "What operating system are you on? Mac, Windows, or Linux?"

This determines which Docker and Ollama instructions to give. Do not proceed until you know the OS.

### Step 1: Install Ollama

Ollama runs AI models locally on the user's machine.

**Mac:**
- Option A (recommended): `brew install ollama` if they have Homebrew
- Option B: Download from https://ollama.com/download/mac
- Option C: `curl -fsSL https://ollama.com/install.sh | sh`
- After install: `ollama serve` starts the server (or it may auto-start)
- Verify: `curl http://localhost:11434` should return "Ollama is running"

**Windows:**
- Download the installer from https://ollama.com/download/windows
- Run the installer (no admin required for most setups)
- Ollama starts automatically as a system tray app
- Verify: Open PowerShell, run `curl http://localhost:11434`

**Linux:**
- `curl -fsSL https://ollama.com/install.sh | sh`
- This installs Ollama and sets up a systemd service
- Verify: `systemctl status ollama` then `curl http://localhost:11434`

**After Ollama is running, pull a model:**
```
ollama pull gemma3:4b
```
This downloads a small, fast model (~2.5 GB). It will take a few minutes depending on internet speed. Any model from https://ollama.com/library works.

Ask the user to confirm: "Did `curl http://localhost:11434` return 'Ollama is running'? And did the model pull complete?"

### Step 2: Install Docker

Docker runs the LearnAI platform (database, API server, web interface) in containers.

**Mac:**
- Option A: Docker Desktop from https://www.docker.com/products/docker-desktop/
- Option B (recommended for Mac): OrbStack from https://orbstack.dev/ (lighter, faster, Mac-only)
- After install, open the app once to finish setup
- Verify: `docker --version` should print a version number

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop/
- IMPORTANT: During install, make sure "Use WSL 2 based engine" is checked
- If WSL2 is not installed: open PowerShell as Administrator, run `wsl --install`, restart
- After install, open Docker Desktop once to finish setup
- Verify: `docker --version` in PowerShell

**Linux:**
- Ubuntu/Debian: `sudo apt update && sudo apt install docker.io docker-compose-plugin`
- Fedora: `sudo dnf install docker docker-compose-plugin`
- After install: `sudo usermod -aG docker $USER` then log out and back in
- Verify: `docker --version` (without sudo)

Ask the user to confirm: "Does `docker --version` work?"

### Step 3: Clone the repo and start LearnAI

```bash
git clone https://github.com/w4ester/learnai.git
cd learnai
cp .env.example .env
```

**IMPORTANT for Linux users:** Before starting, edit the `.env` file and change:
```
OLLAMA_BASE_URL=http://host.docker.internal:11434
```
to:
```
OLLAMA_BASE_URL=http://172.17.0.1:11434
```
This is because Docker containers on Linux cannot reach `host.docker.internal`. The address `172.17.0.1` is the Docker bridge gateway that routes to the host.

Mac and Windows users do NOT need to change anything.

Now start the platform:
```bash
docker compose up --build
```

This will:
1. Build the backend (Python/FastAPI) container
2. Build the frontend (Svelte/nginx) container
3. Start a PostgreSQL database
4. Connect everything together

First build takes 2-5 minutes. Subsequent starts are much faster.

When you see all three services show "healthy" or "started", the platform is ready.

Ask the user to confirm: "Do you see output from `docker compose up --build` showing the containers starting? Any errors?"

### Step 4: Open LearnAI

Open a web browser and go to: http://localhost:9180

The user should see the LearnAI welcome page with a sidebar showing: RAG, Tools, Profiles, Prompts, Skills, Workshops.

Ask them: "Do you see the LearnAI welcome page? What does it look like?"

### Step 5: First chat

1. Click "+ New Chat" in the sidebar
2. Type a message like "Hello, what model are you?"
3. If the message gets a response, the full stack is working: browser → nginx → FastAPI → Ollama → back

If no models appear in the dropdown:
- Make sure Ollama is running: `curl http://localhost:11434`
- Make sure at least one model is pulled: `ollama list`
- Try restarting: `docker compose restart api`

### Step 6: Explore

After the first successful chat, suggest these next steps:
1. **Workshops** — Click "Workshops" in the sidebar. Follow "Run AI Locally: Start to Finish" for a guided 20-minute tour of every feature.
2. **Profiles** — Click "Profiles" and try a preset card (Quick Chat, Creative Writer, etc.)
3. **RAG** — Click "RAG", upload any text file or PDF, then start a chat and ask questions about it
4. **Tools** — Click "Tools" and try the calculator or YouTube transcript tool

## Troubleshooting reference

Provide this information ONLY when the user reports a specific error. Do not preemptively dump troubleshooting steps.

### "Models don't appear in the dropdown"
- Is Ollama running? `curl http://localhost:11434`
- Is at least one model pulled? `ollama list`
- Is the OLLAMA_BASE_URL correct in .env?
  - Mac/Windows: `http://host.docker.internal:11434`
  - Linux: `http://172.17.0.1:11434`
- Restart the API container: `docker compose restart api`

### "Cannot connect to Docker daemon"
- Is Docker Desktop / OrbStack running? Open the app.
- On Linux: `sudo systemctl start docker`
- On Linux: did you add yourself to the docker group? `groups` should show `docker`

### "Port 9180 already in use"
- Something else is using that port. Either stop it or change the port in docker-compose.yml:
  ```yaml
  ports:
    - "127.0.0.1:9280:80"  # change 9180 to any free port
  ```
  Then use `http://localhost:9280` instead.

### "OLLAMA_BASE_URL connection refused" (Linux only)
- Try: `OLLAMA_BASE_URL=http://172.17.0.1:11434` in .env
- If that doesn't work: check if Ollama is listening on all interfaces:
  ```bash
  sudo systemctl edit ollama
  # Add: Environment="OLLAMA_HOST=0.0.0.0"
  sudo systemctl restart ollama
  ```

### "docker compose: command not found"
- Older Docker versions use `docker-compose` (with hyphen) instead of `docker compose` (with space)
- Try: `docker-compose up --build`
- Or update Docker to get the modern `docker compose` plugin

### Stopping and restarting
```bash
docker compose down          # stop everything, keep data
docker compose up -d         # start in background (after first build)
docker compose down -v       # stop and DELETE all data (fresh start)
```

## Platform architecture (for context, not for the user)

The AI assistant reading this should understand the stack but does NOT need to explain it to the user unless asked:

- **learnai-web** (nginx container, port 80 inside → 9180 on host): serves the Svelte frontend as static files, proxies /api/* to the backend
- **learnai-api** (FastAPI/Uvicorn container, port 8080): handles all API routes, calls Ollama for LLM inference, manages database
- **learnai-db** (PostgreSQL 16 + pgvector container, port 5432): stores chats, users, skills, profiles, prompts, RAG embeddings
- **Ollama** (runs on the HOST machine, not in Docker): serves AI models via HTTP API on port 11434

The frontend calls the backend via nginx reverse proxy. The backend calls Ollama via HTTP. The database stores everything. All traffic stays on localhost.

## What the user should NOT need to do

- Create any accounts (noauth mode — no login required)
- Get API keys (Ollama is free and local)
- Edit any code (everything works out of the box)
- Understand Docker internals (they just need `docker compose up --build`)
- Configure networking (defaults handle Mac/Windows; Linux needs one env var change)

## Tone guidance for the AI assistant

- Be encouraging. "Nice, Ollama is running!" not just "Proceed to step 2."
- Go one step at a time. Wait for confirmation before moving on.
- If they paste an error, match it against the troubleshooting section before guessing.
- If you don't know the answer, say so and suggest they open an issue on the GitHub repo.
- Remember: many attendees are trying local AI for the first time. This might be their first time using the terminal, Docker, or git. Meet them where they are.
