<script lang="ts">
  import { onMount } from 'svelte';
  import { listChats, createChat } from '../lib/api';

  let chats: Array<{ id:string; title?:string; updatedAt: string }> = [];
  let error: string | null = null;
  let busy = false;
  let newTitle = '';

  async function load() {
    try { busy = true; error = null; const { items } = await listChats(); chats = items; }
    catch (e:any) { error = e?.message || 'Failed to load chats'; }
    finally { busy = false; }
  }
  onMount(load);

  async function createNew() {
    try {
      busy = true; error = null;
      const res = await createChat(newTitle || undefined);
      window.location.hash = '/chat/' + res.id;
    } catch (e:any) { error = e?.message || 'Failed to create chat'; }
    finally { busy = false; }
  }
</script>

<div class="grid2">
  <div class="card">
    <h2>Your Chats</h2>
    {#if error}<div class="msg-error">{error}</div>{/if}
    {#if busy && chats.length === 0}<div class="empty-state">Loading...</div>{/if}
    <div class="list">
      {#each chats as c}
        <a class="item" href={"#/chat/" + c.id} style="display:block; text-decoration:none; color:inherit;">
          <div class="row" style="align-items:center;">
            <div class="col">
              <div style="font-weight:600; font-size: 0.95rem;">{c.title || 'Untitled Chat'}</div>
              <small class="mono">{new Date(c.updatedAt).toLocaleString()}</small>
            </div>
            <div>
              <span style="color:var(--brand); font-size:0.8rem; font-weight:500;">Open &rarr;</span>
            </div>
          </div>
        </a>
      {/each}
      {#if !busy && chats.length === 0}
        <div class="empty-state">No chats yet. Create one to get started.</div>
      {/if}
    </div>
  </div>
  <div class="card">
    <h2>New Chat</h2>
    <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:20px;">Start a new conversation with your AI model.</p>
    <label>Title (optional)</label>
    <input bind:value={newTitle} placeholder="e.g., Project Q&A" />
    <div style="height:20px;"></div>
    <button class="btn primary" style="width:100%;" on:click={createNew} disabled={busy}>
      {busy ? 'Creating...' : 'Create Chat'}
    </button>
  </div>
</div>
