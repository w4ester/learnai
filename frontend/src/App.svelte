<script lang="ts">
  import { onMount } from 'svelte';
  import { user } from './lib/auth';
  import { me } from './lib/api';
  import { sidebarOpen } from './lib/stores';
  import { currentTheme, initTheme } from './lib/theme';
  import Login from './pages/Login.svelte';
  import Chat from './pages/Chat.svelte';
  import Rag from './pages/Rag.svelte';
  import Tools from './pages/Tools.svelte';
  import Profiles from './pages/Profiles.svelte';
  import Prompts from './pages/Prompts.svelte';
  import Skills from './pages/Skills.svelte';
  import Workshops from './pages/Workshops.svelte';
  import Sidebar from './components/Sidebar.svelte';

  type Route = { name: 'login'|'chats'|'chat'|'rag'|'tools'|'profiles'|'prompts'|'skills'|'workshops'; params?: Record<string,string> };
  let route: Route = { name: 'chats' };

  function parseRoute(): Route {
    const h = window.location.hash || '#/chats';
    if (h.startsWith('#/chat/')) return { name: 'chat', params: { id: h.split('/')[2] } };
    if (h === '#/login') return { name: 'login' };
    if (h === '#/rag') return { name: 'rag' };
    if (h === '#/tools') return { name: 'tools' };
    if (h === '#/profiles') return { name: 'profiles' };
    if (h === '#/prompts') return { name: 'prompts' };
    if (h === '#/skills') return { name: 'skills' };
    if (h === '#/workshops') return { name: 'workshops' };
    return { name: 'chats' };
  }

  function handleHashChange() {
    route = parseRoute();
    if (window.innerWidth <= 768) {
      sidebarOpen.set(false);
    }
  }

  onMount(async () => {
    initTheme();
    window.addEventListener('hashchange', handleHashChange);
    route = parseRoute();
    if (window.innerWidth <= 768) {
      sidebarOpen.set(false);
    }
    try {
      const current = await me();
      user.set(current);
      if (route.name === 'login') {
        window.location.hash = '/chats';
      }
    } catch {
      user.set(null);
    }
  });
</script>

{#if route.name === 'login'}
  <Login on:loggedin={() => { window.location.hash = '/chats'; }} />
{:else}
  <div class="mobile-header">
    <button class="hamburger" on:click={() => sidebarOpen.update(v => !v)}>
      <span></span><span></span><span></span>
    </button>
    <span class="mobile-logo">Learn<span class="welcome-accent">AI</span></span>
  </div>

  <div class="app-layout">
    {#if $sidebarOpen}
      <div class="sidebar-overlay" on:click={() => sidebarOpen.set(false)}></div>
    {/if}

    <div class="sidebar-wrapper" class:open={$sidebarOpen}>
      <Sidebar />
    </div>

    <main class="main-content">
      {#if route.name === 'chats'}
        <div class="welcome-page">
          <div class="welcome-center">
            <h1 class="welcome-title">Learn<span class="welcome-accent">AI</span></h1>
            <p class="welcome-sub">Select a chat from the sidebar or start a new one.</p>
          </div>
        </div>
      {:else if route.name === 'chat'}
        <Chat id={route.params?.id || ''} />
      {:else if route.name === 'rag'}
        <div class="page-container"><Rag /></div>
      {:else if route.name === 'tools'}
        <div class="page-container"><Tools /></div>
      {:else if route.name === 'profiles'}
        <div class="page-container"><Profiles /></div>
      {:else if route.name === 'prompts'}
        <div class="page-container"><Prompts /></div>
      {:else if route.name === 'skills'}
        <div class="page-container"><Skills /></div>
      {:else if route.name === 'workshops'}
        <div class="page-container"><Workshops /></div>
      {/if}
    </main>
  </div>
{/if}

<style>
  .app-layout {
    display: grid;
    grid-template-columns: 260px 1fr;
    height: 100vh;
    overflow: hidden;
    position: relative;
  }

  .sidebar-wrapper {
    height: 100vh;
    overflow: hidden;
  }

  .sidebar-overlay {
    display: none;
  }

  .main-content {
    overflow-y: auto;
    height: 100vh;
    background: var(--bg);
  }

  .mobile-header {
    display: none;
  }

  .page-container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px 28px;
  }

  .welcome-page {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    text-align: center;
    padding: 20px;
  }
  .welcome-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.5rem;
    font-weight: 400;
    color: var(--text);
    margin-bottom: 12px;
  }
  .welcome-accent { color: var(--accent-text, var(--brand)); }
  .welcome-sub {
    color: var(--text-muted);
    font-size: 1rem;
  }

  .hamburger {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 8px;
    background: none;
    border: none;
    cursor: pointer;
  }
  .hamburger span {
    display: block;
    width: 20px;
    height: 2px;
    background: var(--text-on-dark);
    border-radius: 1px;
    transition: all 0.2s;
  }

  .mobile-logo {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.05rem;
    color: var(--text-on-dark);
  }

  @media (max-width: 768px) {
    .app-layout {
      grid-template-columns: 1fr;
    }

    .sidebar-wrapper {
      position: fixed;
      top: 0;
      left: 0;
      z-index: 200;
      transform: translateX(-100%);
      transition: transform 0.25s var(--ease);
      width: 280px;
      box-shadow: none;
    }
    .sidebar-wrapper.open {
      transform: translateX(0);
      box-shadow: 4px 0 24px rgba(0,0,0,0.3);
    }

    .sidebar-overlay {
      display: block;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.4);
      z-index: 190;
      animation: fadeIn 0.2s ease;
    }

    .mobile-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 16px;
      border-bottom: 1px solid var(--border-light);
      background: var(--header-bg);
      position: sticky;
      top: 0;
      z-index: 300;
    }

    .app-layout { height: calc(100vh - 48px); }
    .main-content { height: calc(100vh - 48px); }

    .page-container {
      padding: 14px 10px;
    }

    .welcome-page {
      height: calc(100vh - 48px);
    }
    .welcome-title {
      font-size: 1.8rem;
    }
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>
