<script lang="ts">
  import { afterUpdate, onDestroy } from 'svelte';
  import { get } from 'svelte/store';
  import { getChat, listProfiles, listPrompts } from '../lib/api';
  import { pendingMessage, workshopAutoSend, sendChatMessage, chatList } from '../lib/stores';
  import ChatInput from '../components/ChatInput.svelte';
  export let id: string;

  let chatTitle = '';
  let messages: Array<{ role: string; content: string; createdAt: string; metadata?: { skill?: string } }> = [];
  let loading = false;
  let error: string | null = null;
  let messagesEl: HTMLElement;

  let profiles: Array<{ id: string; name: string; base_model: string }> = [];
  let prompts: Array<{ id: string; name: string; template: string }> = [];

  // Side panel state
  let panelIdx: number | null = null;
  let copied = false;

  const PREVIEW_LEN = 120;

  // Poll the server while a message is in flight so we see intermediate
  // messages (user → tool → assistant) as the backend writes them, rather
  // than waiting for the single POST /message call to resolve. This matters
  // when the pipeline runs a skill that calls a tool — total latency can be
  // 2+ minutes on a cloud model, and without polling the UI just freezes
  // on "Processing..." the whole time.
  const POLL_INTERVAL_MS = 2500;
  const POLL_MAX_TICKS = 240; // ~10 minutes max
  let pollHandle: ReturnType<typeof setInterval> | null = null;
  let pollTicks = 0;
  let pollStartingLen = 0;

  $: panelMessage = panelIdx !== null ? messages[panelIdx] : null;

  $: if ($pendingMessage && $pendingMessage.chatId === id && !$pendingMessage.busy && $pendingMessage.resultMessages) {
    messages = $pendingMessage.resultMessages;
    pendingMessage.set(null);
  }

  $: sending = $pendingMessage?.chatId === id && $pendingMessage?.busy;

  // Start polling when sending begins, stop when it ends.
  $: if (sending && !pollHandle) startPolling();
  $: if (!sending && pollHandle) stopPolling();

  function startPolling() {
    if (pollHandle) return;
    pollTicks = 0;
    pollStartingLen = messages.length;
    pollHandle = setInterval(pollTick, POLL_INTERVAL_MS);
  }

  function stopPolling() {
    if (pollHandle) {
      clearInterval(pollHandle);
      pollHandle = null;
    }
  }

  async function pollTick() {
    pollTicks++;
    if (pollTicks > POLL_MAX_TICKS) { stopPolling(); return; }
    try {
      const res = await getChat(id);
      if (!res?.messages) return;
      if (res.messages.length > messages.length) {
        messages = res.messages;
      }
      // If the list grew past where we started AND the newest message is
      // from the assistant, the backend has finished the full pipeline
      // (user → [tool] → assistant). Clear the pending state so
      // "Processing..." disappears and the input unlocks, even if the main
      // POST fetch is still waiting to return. The starting-length guard
      // prevents a false stop on the very first tick when the previous
      // turn also ended with an assistant message.
      if (res.messages.length > pollStartingLen) {
        const last = res.messages[res.messages.length - 1];
        if (last && last.role === 'assistant') {
          const pm = get(pendingMessage);
          if (pm && pm.chatId === id) pendingMessage.set(null);
          stopPolling();
        }
      }
    } catch {}
  }

  onDestroy(stopPolling);

  // Pick up auto generated title from sidebar store
  $: {
    const entry = $chatList.find(c => c.id === id);
    if (entry?.title && chatTitle === 'Untitled Chat') chatTitle = entry.title;
  }

  async function load(chatId: string) {
    try {
      loading = true;
      error = null;
      panelIdx = null;
      const res = await getChat(chatId);
      chatTitle = res.chat.title || 'Untitled Chat';
      messages = res.messages;
      profiles = await listProfiles();
      prompts = await listPrompts();
      const pending = get(workshopAutoSend);
      if (pending && pending.chatId === chatId) {
        workshopAutoSend.set(null);
        sendChatMessage(chatId, pending.text, {});
      }
    } catch (e: any) {
      error = e?.message || 'Failed to load chat';
    } finally {
      loading = false;
    }
  }

  $: load(id);

  afterUpdate(() => {
    if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
  });

  function togglePanel(idx: number) {
    if (panelIdx === idx) {
      panelIdx = null;
    } else {
      panelIdx = idx;
      copied = false;
    }
  }

  function closePanel() {
    panelIdx = null;
    copied = false;
  }

  function needsTruncation(m: typeof messages[0]): boolean {
    return m.role === 'assistant' && m.content.length > PREVIEW_LEN;
  }

  function preview(content: string): string {
    if (content.length <= PREVIEW_LEN) return content;
    const cut = content.lastIndexOf(' ', PREVIEW_LEN);
    return content.slice(0, cut > 60 ? cut : PREVIEW_LEN) + '...';
  }

  // Detect download URLs in message content (for tool results like pptx)
  function extractDownloads(content: string): Array<{ url: string; filename: string }> {
    const matches: Array<{ url: string; filename: string }> = [];
    const re = /\/api\/tools\/download\/([A-Za-z0-9_.\-]+)/g;
    let m;
    while ((m = re.exec(content)) !== null) {
      const full = m[0];
      const id = m[1];
      const parts = id.split('_');
      const filename = parts.length > 1 ? parts.slice(1).join('_') : id;
      if (!matches.find(x => x.url === full)) {
        matches.push({ url: full, filename });
      }
    }
    return matches;
  }

  async function copyContent() {
    if (!panelMessage) return;
    try {
      await navigator.clipboard.writeText(panelMessage.content);
      copied = true;
      setTimeout(() => { copied = false; }, 2000);
    } catch {}
  }

  function downloadFile(ext: string) {
    if (!panelMessage) return;
    const type = ext === 'md' ? 'text/markdown' : 'text/plain';
    const blob = new Blob([panelMessage.content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${panelMessage.role}-${new Date(panelMessage.createdAt).toISOString().slice(0,19)}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') closePanel();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="chat-page">
  <div class="chat-main">
    <div class="chat-header">
      <h2 class="chat-title">{chatTitle}</h2>
    </div>

    <div class="chat-messages" bind:this={messagesEl}>
      {#if error}
        <div class="msg-error">{error}</div>
      {/if}

      {#each messages as m, idx}
        <div class="message {m.role}">
          <div class="msg-meta">
            <span class="badge {m.role}">{m.role}</span>
            {#if m.metadata?.skill}
              <span class="badge" style="background:var(--success-bg);color:var(--success);border-color:rgba(92,184,122,0.2);">skill:{m.metadata.skill}</span>
            {/if}
            <small class="mono">{new Date(m.createdAt + (m.createdAt.endsWith('Z') ? '' : 'Z')).toLocaleString()}</small>
          </div>

          {#if needsTruncation(m)}
            <div class="msg-content msg-preview">{preview(m.content)}</div>
            <button class="view-toggle" on:click={() => togglePanel(idx)}>
              {#if panelIdx === idx}
                ✕ Close panel
              {:else}
                ⊞ View full answer
              {/if}
            </button>
          {:else}
            <div class="msg-content">{m.content}</div>
          {/if}
          {#each extractDownloads(m.content) as dl}
            <a class="download-btn" href={dl.url} target="_blank" rel="noopener">
              <span class="download-icon">⬇</span>
              <span class="download-name">Download {dl.filename}</span>
            </a>
          {/each}
        </div>
      {/each}

      {#if sending}
        <div class="thinking-indicator">
          <div class="thinking-dots">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <span class="thinking-text">Processing...</span>
        </div>
      {/if}

      {#if messages.length === 0 && !loading && !sending}
        <div class="chat-welcome">
          <h1 class="welcome-heading">How can I help?</h1>
          <p class="welcome-sub">Send a message to start the conversation.</p>
        </div>
      {/if}
    </div>

    <ChatInput chatId={id} {profiles} {prompts} />
  </div>

  {#if panelMessage}
    <div class="answer-panel">
      <div class="answer-panel-header">
        <span class="badge {panelMessage.role}">{panelMessage.role}</span>
        <small class="mono">{new Date(panelMessage.createdAt + (panelMessage.createdAt.endsWith('Z') ? '' : 'Z')).toLocaleString()}</small>
        <div class="answer-panel-spacer"></div>
        <button class="answer-panel-btn" on:click={copyContent}>
          {copied ? 'Copied!' : 'Copy'}
        </button>
        <button class="answer-panel-btn" on:click={() => downloadFile('txt')}>.txt</button>
        <button class="answer-panel-btn" on:click={() => downloadFile('md')}>.md</button>
        <button class="answer-panel-close" on:click={closePanel}>&times;</button>
      </div>
      <div class="answer-panel-content">{panelMessage.content}</div>
    </div>
  {/if}
</div>

<style>
  .chat-page {
    display: flex;
    height: 100vh;
  }

  .chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .chat-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-light);
    flex-shrink: 0;
  }
  .chat-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.15rem;
    font-weight: 400;
    margin: 0;
    color: var(--text);
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .message {
    border-radius: 10px;
    padding: 12px 16px;
  }

  .msg-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }
  .msg-content {
    white-space: pre-wrap;
    line-height: 1.7;
    font-size: 0.92rem;
    word-break: break-word;
    overflow-wrap: break-word;
  }

  .download-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 10px;
    padding: 10px 16px;
    background: var(--brand);
    color: #fff;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.15s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
  .download-btn:hover {
    background: var(--brand-light);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    color: #fff;
  }
  .download-icon {
    font-size: 1rem;
  }
  .msg-preview {
    color: var(--text-secondary);
  }

  /* View full answer / Close panel toggle */
  .view-toggle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    padding: 0;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--gold-light);
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
    transition: color 0.15s;
  }
  .view-toggle:hover {
    color: var(--brand);
  }

  .chat-welcome {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 20px;
  }
  .welcome-heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.8rem;
    font-weight: 400;
    color: var(--text);
    margin-bottom: 8px;
  }
  .welcome-sub {
    color: var(--text-muted);
    font-size: 0.95rem;
  }

  .thinking-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    border-radius: 10px;
    background: var(--gold-bg);
    border-left: 3px solid var(--gold);
  }
  .thinking-text {
    color: var(--text-secondary);
    font-size: 0.88rem;
    font-style: italic;
  }
  .thinking-dots {
    display: flex;
    gap: 4px;
    align-items: center;
  }
  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--gold);
    animation: pulse 1.4s ease-in-out infinite;
  }
  .dot:nth-child(2) { animation-delay: 0.2s; }
  .dot:nth-child(3) { animation-delay: 0.4s; }
  @keyframes pulse {
    0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1); }
  }

  /* ── Answer Side Panel ── */
  .answer-panel {
    width: 440px;
    flex-shrink: 0;
    border-left: 1.5px solid var(--border);
    background: var(--card);
    display: flex;
    flex-direction: column;
    height: 100vh;
    animation: panelSlideIn 0.2s ease;
  }
  @keyframes panelSlideIn {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }

  .answer-panel-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-light);
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .answer-panel-spacer { flex: 1; }

  .answer-panel-btn {
    padding: 5px 12px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--card-alt);
    color: var(--text);
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.15s;
  }
  .answer-panel-btn:hover {
    background: var(--bg-warm);
    border-color: var(--border-strong);
  }

  .answer-panel-close {
    width: 30px;
    height: 30px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-size: 1.2rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
    font-family: inherit;
    margin-left: 4px;
  }
  .answer-panel-close:hover {
    background: var(--danger-bg);
    color: var(--brand);
  }

  .answer-panel-content {
    padding: 20px 24px;
    overflow-y: auto;
    flex: 1;
    white-space: pre-wrap;
    line-height: 1.75;
    font-size: 0.92rem;
    color: var(--text);
  }

  /* ── Mobile ── */
  @media (max-width: 768px) {
    .chat-page { height: calc(100vh - 48px); }
    .chat-header { padding: 12px 16px; }
    .chat-messages { padding: 12px; gap: 8px; }
    .message { padding: 8px 12px; }
    .welcome-heading { font-size: 1.3rem; }

    .answer-panel {
      position: fixed;
      inset: 0;
      width: 100%;
      z-index: 450;
      border-left: none;
      animation: mobileSlideUp 0.2s ease;
    }
    @keyframes mobileSlideUp {
      from { opacity: 0; transform: translateY(100%); }
      to { opacity: 1; transform: translateY(0); }
    }
    .answer-panel-header { gap: 6px; padding: 14px 16px; }
    .answer-panel-content { padding: 14px 16px; font-size: 0.9rem; }
    .answer-panel-btn { padding: 8px 14px; font-size: 0.78rem; min-height: 36px; }
    .msg-content { font-size: 0.9rem; }
    .view-toggle { padding: 8px 14px; font-size: 0.8rem; min-height: 36px; }
  }
</style>
