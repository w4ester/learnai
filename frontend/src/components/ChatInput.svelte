<script lang="ts">
  import { listModels, listRagFiles } from '../lib/api';
  import { selectedModel, modelList, pendingMessage, sendChatMessage } from '../lib/stores';
  import { activeFileIds, ragFiles, toggleFileActive } from '../lib/rag';
  import { currentTheme } from '../lib/theme';
  import { clickOutside } from '../lib/actions';
  import { onMount } from 'svelte';

  export let chatId: string;
  export let profiles: Array<{ id: string; name: string; base_model: string }> = [];
  export let prompts: Array<{ id: string; name: string; template: string }> = [];

  let input = '';
  let showControls = false;

  let profileId = '';
  let promptId = '';
  let useRag = false;

  // Enter-to-send preference, persisted per client
  const ENTER_KEY = 'learnai.enterToSend';
  let enterToSend = typeof localStorage !== 'undefined' && localStorage.getItem(ENTER_KEY) === 'true';
  function toggleEnterToSend() {
    enterToSend = !enterToSend;
    if (typeof localStorage !== 'undefined') localStorage.setItem(ENTER_KEY, String(enterToSend));
  }

  $: busy = $pendingMessage?.chatId === chatId && $pendingMessage?.busy;
  $: error = $pendingMessage?.chatId === chatId && !$pendingMessage?.busy ? $pendingMessage?.error : null;

  onMount(async () => {
    try {
      const res = await listModels();
      modelList.set(res.data || []);
      if ((res.data || []).length && !$selectedModel) selectedModel.set(res.data[0].id);
    } catch {}
    // Refresh the RAG file list so the dropdown shows current files
    try {
      const rag = await listRagFiles();
      ragFiles.set(rag.items || []);
    } catch {}
  });

  function goToRagPage() {
    window.location.hash = '/rag';
    showControls = false;
  }

  function applyPrompt() {
    const p = prompts.find(p => p.id === promptId);
    if (p) {
      input = (p.template + "\n\n" + input).trim();
      showControls = false;
    }
  }

  function send() {
    if (!input.trim() || busy) return;
    const msg = input;
    input = '';
    sendChatMessage(chatId, msg, { profileId: profileId || undefined, useRag });
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key !== 'Enter') return;
    // Ctrl/Cmd + Enter always sends (power user shortcut, works either mode)
    if (e.metaKey || e.ctrlKey) {
      e.preventDefault();
      send();
      return;
    }
    // When enterToSend is on: Enter alone sends, Shift+Enter is newline
    if (enterToSend && !e.shiftKey) {
      e.preventDefault();
      send();
    }
    // When enterToSend is off: Enter alone inserts newline (default textarea behavior)
  }

  function getProfileName(id: string): string {
    const p = profiles.find(p => p.id === id);
    return p ? p.name : '';
  }

  function getProfileModel(id: string): string {
    const p = profiles.find(p => p.id === id);
    return p ? p.base_model : '';
  }

  $: activeModel = profileId ? getProfileModel(profileId) : $selectedModel;
</script>

