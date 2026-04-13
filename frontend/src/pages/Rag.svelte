<script lang="ts">
  import { onMount } from 'svelte';
  import { uploadRagFile, listRagFiles, deleteRagFile, deleteAllRagFiles } from '../lib/api';
  import { activeFileIds, toggleFileActive } from '../lib/rag';

  let files: Array<{ id: string; filename: string; size: number }> = [];
  let busy = false;
  let error: string | null = null;
  let ok: string | null = null;

  onMount(loadFiles);

  async function loadFiles() {
    try {
      const res = await listRagFiles();
      files = res.items;
    } catch {}
  }

  function choose(id: string) { toggleFileActive(id); }

  async function onPick(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    try {
      busy = true; error = null; ok = null;
      const res = await uploadRagFile(file);
      files = [res, ...files];
      toggleFileActive(res.id);
      ok = `Uploaded ${res.filename}`;
    } catch (e: any) { error = e?.message || 'Upload failed'; }
    finally { busy = false; }
  }

  async function removeFile(id: string) {
    try {
      await deleteRagFile(id);
      files = files.filter(f => f.id !== id);
      activeFileIds.update(ids => ids.filter(i => i !== id));
    } catch (e: any) { error = e?.message || 'Delete failed'; }
  }

  async function clearAll() {
    try {
      await deleteAllRagFiles();
      files = [];
      activeFileIds.set([]);
      ok = 'All files cleared';
    } catch (e: any) { error = e?.message || 'Clear failed'; }
  }
</script>

<div class="grid2">
  <div class="card">
    <h2>Upload Document</h2>
    <p style="color:var(--text-secondary); font-size:0.88rem; margin-bottom:20px;">
      Upload a text file to use as retrieval context in your chats.
    </p>
    <label class="drop-zone">
      <input type="file" on:change={onPick} style="display:none;" />
      {busy ? 'Uploading...' : 'Click to choose a file'}
    </label>
    {#if error}<div class="msg-error">{error}</div>{/if}
    {#if ok}<div class="msg-success">{ok}</div>{/if}
  </div>
  <div class="card">
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px;">
      <h2 style="margin:0;">Uploaded Files</h2>
      {#if files.length > 0}
        <button class="btn danger" style="font-size:0.78rem; padding:5px 12px;" on:click={clearAll}>Clear All</button>
      {/if}
    </div>
    <div class="list">
      {#each files as f}
        <div class="item">
          <div class="row" style="align-items:center;">
            <div class="col">
              <div style="font-weight:600;">{f.filename}</div>
              <small class="mono">{Math.round(f.size/1024)} KB</small>
            </div>
            <div style="display:flex; gap:6px;">
              <button class="btn {$activeFileIds.includes(f.id) ? 'success' : ''}" on:click={() => choose(f.id)}>
                {$activeFileIds.includes(f.id) ? 'Active' : 'Use'}
              </button>
              <button class="btn danger" on:click={() => removeFile(f.id)} title="Delete file">&times;</button>
            </div>
          </div>
        </div>
      {/each}
      {#if files.length===0}
        <div class="empty-state">No files uploaded yet.</div>
      {/if}
    </div>
  </div>
</div>
