<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { user, clearAuth } from '../lib/auth';
  import { listChats, createChat, deleteChat, renameChat } from '../lib/api';
  import { chatList, sidebarOpen, pendingMessage } from '../lib/stores';
  import { currentTheme } from '../lib/theme';

  let busy = false;
  let editingId: string | null = null;
  let editTitle = '';
  let renameInputEl: HTMLInputElement;

  onMount(refreshChats);

  export async function refreshChats() {
    try {
      const { items } = await listChats();
      chatList.set(items);
    } catch {}
  }

  async function createNewChat() {
    try {
      busy = true;
      const res = await createChat();
      chatList.update(list => [{ id: res.id, title: res.title, updatedAt: new Date().toISOString() }, ...list]);
      window.location.hash = '/chat/' + res.id;
    } catch {}
    finally { busy = false; }
  }

  function isActiveChat(id: string): boolean {
    return window.location.hash === '#/chat/' + id;
  }

  function isActiveNav(path: string): boolean {
    const hash = window.location.hash || '#/chats';
    return hash === '#/' + path;
  }

  async function startRename(e: Event, c: { id: string; title?: string }) {
    e.preventDefault();
    e.stopPropagation();
    editingId = c.id;
    editTitle = c.title || '';
    await tick();
    if (renameInputEl) { renameInputEl.focus(); renameInputEl.select(); }
  }

  async function finishRename(id: string) {
    if (editTitle.trim()) {
      try {
        await renameChat(id, editTitle.trim());
        chatList.update(list => list.map(c => c.id === id ? { ...c, title: editTitle.trim() } : c));
      } catch {}
    }
    editingId = null;
  }

  function handleRenameKeydown(e: KeyboardEvent, id: string) {
    if (e.key === 'Enter') { e.preventDefault(); finishRename(id); }
    if (e.key === 'Escape') { editingId = null; }
  }

  async function removeChat(e: Event, id: string) {
    e.preventDefault();
    e.stopPropagation();
    try {
      await deleteChat(id);
      chatList.update(list => list.filter(c => c.id !== id));
      if (window.location.hash === '#/chat/' + id) {
        window.location.hash = '/chats';
      }
    } catch {}
  }

  function logout() {
    clearAuth();
    window.location.hash = '/login';
  }
</script>