<div class="chat-input-area">
  {#if showControls}
    <div class="input-controls-popup" use:clickOutside on:clickoutside={() => showControls = false}>
      <div class="ctrl-section">
        <label>Profile</label>
        <select bind:value={profileId}>
          <option value=''>None</option>
          {#each profiles as p}<option value={p.id}>{p.name} ({p.base_model})</option>{/each}
        </select>
      </div>
      <div class="ctrl-section">
        <label>Model {#if profileId}<span class="ctrl-override">(set by profile)</span>{/if}</label>
        {#if profileId}
          <div class="ctrl-model-locked">{getProfileModel(profileId)}</div>
        {:else}
          <select bind:value={$selectedModel}>
            {#each $modelList as m}
              <option value={m.id}>{m.id}</option>
            {/each}
          </select>
        {/if}
      </div>
      <div class="ctrl-section">
        <label>Prompt</label>
        <div style="display:flex; gap:8px;">
          <select bind:value={promptId} style="flex:1;">
            <option value=''>None</option>
            {#each prompts as p}<option value={p.id}>{p.name}</option>{/each}
          </select>
          {#if promptId}
            <button class="ctrl-insert-btn" on:click={applyPrompt}>Insert</button>
          {/if}
        </div>
      </div>
      <div class="ctrl-section">
        <label style="display:inline-flex; align-items:center; gap:8px; text-transform:none; letter-spacing:0; cursor:pointer; font-weight:500;">
          <input type="checkbox" bind:checked={useRag} />
          Use RAG files
          {#if $activeFileIds.length > 0}
            <span class="rag-count">{$activeFileIds.length} active</span>
          {/if}
        </label>
        {#if useRag}
          <div class="rag-picker">
            {#if $ragFiles.length > 0}
              {#each $ragFiles as f}
                <button
                  class="rag-option"
                  class:active={$activeFileIds.includes(f.id)}
                  on:click={() => toggleFileActive(f.id)}
                  title={f.filename}
                >
                  <span class="rag-check">{$activeFileIds.includes(f.id) ? '✓' : ''}</span>
                  <span class="rag-filename">{f.filename}</span>
                  <span class="rag-size">{Math.round(f.size/1024)} KB</span>
                </button>
              {/each}
            {:else}
              <div class="rag-empty">No files uploaded yet.</div>
            {/if}
            <button class="rag-add" on:click={goToRagPage}>
              <span class="rag-check">+</span>
              <span class="rag-filename">Upload new file</span>
            </button>
          </div>
        {/if}
      </div>
      <div class="ctrl-section">
        <label style="display:inline-flex; align-items:center; gap:8px; text-transform:none; letter-spacing:0; cursor:pointer; font-weight:500;">
          <input type="checkbox" checked={enterToSend} on:change={toggleEnterToSend} />
          Enter to send
        </label>
        <div style="margin-top:6px; font-size:0.72rem; color:var(--text-muted);">
          {#if enterToSend}
            Enter sends the message. Shift+Enter inserts a new line.
          {:else}
            Enter inserts a new line. Cmd/Ctrl+Enter sends the message.
          {/if}
        </div>
      </div>
    </div>
  {/if}

  {#if profileId || useRag || activeModel}
    <div class="input-tags">
      <span class="input-tag model-tag">{activeModel || 'No model'}</span>
      {#if profileId}<span class="input-tag">Profile: {getProfileName(profileId)}</span>{/if}
      {#if useRag}<span class="input-tag">RAG active</span>{/if}
    </div>
  {/if}

  <div class="chat-input-row">
    <button class="input-plus-btn" class:active={showControls} on:click={() => showControls = !showControls}>+</button>
    <textarea
      bind:value={input}
      rows="1"
      on:keydown={handleKeydown}
      placeholder="Message {$currentTheme.name}..."
      class="chat-textarea"
    ></textarea>
    <button class="input-send-btn" on:click={send} disabled={busy || !input.trim()}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
  </div>

  {#if error}<div class="msg-error" style="margin:8px 0 0;">{error}</div>{/if}
</div>

<style>
  .chat-input-area {
    padding: 16px 24px 20px;
    border-top: 1px solid var(--border-light);
    position: relative;
  }

  .chat-input-row {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 6px 8px 6px 6px;
    transition: border-color 0.15s;
  }
  .chat-input-row:focus-within {
    border-color: var(--brand);
  }

  .chat-textarea {
    flex: 1;
    border: none;
    background: transparent;
    color: var(--text);
    font-size: 0.92rem;
    font-family: inherit;
    padding: 8px 4px;
    resize: none;
    min-height: 24px;
    max-height: 120px;
    box-shadow: none;
    outline: none;
    line-height: 1.5;
  }
  .chat-textarea::placeholder { color: var(--text-muted); }

  .input-plus-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.15s;
    flex-shrink: 0;
    font-family: inherit;
  }
  .input-plus-btn:hover, .input-plus-btn.active {
    background: var(--brand-bg);
    border-color: var(--brand);
    color: var(--brand);
  }

  .input-send-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: var(--brand);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .input-send-btn:hover { background: var(--brand-light); }
  .input-send-btn:disabled { opacity: 0.3; cursor: default; }

  .input-controls-popup {
    position: absolute;
    bottom: calc(100% + 4px);
    left: 24px;
    right: 24px;
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 -4px 24px rgba(0,0,0,0.15);
    z-index: 50;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .ctrl-section label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 4px;
    display: block;
  }
  .ctrl-section select, .ctrl-section input[type="checkbox"] {
    box-shadow: none;
  }
  .ctrl-insert-btn {
    padding: 6px 14px;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--card-alt);
    color: var(--text);
    font-size: 0.8rem;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .ctrl-insert-btn:hover { background: var(--bg-warm); }

  .rag-count {
    margin-left: auto;
    font-size: 0.68rem;
    color: var(--brand);
    background: var(--brand-bg);
    padding: 2px 8px;
    border-radius: 999px;
    font-weight: 600;
  }
  .rag-picker {
    margin-top: 8px;
    border: 1px solid var(--border-light);
    border-radius: 8px;
    background: var(--bg);
    max-height: 200px;
    overflow-y: auto;
  }
  .rag-option, .rag-add {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    background: transparent;
    border: none;
    border-bottom: 1px solid var(--border-light);
    color: var(--text);
    font-family: inherit;
    font-size: 0.82rem;
    cursor: pointer;
    text-align: left;
    transition: background 0.1s;
  }
  .rag-option:last-of-type { border-bottom: 1px solid var(--border-light); }
  .rag-add { border-bottom: none; color: var(--brand); font-weight: 600; }
  .rag-option:hover, .rag-add:hover { background: var(--card); }
  .rag-option.active { background: var(--brand-bg); }
  .rag-check {
    width: 16px;
    flex-shrink: 0;
    color: var(--brand);
    font-weight: 700;
    text-align: center;
  }
  .rag-filename {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .rag-size {
    font-size: 0.7rem;
    color: var(--text-muted);
    flex-shrink: 0;
    font-variant-numeric: tabular-nums;
  }
  .rag-empty {
    padding: 12px;
    font-size: 0.78rem;
    color: var(--text-muted);
    text-align: center;
    font-style: italic;
  }

  .ctrl-override {
    text-transform: none;
    letter-spacing: 0;
    font-weight: 400;
    font-style: italic;
    color: var(--gold);
  }
  .ctrl-model-locked {
    padding: 11px 14px;
    border: 1.5px solid var(--border);
    border-radius: 6px;
    background: var(--card-alt);
    color: var(--text-muted);
    font-size: 0.9rem;
    font-style: italic;
  }

  .input-tags {
    display: flex;
    gap: 6px;
    padding: 0 0 8px;
  }
  .input-tag {
    font-size: 0.72rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 999px;
    background: var(--gold-bg);
    color: var(--gold-light);
    border: 1px solid rgba(232, 184, 58, 0.15);
  }
  .model-tag {
    background: rgba(255,255,255,0.06);
    color: var(--text-secondary);
    border-color: var(--border);
  }

  @media (max-width: 768px) {
    .chat-input-area { padding: 10px 12px 14px; }
    .input-controls-popup {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      top: auto;
      border-radius: 14px 14px 0 0;
      padding: 20px 16px;
      max-height: 70vh;
      overflow-y: auto;
      box-shadow: 0 -8px 32px rgba(0,0,0,0.25);
    }
    .input-tags { flex-wrap: wrap; }
    .input-plus-btn { width: 38px; height: 38px; font-size: 1.1rem; }
    .input-send-btn { width: 38px; height: 38px; }
    .chat-textarea { font-size: 16px; /* prevents iOS zoom on focus */ }
    .ctrl-section select, .ctrl-section input { font-size: 16px; min-height: 44px; }
  }
</style>
