<script lang="ts">
  import { onMount } from 'svelte';
  import { listProfiles, createProfile, updateProfile, deleteProfile, listModels } from '../lib/api';

  let profiles: Array<{ id: string; name: string; base_model: string; system_prompt?: string; params?: any }> = [];
  let models: Array<{ id: string }> = [];

  let editId: string | null = null;
  let name = '';
  let base_model = '';
  let system_prompt = '';

  // Params as individual fields (0 = use model/Ollama default)
  let temperature = 0;
  let top_p = 0;
  let top_k = 0;
  let max_tokens = 0;
  let repeat_penalty = 0;
  let num_ctx = 0;

  let error: string | null = null;
  let ok: string | null = null;

  async function load() {
    try { profiles = await listProfiles(); } catch {}
  }

  onMount(async () => {
    await load();
    try {
      const res = await listModels();
      models = res.data || [];
      if (models.length && !base_model) base_model = models[0].id;
    } catch {}
  });

  function paramsToFields(p: any) {
    if (!p) return;
    if (p.temperature != null) temperature = p.temperature;
    if (p.top_p != null) top_p = p.top_p;
    if (p.top_k != null) top_k = p.top_k;
    if (p.num_predict != null) max_tokens = p.num_predict;
    if (p.max_tokens != null) max_tokens = p.max_tokens;
    if (p.repeat_penalty != null) repeat_penalty = p.repeat_penalty;
    if (p.num_ctx != null) num_ctx = p.num_ctx;
  }

  function fieldsToParams(): any {
    const p: any = {};
    if (temperature > 0) p.temperature = temperature;
    if (top_p > 0) p.top_p = top_p;
    if (top_k > 0) p.top_k = top_k;
    if (max_tokens > 0) p.num_predict = max_tokens;
    if (repeat_penalty > 0) p.repeat_penalty = repeat_penalty;
    if (num_ctx > 0) p.num_ctx = num_ctx;
    return p;
  }

  function resetFields() {
    temperature = 0; top_p = 0; top_k = 0; max_tokens = 0; repeat_penalty = 0; num_ctx = 0;
  }

  const presets = [
    {
      label: 'Quick Chat',
      desc: 'Fast, conversational responses. Low memory.',
      icon: '💬',
      name: 'Quick Chat',
      system_prompt: 'You are a helpful, concise assistant. Answer questions directly in plain language.',
      params: { temperature: 0.7, num_ctx: 4096, num_predict: 1024 }
    },
    {
      label: 'Deep RAG',
      desc: 'Large context for document Q&A. Uses more memory.',
      icon: '📄',
      name: 'Deep RAG',
      system_prompt: 'You are a document analyst. Answer questions based on the provided context. Cite specific details from the documents. If the context does not contain the answer, say so.',
      params: { temperature: 0.3, num_ctx: 65536, num_predict: 4096 }
    },
    {
      label: 'Creative Writer',
      desc: 'High variety for brainstorming and drafts.',
      icon: '✨',
      name: 'Creative Writer',
      system_prompt: 'You are a creative writing partner. Generate imaginative, varied responses. Explore different angles and ideas freely.',
      params: { temperature: 1.2, top_p: 0.95, top_k: 80, num_predict: 4096 }
    },
    {
      label: 'Precise Analyst',
      desc: 'Focused, deterministic. Good for code and data.',
      icon: '🎯',
      name: 'Precise Analyst',
      system_prompt: 'You are a precise technical analyst. Give accurate, well structured responses. Avoid speculation. When uncertain, say so.',
      params: { temperature: 0.2, top_p: 0.8, top_k: 20, num_predict: 2048 }
    },
    {
      label: 'Full Context',
      desc: 'Maximum context window for long conversations.',
      icon: '🧠',
      name: 'Full Context',
      system_prompt: 'You are a knowledgeable assistant with access to a large conversation history. Reference earlier parts of the conversation when relevant.',
      params: { temperature: 0.7, num_ctx: 131072, num_predict: 4096 }
    },
  ];

  function applyPreset(preset: typeof presets[0]) {
    if (editId) return; // don't overwrite when editing
    name = preset.name;
    system_prompt = preset.system_prompt;
    resetFields();
    if (preset.params.temperature) temperature = preset.params.temperature;
    if (preset.params.top_p) top_p = preset.params.top_p;
    if (preset.params.top_k) top_k = preset.params.top_k;
    if (preset.params.num_predict) max_tokens = preset.params.num_predict;
    if (preset.params.num_ctx) num_ctx = preset.params.num_ctx;
    if (preset.params.repeat_penalty) repeat_penalty = preset.params.repeat_penalty;
  }

  function editProfile(p: typeof profiles[0]) {
    editId = p.id;
    name = p.name;
    base_model = p.base_model;
    system_prompt = p.system_prompt || '';
    resetFields();
    paramsToFields(p.params);
    ok = null; error = null;
  }

  function cancelEdit() {
    editId = null;
    name = '';
    base_model = models.length ? models[0].id : '';
    system_prompt = '';
    resetFields();
    ok = null; error = null;
  }

  async function save() {
    try {
      error = null; ok = null;
      const data = { name, base_model, system_prompt, params: fieldsToParams() };
      if (editId) {
        await updateProfile(editId, data);
        ok = 'Profile updated';
      } else {
        await createProfile(data);
        ok = 'Profile created';
      }
      cancelEdit();
      await load();
    } catch (e: any) { error = e?.message || 'Failed'; }
  }

  async function remove(id: string) {
    try {
      await deleteProfile(id);
      if (editId === id) cancelEdit();
      await load();
    } catch (e: any) { error = e?.message || 'Failed'; }
  }
