<script lang="ts">
  import { onMount } from 'svelte';
  import { listTools, callTool, generateTool, deleteTool } from '../lib/api';
  import { selectedModel } from '../lib/stores';

  let tools: Array<{ name: string; schema: any; generated?: boolean }> = [];
  let chosen = '';
  let args = '{}';
  let result: any = null;
  let error: string | null = null;
  let busy = false;

  // Builder state
  let buildDescription = '';
  let building = false;
  let buildError: string | null = null;
  let buildOk: string | null = null;
  let lastBuiltCode: string | null = null;

  onMount(loadTools);

  async function loadTools() {
    try {
      const { items } = await listTools();
      tools = items;
      if (items.length) chosen = items[0].name;
    } catch {}
  }

  async function run() {
    try {
      error = null;
      result = null;
      busy = true;
      const parsed = args ? JSON.parse(args) : {};
      result = await callTool(chosen, parsed);
    } catch (e: any) {
      error = e?.message || 'Failed';
    } finally { busy = false; }
  }

  async function build() {
    if (!buildDescription.trim()) return;
    try {
      building = true;
      buildError = null;
      buildOk = null;
      lastBuiltCode = null;
      const res = await generateTool(buildDescription, $selectedModel || undefined);
      buildOk = `Created tool "${res.name}"`;
      lastBuiltCode = res.code;
      buildDescription = '';
      await loadTools();
      chosen = res.name;
    } catch (e: any) {
      buildError = e?.message || 'Failed to generate tool';
    } finally { building = false; }
  }

  async function removeTool(name: string) {
    try {
      await deleteTool(name);
      await loadTools();
      if (chosen === name && tools.length) chosen = tools[0].name;
    } catch (e: any) { error = e?.message || 'Failed to delete'; }
  }

  function handleBuildKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      build();
    }
  }
</script>

<div style="display:flex; flex-direction:column; gap:24px;">
  <!-- Tool Builder -->
  <div class="card">
    <h2>Build a Tool</h2>
    <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:16px;">
      Describe what you want in plain English. The AI will create a working tool for you.
    </p>
    <div style="display:flex; gap:10px; align-items:flex-end;">
      <div style="flex:1;">
        <textarea
          rows="2"
          bind:value={buildDescription}
          on:keydown={handleBuildKeydown}
          placeholder="e.g., convert temperature from Fahrenheit to Celsius"
          style="width:100%;"
        ></textarea>
      </div>
      <button class="btn primary" style="height:56px; padding:0 24px;" on:click={build} disabled={building || !buildDescription.trim()}>
        {building ? 'Building...' : 'Build Tool'}
      </button>
    </div>
    {#if buildError}<div class="msg-error">{buildError}</div>{/if}
    {#if buildOk}<div class="msg-success">{buildOk}</div>{/if}
    {#if lastBuiltCode}
      <details style="margin-top:12px;">
        <summary style="cursor:pointer; color:var(--text-muted); font-size:0.82rem;">View generated code</summary>
        <pre style="margin-top:8px; font-size:0.8rem; white-space:pre-wrap;">{lastBuiltCode}</pre>
      </details>
    {/if}
  </div>

  <div class="grid2">
    <!-- Run a Tool -->
    <div class="card">
      <h2>Run a Tool</h2>
      <label>Tool</label>
      <select bind:value={chosen}>
        {#each tools as t}
          <option value={t.name}>{t.name} {t.generated ? '(custom)' : ''}</option>
        {/each}
      </select>

      {#if chosen}
        {@const spec = tools.find(t => t.name === chosen)}
        {#if spec?.schema?.properties}
          <div style="margin-top:8px; font-size:0.78rem; color:var(--text-muted);">
            Args: {Object.keys(spec.schema.properties).join(', ')}
          </div>
        {/if}
      {/if}

      <div style="height:12px;"></div>
      <label>Arguments (JSON)</label>
      <textarea rows="3" bind:value={args} placeholder="Enter JSON arguments..."></textarea>
      <div style="height:12px;"></div>
      <div style="display:flex; gap:8px;">
        <button class="btn primary" style="flex:1;" on:click={run} disabled={busy}>
          {busy ? 'Running...' : 'Run Tool'}
        </button>
        {#if chosen && tools.find(t => t.name === chosen)?.generated}
          <button class="btn danger" on:click={() => removeTool(chosen)}>Delete</button>
        {/if}
      </div>
      {#if error}<div class="msg-error">{error}</div>{/if}
    </div>

    <!-- Result -->
    <div class="card">
      <h2>Result</h2>
      {#if result}
        <pre style="white-space:pre-wrap;">{JSON.stringify(result, null, 2)}</pre>
      {:else}
        <div class="empty-state">Run a tool to see results here.</div>
      {/if}
    </div>
  </div>

  <!-- Available Tools -->
  {#if tools.length > 1}
    <div class="card">
      <h2>Available Tools</h2>
      <div class="list">
        {#each tools as t}
          <div class="item" style="cursor:pointer;" on:click={() => { chosen = t.name; }}>
            <div class="row" style="align-items:center;">
              <div class="col">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-weight:600;">{t.name}</span>
                  {#if t.generated}
                    <span class="badge" style="background:var(--success-bg);color:var(--success);">custom</span>
                  {:else}
                    <span class="badge">built-in</span>
                  {/if}
                </div>
                {#if t.schema?.properties}
                  <div style="color:var(--text-muted); font-size:0.78rem; margin-top:2px;">
                    Params: {Object.keys(t.schema.properties).join(', ')}
                  </div>
                {/if}
              </div>
              {#if t.generated}
                <button class="btn danger" style="font-size:0.75rem; padding:4px 10px;" on:click|stopPropagation={() => removeTool(t.name)}>Delete</button>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>
