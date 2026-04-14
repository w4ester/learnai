<script lang="ts">
  import { createChat } from '../lib/api';
  import { workshopAutoSend } from '../lib/stores';

  let open = [false];
  let launching = -1;

  function toggle(i: number) {
    open[i] = !open[i];
    open = open;
  }

  async function sendPrompt(i: number, text: string) {
    if (launching >= 0) return;
    try {
      launching = i;
      const res = await createChat('Workshop Setup Help');
      workshopAutoSend.set({ chatId: res.id, text });
      window.location.hash = '/chat/' + res.id;
    } catch {}
    finally { launching = -1; }
  }
</script>

<div class="workshops">
  <div class="header">
    <h1>Workshops</h1>
    <p class="subtitle">Self paced workshops for building with AI. Pick one and start building.</p>
  </div>

  <div class="sessions">
    <div class="session s0" class:open={open[0]}>
      <button class="session-header" on:click={() => toggle(0)}>
        <div class="num p0">01</div>
        <div class="session-info">
          <div class="session-title">Run AI Locally: Start to Finish</div>
          <div class="session-subtitle">Self paced · 20 min · Mac, Windows, Linux</div>
        </div>
        <div class="chevron" class:rotated={open[0]}>&#9654;</div>
      </button>
      {#if open[0]}
        <div class="session-body">
          <div class="section">
            <div class="section-label">Two paths</div>
            <div class="pills">
              <span class="pill p0">Path A: Local models (Ollama)</span>
              <span class="pill p0">Path B: Cloud models (API key)</span>
            </div>
          </div>
          <div class="section">
            <div class="section-label">Path A: Local with Ollama (Mac)</div>
            <div class="outcome"><div class="dot"></div>Install Ollama. Three options on ollama.com: curl script (recommended), Mac app download, or brew install ollama</div>
            <div class="outcome"><div class="dot"></div>Curl: curl -fsSL https://ollama.com/install.sh | sh</div>
            <div class="outcome"><div class="dot"></div>Verify: curl http://localhost:11434 shows Ollama is running</div>
            <div class="outcome"><div class="dot"></div>Pull a model: ollama pull (pick any model from ollama.com/library)</div>
            <div class="outcome"><div class="dot"></div>Install Docker Desktop (docker.com)</div>
            <div class="outcome"><div class="dot"></div>Clone repo, cp .env.example .env, docker compose up --build</div>
            <div class="outcome"><div class="dot"></div>Open localhost:9180. Your models appear in the dropdown.</div>
          </div>
          <div class="section">
            <div class="section-label">Path A: Local with Ollama (Windows)</div>
            <div class="outcome"><div class="dot"></div>Install Ollama for Windows from ollama.com (native installer, no WSL needed for Ollama itself)</div>
            <div class="outcome"><div class="dot"></div>Verify: curl http://localhost:11434 in PowerShell shows Ollama is running</div>
            <div class="outcome"><div class="dot"></div>Pull a model: ollama pull (same as Mac)</div>
            <div class="outcome"><div class="dot"></div>Enable WSL2 for Docker: PowerShell as admin, wsl --install, restart</div>
            <div class="outcome"><div class="dot"></div>Install Docker Desktop (check "Use WSL 2 based engine")</div>
            <div class="outcome"><div class="dot"></div>Clone, copy .env, docker compose up --build, open localhost:9180</div>
            <div class="outcome"><div class="dot"></div>If models do not show: change OLLAMA_BASE_URL to http://localhost:11434 in .env</div>
          </div>
          <div class="section">
            <div class="section-label">Path A: Local with Ollama (Linux)</div>
            <div class="outcome"><div class="dot"></div>Install Ollama: curl -fsSL https://ollama.com/install.sh | sh (official script, sets up systemd service)</div>
            <div class="outcome"><div class="dot"></div>Verify: systemctl status ollama, then curl http://localhost:11434</div>
            <div class="outcome"><div class="dot"></div>Pull a model: ollama pull (pick any from ollama.com/library)</div>
            <div class="outcome"><div class="dot"></div>Install Docker: sudo apt install docker.io docker-compose-plugin (or dnf/pacman)</div>
            <div class="outcome"><div class="dot"></div>Add yourself to docker group: sudo usermod -aG docker $USER (log out and back in)</div>
            <div class="outcome"><div class="dot"></div>Clone, cp .env.example .env, change OLLAMA_BASE_URL to http://172.17.0.1:11434</div>
            <div class="outcome"><div class="dot"></div>docker compose up --build, open localhost:9180</div>
          </div>
          <div class="section">
            <div class="section-label">Path B: Cloud models (no GPU needed)</div>
            <div class="outcome"><div class="dot"></div>Install Docker only. No Ollama needed.</div>
            <div class="outcome"><div class="dot"></div>Edit .env: MODEL_PROVIDER=openai and set your API key</div>
            <div class="outcome"><div class="dot"></div>Works with OpenAI, Claude (via LiteLLM), and Gemini (OpenAI compatible mode)</div>
            <div class="outcome"><div class="dot"></div>docker compose up --build, open localhost:9180. Cloud models appear in dropdown.</div>
          </div>
          <div class="section">
            <div class="section-label">After setup: first 5 minutes</div>
            <div class="outcome"><div class="dot"></div>Start a chat and send a message</div>
            <div class="outcome"><div class="dot"></div>Create a profile with a preset card</div>
            <div class="outcome"><div class="dot"></div>Upload a document for RAG and ask a question about it</div>
            <div class="outcome"><div class="dot"></div>Try the calculator or YouTube transcript tool</div>
          </div>
          <div class="section cta-section">
            <button class="cta p0" disabled={launching >= 0} on:click={() => sendPrompt(0, 'Walk me through setting up Ollama on my machine step by step. I am new to this. Ask me what OS I am on first, then give me one step at a time and wait for me to confirm before moving to the next.')}>
              {launching === 0 ? 'Opening...' : 'Get setup help &#8599;'}
            </button>
            <a class="cta-ghost" href="/guides/ollama-setup-guide.pdf" download>
              &#11015; Download PDF guide (Mac · Windows · Linux)
            </a>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .workshops { padding: 0; }
  .header {
    margin-bottom: 28px;
  }
  .header h1 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.6rem;
    font-weight: 400;
    color: var(--text);
    margin: 0 0 6px;
  }
  .subtitle {
    color: var(--text-muted);
    font-size: 0.88rem;
    margin: 0;
  }

  .sessions {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .session {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    transition: border-color 0.2s;
  }
  .session.open { border-color: var(--brand-border); }

  .session-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 18px;
    width: 100%;
    background: transparent;
    border: none;
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    color: var(--text);
  }

  .num {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
    font-weight: 700;
    flex-shrink: 0;
    color: #fff;
  }
  .num.p0 { background: var(--brand); }

  .session-info { flex: 1; min-width: 0; }
  .session-title { font-size: 0.95rem; font-weight: 600; }
  .session-subtitle { font-size: 0.78rem; color: var(--text-muted); margin-top: 2px; }

  .chevron {
    font-size: 0.7rem;
    color: var(--text-muted);
    transition: transform 0.2s;
    flex-shrink: 0;
  }
  .chevron.rotated { transform: rotate(90deg); }

  .session-body {
    padding: 4px 18px 18px;
    border-top: 1px solid var(--border);
  }

  .section { margin-top: 18px; }
  .section-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 8px;
  }

  .pills { display: flex; flex-wrap: wrap; gap: 6px; }
  .pill {
    font-size: 0.78rem;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 500;
  }
  .pill.p0 { background: var(--brand-bg); color: var(--brand-light); border: 1px solid var(--brand-border); }

  .outcome {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    font-size: 0.88rem;
    color: var(--text);
    line-height: 1.5;
  }
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--brand);
    flex-shrink: 0;
    margin-top: 8px;
  }

  .cta-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 24px;
  }
  .cta {
    padding: 12px 20px;
    border-radius: 8px;
    border: none;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.15s;
    text-align: center;
  }
  .cta.p0 { background: var(--brand); color: #fff; }
  .cta.p0:hover { background: var(--brand-light); }
  .cta:disabled { opacity: 0.6; cursor: not-allowed; }

  .cta-ghost {
    display: block;
    text-align: center;
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.82rem;
    text-decoration: none;
    transition: all 0.15s;
  }
  .cta-ghost:hover {
    border-color: var(--brand-border);
    color: var(--brand-light);
    background: var(--brand-bg);
  }

  @media (max-width: 768px) {
    .session-header { padding: 14px; gap: 10px; }
    .session-body { padding: 4px 14px 14px; }
    .outcome { font-size: 0.84rem; }
  }
</style>