</script>

{#if !editId}
  <div class="preset-section">
    <label>Start from a preset <span style="font-weight:400; text-transform:none; letter-spacing:0; font-size:0.72rem; color:var(--text-muted);">Pick one to pre-fill the form, then choose your model and save.</span></label>
    <div class="preset-grid">
      {#each presets as preset}
        <button class="preset-card" on:click={() => applyPreset(preset)} title={preset.desc}>
          <span class="preset-icon">{preset.icon}</span>
          <div>
            <div class="preset-label">{preset.label}</div>
            <div class="preset-desc">{preset.desc}</div>
          </div>
        </button>
      {/each}
    </div>
  </div>
{/if}

<div class="grid2">
  <div class="card">
    <h2>{editId ? 'Edit Profile' : 'New Profile'}</h2>
    <label>Name</label>
    <input bind:value={name} placeholder="Socratic Tutor" />
    <div style="height:14px;"></div>
    <label>Base Model</label>
    <select bind:value={base_model}>
      {#each models as m}
        <option value={m.id}>{m.id}</option>
      {/each}
    </select>
    <div style="height:14px;"></div>
    <label>System Prompt</label>
    <textarea rows="4" bind:value={system_prompt} placeholder="You are a helpful assistant..."></textarea>
    <div style="height:18px;"></div>

    <label>Parameters <span style="font-weight:400; text-transform:none; letter-spacing:0; font-size:0.72rem; color:var(--text-muted);">All start at Default (model decides). Slide to override.</span></label>
    <div class="params-grid">
      <div class="param-row" title="Controls randomness. Lower = more focused and predictable. Higher = more creative and varied. Most models default to 0.7 or 1.0.">
        <span class="param-label">Temperature</span>
        <input type="range" min="0" max="2" step="0.05" bind:value={temperature} class="param-slider" />
        <span class="param-value">{temperature === 0 ? 'Default' : temperature}</span>
      </div>
      <div class="param-row" title="Nucleus sampling. Only considers tokens whose cumulative probability reaches this threshold. Lower = fewer token choices, more predictable. Most models default to 0.9 or 0.95.">
        <span class="param-label">Top P</span>
        <input type="range" min="0" max="1" step="0.05" bind:value={top_p} class="param-slider" />
        <span class="param-value">{top_p === 0 ? 'Default' : top_p}</span>
      </div>
      <div class="param-row" title="Limits token selection to the top K most likely choices. Lower = more focused. Higher = more variety. Common defaults are 20 to 64.">
        <span class="param-label">Top K</span>
        <input type="range" min="0" max="100" step="1" bind:value={top_k} class="param-slider" />
        <span class="param-value">{top_k === 0 ? 'Default' : top_k}</span>
      </div>
      <div class="param-row" title="Maximum number of tokens the model can generate in a single response. Ollama default is unlimited (generates until the model stops naturally). Set this to cap response length.">
        <span class="param-label">Max Tokens</span>
        <input type="range" min="0" max="8192" step="128" bind:value={max_tokens} class="param-slider" />
        <span class="param-value">{max_tokens === 0 ? 'Default' : max_tokens}</span>
      </div>
      <div class="param-row" title="How many tokens of conversation history the model can see at once. Larger = more context but uses more memory. On 36GB Apple Silicon: 8B models handle 128K, 27B models handle 64K. Ollama default is usually 2048.">
        <span class="param-label">Context Window</span>
        <input type="range" min="0" max="262144" step="2048" bind:value={num_ctx} class="param-slider" />
        <span class="param-value">{num_ctx === 0 ? 'Default' : (num_ctx >= 1024 ? Math.round(num_ctx / 1024) + 'K' : num_ctx)}</span>
      </div>
      <div class="param-row" title="Penalizes the model for repeating the same words or phrases. Higher = less repetition. 1.0 = no penalty. Most models default to 1.0 or 1.1.">
        <span class="param-label">Repeat Penalty</span>
        <input type="range" min="0" max="2" step="0.05" bind:value={repeat_penalty} class="param-slider" />
        <span class="param-value">{repeat_penalty === 0 ? 'Default' : repeat_penalty}</span>
      </div>
    </div>

    <div style="height:20px;"></div>
    <div style="display:flex; gap:8px;">
      <button class="btn primary" style="flex:1;" on:click={save}>
        {editId ? 'Save Changes' : 'Create Profile'}
      </button>
      {#if editId}
        <button class="btn" on:click={cancelEdit}>Cancel</button>
      {/if}
    </div>
    {#if error}<div class="msg-error">{error}</div>{/if}
    {#if ok}<div class="msg-success">{ok}</div>{/if}
  </div>
  <div class="card">
    <h2>Your Profiles</h2>
    <div class="list">
      {#each profiles as p}
        <div class="item" style="cursor:pointer;" class:active-item={editId === p.id} on:click={() => editProfile(p)}>
          <div class="row" style="align-items:center;">
            <div class="col">
              <div style="font-weight:600;">{p.name}</div>
              <small class="mono">{p.base_model}</small>
              {#if p.system_prompt}
                <div style="color:var(--text-muted); font-size:0.8rem; margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:300px;">
                  {p.system_prompt}
                </div>
              {/if}
              {#if p.params}
                <div style="display:flex; gap:8px; margin-top:4px; flex-wrap:wrap;">
                  {#if p.params.temperature != null}
                    <span class="badge">temp: {p.params.temperature}</span>
                  {/if}
                  {#if p.params.top_p != null}
                    <span class="badge">top_p: {p.params.top_p}</span>
                  {/if}
                  {#if p.params.num_predict != null}
                    <span class="badge">tokens: {p.params.num_predict}</span>
                  {/if}
                  {#if p.params.num_ctx != null}
                    <span class="badge">ctx: {p.params.num_ctx >= 1024 ? Math.round(p.params.num_ctx / 1024) + 'K' : p.params.num_ctx}</span>
                  {/if}
                </div>
              {/if}
            </div>
            <div style="display:flex; gap:6px;">
              <button class="btn" on:click|stopPropagation={() => editProfile(p)} style="font-size:0.78rem; padding:5px 12px;">Edit</button>
              <button class="btn danger" on:click|stopPropagation={() => remove(p.id)} style="font-size:0.78rem; padding:5px 12px;">Delete</button>
            </div>
          </div>
        </div>
      {/each}
      {#if profiles.length===0}
        <div class="empty-state">No profiles yet.</div>
      {/if}
    </div>
  </div>
</div>

<style>
  .active-item {
    border-color: var(--gold) !important;
    background: var(--gold-bg) !important;
  }

  .params-grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .param-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .param-label {
    font-size: 0.82rem;
    color: var(--text-secondary);
    width: 110px;
    flex-shrink: 0;
  }
  .param-slider {
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    border-radius: 2px;
    background: var(--border);
    outline: none;
    border: none;
    padding: 0;
    box-shadow: none;
  }
  .param-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--gold);
    cursor: pointer;
    border: 2px solid var(--card);
    box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  }
  .param-value {
    font-size: 0.82rem;
    color: var(--text);
    font-variant-numeric: tabular-nums;
    width: 60px;
    text-align: right;
    flex-shrink: 0;
  }

  .preset-section {
    margin-bottom: 20px;
  }
  .preset-grid {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  .preset-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: var(--card);
    border: 1.5px solid var(--border-light);
    border-radius: var(--radius);
    cursor: pointer;
    font-family: inherit;
    text-align: left;
    transition: all 0.15s;
    flex: 1;
    min-width: 180px;
  }
  .preset-card:hover {
    border-color: var(--gold);
    background: var(--gold-bg);
  }
  .preset-icon {
    font-size: 1.4rem;
    flex-shrink: 0;
  }
  .preset-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text);
  }
  .preset-desc {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 2px;
  }

  @media (max-width: 768px) {
    .preset-grid { flex-direction: column; }
    .preset-card { min-width: 0; }
  }
</style>