<aside class="sidebar" class:collapsed={!$sidebarOpen}>
  <div class="sb-brand">
    <span class="sb-logo">Learn<span class="sb-accent">AI</span></span>
  </div>

  <button class="sb-new-chat" on:click={createNewChat} disabled={busy}>
    <span class="sb-plus">+</span>
    {busy ? 'Creating...' : 'New Chat'}
  </button>

  <nav class="sb-nav">
    <a href="#/rag" class:active={isActiveNav('rag')}>
      <span class="sb-icon">&#9783;</span> RAG
    </a>
    <a href="#/tools" class:active={isActiveNav('tools')}>
      <span class="sb-icon">&#9881;</span> Tools
    </a>
    <a href="#/profiles" class:active={isActiveNav('profiles')}>
      <span class="sb-icon">&#9673;</span> Profiles
    </a>
    <a href="#/prompts" class:active={isActiveNav('prompts')}>
      <span class="sb-icon">&#9998;</span> Prompts
    </a>
    <a href="#/skills" class:active={isActiveNav('skills')}>
      <span class="sb-icon">&#9889;</span> Skills
    </a>
    <a href="#/workshops" class:active={isActiveNav('workshops')}>
      <span class="sb-icon">&#9776;</span> Workshops
    </a>
  </nav>

  <div class="sb-section-label">Recent Chats</div>
  <div class="sb-chats">
    {#each $chatList as c}
      <a href={"#/chat/" + c.id} class="sb-chat-item" class:active={isActiveChat(c.id)}>
        {#if editingId === c.id}
          <input
            class="sb-rename-input"
            bind:this={renameInputEl}
            bind:value={editTitle}
            on:blur={() => finishRename(c.id)}
            on:keydown={(e) => handleRenameKeydown(e, c.id)}
            on:click|preventDefault|stopPropagation
          />
        {:else}
          {#if $pendingMessage?.chatId === c.id && $pendingMessage?.busy}
            <span class="sb-processing-dot"></span>
          {/if}
          <span class="sb-chat-title">{c.title || 'Untitled Chat'}</span>
          <button class="sb-chat-action sb-chat-edit" on:click={(e) => startRename(e, c)} title="Rename">&#9998;</button>
          <button class="sb-chat-action sb-chat-delete" on:click={(e) => removeChat(e, c.id)} title="Delete">&times;</button>
        {/if}
      </a>
    {/each}
    {#if $chatList.length === 0}
      <div class="sb-empty">No chats yet</div>
    {/if}
  </div>

  <div class="sb-user">
    {#if $user}
      <span class="sb-user-email">{$currentTheme.tagline}</span>
      <button class="sb-logout" on:click={logout}>Logout</button>
    {:else}
      <a href="#/login" class="sb-login-link">Login</a>
    {/if}
  </div>
</aside>

<style>
  .sidebar {
    background: var(--header-bg);
    height: 100vh;
    display: flex;
    flex-direction: column;
    border-right: 1px solid rgba(255,255,255,0.06);
    overflow: hidden;
    width: 260px;
  }

  .sb-brand {
    padding: 18px 20px 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .sb-logo {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.15rem;
    color: var(--text-on-dark);
  }
  .sb-accent { color: var(--accent-text, var(--gold-light)); }

  .sb-new-chat {
    margin: 0 12px 8px;
    padding: 10px 16px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    color: var(--text-on-dark);
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: background 0.15s;
    font-family: inherit;
  }
  .sb-new-chat:hover { background: rgba(255,255,255,0.12); }
  .sb-plus { font-size: 1.1rem; opacity: 0.7; }

  .sb-nav {
    display: flex;
    flex-direction: column;
    padding: 8px 12px;
    gap: 2px;
  }
  .sb-nav a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 6px;
    color: rgba(240, 236, 230, 0.55);
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.15s;
  }
  .sb-nav a:hover { color: var(--text-on-dark); background: rgba(255,255,255,0.06); }
  .sb-nav a.active { color: var(--gold-light); background: rgba(245, 197, 66, 0.08); }
  .sb-icon { font-size: 0.95rem; width: 18px; text-align: center; }

  .sb-section-label {
    padding: 16px 20px 6px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(240, 236, 230, 0.3);
  }

  .sb-chats {
    flex: 1;
    overflow-y: auto;
    padding: 0 12px;
  }
  .sb-chat-item {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 12px;
    border-radius: 6px;
    color: rgba(240, 236, 230, 0.55);
    font-size: 0.84rem;
    text-decoration: none;
    transition: all 0.15s;
  }
  .sb-chat-item:hover { color: var(--text-on-dark); background: rgba(255,255,255,0.06); }
  .sb-chat-item.active { color: var(--text-on-dark); background: rgba(255,255,255,0.1); }
  .sb-chat-title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    min-width: 0;
  }
  .sb-chat-action {
    display: none;
    width: 22px;
    height: 22px;
    border-radius: 4px;
    border: none;
    background: transparent;
    color: rgba(240, 236, 230, 0.35);
    font-size: 0.85rem;
    cursor: pointer;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    font-family: inherit;
    transition: all 0.15s;
    line-height: 1;
    padding: 0;
  }
  .sb-chat-item:hover .sb-chat-action { display: flex; }
  .sb-chat-edit:hover {
    background: rgba(232, 184, 58, 0.15);
    color: var(--gold-light);
  }
  .sb-chat-delete {
    font-size: 1rem;
  }
  .sb-chat-delete:hover {
    background: rgba(224, 51, 80, 0.15);
    color: #f07088;
  }
  .sb-rename-input {
    flex: 1;
    min-width: 0;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 4px;
    color: var(--text-on-dark);
    font-size: 0.84rem;
    padding: 2px 6px;
    font-family: inherit;
    outline: none;
    box-shadow: none;
    width: 100%;
  }
  .sb-rename-input:focus {
    border-color: var(--gold-light);
  }
  .sb-processing-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--gold-light);
    flex-shrink: 0;
    animation: sb-pulse 1.2s ease-in-out infinite;
  }
  @keyframes sb-pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
  }
  .sb-empty {
    padding: 12px;
    color: rgba(240, 236, 230, 0.25);
    font-size: 0.82rem;
    font-style: italic;
  }

  .sb-user {
    padding: 14px 16px;
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }
  .sb-user-email {
    font-size: 0.78rem;
    color: rgba(240, 236, 230, 0.4);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }
  .sb-logout {
    background: none;
    border: 1px solid rgba(255,255,255,0.1);
    color: rgba(240, 236, 230, 0.5);
    font-size: 0.75rem;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-family: inherit;
    flex-shrink: 0;
    transition: all 0.15s;
  }
  .sb-logout:hover { background: rgba(255,255,255,0.06); color: var(--text-on-dark); }
  .sb-login-link {
    color: var(--gold-light);
    font-size: 0.85rem;
    text-decoration: none;
  }

  .sb-chats::-webkit-scrollbar { width: 4px; }
  .sb-chats::-webkit-scrollbar-track { background: transparent; }
  .sb-chats::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

  @media (max-width: 768px) {
    .sidebar { width: 100%; }
    .sb-brand { padding: 14px 16px 10px; }
    .sb-nav a { padding: 10px 12px; font-size: 0.88rem; min-height: 44px; }
    .sb-chat-item { padding: 10px 12px; min-height: 44px; }
    .sb-new-chat { padding: 12px 16px; font-size: 0.9rem; min-height: 44px; }
    .sb-user { padding: 12px 16px; }
    .sb-user-email { font-size: 0.72rem; line-height: 1.3; white-space: normal; }
    .sb-logout { padding: 8px 14px; font-size: 0.8rem; min-height: 36px; }
  }
</style>
