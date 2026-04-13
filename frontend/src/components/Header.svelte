<script lang="ts">
  import { user, clearAuth } from '../lib/auth';
  import { listModels } from '../lib/api';
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { selectedModel } from '../lib/stores';
  import { currentTheme } from '../lib/theme';

  const models = writable<Array<{id:string}>>([]);

  onMount(async () => {
    try {
      const res = await listModels();
      models.set(res.data || []);
      if ((res.data || []).length) selectedModel.set(res.data[0].id);
    } catch {}
  });

  function isActive(path: string): boolean {
    const hash = window.location.hash || '#/chats';
    if (path === '#/chats' && hash.startsWith('#/chat')) return true;
    return hash === path;
  }
</script>

<header class="header">
  <div class="logo">Learn<span class="accent">AI</span></div>
  <nav class="nav">
    <a href="#/chats" class:active={isActive('#/chats')}>Chats</a>
    <a href="#/rag" class:active={isActive('#/rag')}>RAG</a>
    <a href="#/tools" class:active={isActive('#/tools')}>Tools</a>
    <a href="#/profiles" class:active={isActive('#/profiles')}>Profiles</a>
    <a href="#/prompts" class:active={isActive('#/prompts')}>Prompts</a>
  </nav>
  <div class="spacer"></div>
  <div class="model-select-wrap">
    <label>Model</label>
    <select bind:value={$selectedModel}>
      {#each $models as m}
        <option value={m.id}>{m.id}</option>
      {/each}
    </select>
  </div>
  <div class="auth">
    {#if $user}
      <span class="user-email">{$currentTheme.tagline}</span>
      <button class="btn header-btn" on:click={() => { clearAuth(); window.location.hash = '/login'; }}>Logout</button>
    {:else}
      <a class="btn header-btn" href="#/login">Login</a>
    {/if}
  </div>
</header>
