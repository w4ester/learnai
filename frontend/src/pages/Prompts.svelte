<script lang="ts">
  import { onMount } from 'svelte';
  import { listPrompts, createPrompt, deletePrompt } from '../lib/api';

  let prompts: Array<{ id:string; name:string; template:string }> = [];
  let name=''; let template='';
  let error: string | null = null; let ok: string | null = null;

  async function load() { try { prompts = await listPrompts(); } catch {} }
  onMount(load);

  async function create() {
    try { error=null; ok=null; const res = await createPrompt({ name, template }); ok='Prompt created'; name=''; template=''; await load(); }
    catch (e:any) { error = e?.message || 'Failed'; }
  }
  async function remove(id:string) {
    try { await deletePrompt(id); await load(); } catch (e:any) { error = e?.message || 'Failed'; }
  }
</script>

<div class="grid2">
  <div class="card">
    <h2>New Prompt</h2>
    <label>Name</label>
    <input bind:value={name} placeholder="Scholar Tone" />
    <div style="height:14px;"></div>
    <label>Template</label>
    <textarea rows="6" bind:value={template} placeholder="You are a scholar..."></textarea>
    <div style="height:20px;"></div>
    <button class="btn primary" style="width:100%;" on:click={create}>Create Prompt</button>
    {#if error}<div class="msg-error">{error}</div>{/if}
    {#if ok}<div class="msg-success">{ok}</div>{/if}
  </div>
  <div class="card">
    <h2>Your Prompts</h2>
    <div class="list">
      {#each prompts as p}
        <div class="item">
          <div class="row" style="align-items:center;">
            <div class="col">
              <div style="font-weight:600;">{p.name}</div>
              <div style="color:var(--text-secondary); font-size:0.85rem; margin-top:4px; white-space:pre-wrap;">{p.template}</div>
            </div>
            <div><button class="btn danger" on:click={() => remove(p.id)}>Delete</button></div>
          </div>
        </div>
      {/each}
      {#if prompts.length===0}
        <div class="empty-state">No prompts yet.</div>
      {/if}
    </div>
  </div>
</div>
