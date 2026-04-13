<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { setAuth } from '../lib/auth';
  import { login, register } from '../lib/api';

  const dispatch = createEventDispatcher<{ loggedin: void }>();
  let email=''; let password=''; let mode:'login'|'register'='login'; let error:string|null=null; let busy=false;

  async function submit() {
    try {
      busy = true; error = null;
      const fn = mode === 'login' ? login : register;
      const { token, user } = await fn(email, password);
      setAuth(token, user);
      dispatch('loggedin');
    } catch (e: any) { error = e?.message || 'Request failed'; } finally { busy = false; }
  }
</script>

<div class="container" style="max-width: 400px; margin-top: 80px;">
  <div class="card" style="text-align:center;">
    <div style="margin-bottom:28px;">
      <div style="font-family:'DM Serif Display',Georgia,serif; font-size:1.6rem; color:var(--text);">Learn<span style="color:var(--brand);">AI</span></div>
      <div style="color:var(--text-muted); font-size:0.88rem; margin-top:6px;">
        {mode === 'login' ? 'Welcome back' : 'Create your account'}
      </div>
    </div>
    {#if error}<div class="msg-error" style="text-align:left;">{error}</div><div style="height:16px;"></div>{/if}
    <div style="text-align:left;">
      <label>Email</label>
      <input type="email" bind:value={email} placeholder="you@example.com" />
      <div style="height:14px;"></div>
      <label>Password</label>
      <input type="password" bind:value={password} placeholder="Enter password" />
    </div>
    <div style="height:24px;"></div>
    <button class="btn primary" style="width:100%;" on:click|preventDefault={submit} disabled={busy}>
      {busy ? 'Please wait...' : (mode === 'login' ? 'Sign In' : 'Create Account')}
    </button>
    <div style="height:14px;"></div>
    <button style="width:100%; background:none; border:none; color:var(--text-muted); font-size:0.85rem; padding:8px;" on:click={() => { mode = mode==='login' ? 'register' : 'login'; error=null; }}>
      {mode === 'login' ? 'Need an account? Register' : 'Already have an account? Sign in'}
    </button>
  </div>
</div>
