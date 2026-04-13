<script lang="ts">
  import { onMount } from 'svelte';
  import { listSkills, createSkill, updateSkill, deleteSkill } from '../lib/api';
  import type { SkillOut } from '../lib/api';

  let skills: SkillOut[] = [];
  let editId: string | null = null;

  let name = '';
  let triggers = '';
  let system_prompt = '';
  let token_budget = 800;
  let model_min = '7B';
  let enabled = true;

  // Examples as structured pairs
  let examplePairs: Array<{ user: string; assistant: string }> = [];

  // Schema as structured fields
  let schemaFields: Array<{ name: string; type: string }> = [];

  let error: string | null = null;
  let ok: string | null = null;

  async function load() {
    try { skills = await listSkills(); } catch {}
  }
  onMount(load);

  function addExample() {
    examplePairs = [...examplePairs, { user: '', assistant: '' }];
  }
  function removeExample(i: number) {
    examplePairs = examplePairs.filter((_, idx) => idx !== i);
  }

  function addSchemaField() {
    schemaFields = [...schemaFields, { name: '', type: 'string' }];
  }
  function removeSchemaField(i: number) {
    schemaFields = schemaFields.filter((_, idx) => idx !== i);
  }

  function editSkill(s: SkillOut) {
    editId = s.id;
    name = s.name;
    triggers = s.triggers;
    system_prompt = s.system_prompt;
    token_budget = s.token_budget || 800;
    model_min = s.model_min || '7B';
    enabled = s.enabled !== false;

    // Parse examples
    if (s.examples && Array.isArray(s.examples)) {
      examplePairs = s.examples.map((ex: any) => ({ user: ex.user || '', assistant: ex.assistant || '' }));
    } else {
      examplePairs = [];
    }

    // Parse schema
    if (s.output_schema && typeof s.output_schema === 'object') {
      schemaFields = Object.entries(s.output_schema).map(([n, t]) => ({ name: n, type: String(t) }));
    } else {
      schemaFields = [];
    }

    ok = null; error = null;
  }

  function cancelEdit() {
    editId = null;
    name = ''; triggers = ''; system_prompt = '';
    token_budget = 800; model_min = '7B'; enabled = true;
    examplePairs = []; schemaFields = [];
    ok = null; error = null;
  }

  function buildExamplesJson(): any[] {
    return examplePairs.filter(p => p.user.trim() || p.assistant.trim());
  }

  function buildSchemaJson(): Record<string, string> | null {
    const valid = schemaFields.filter(f => f.name.trim());
    if (!valid.length) return null;
    const obj: Record<string, string> = {};
    valid.forEach(f => { obj[f.name.trim()] = f.type; });
    return obj;
  }

  async function save() {
    try {
      error = null; ok = null;
      const data = {
        name, triggers, system_prompt,
        examples: buildExamplesJson(),
        output_schema: buildSchemaJson(),
        token_budget, model_min, enabled,
      };
      if (editId) {
        await updateSkill(editId, data);
        ok = 'Skill updated';
      } else {
        await createSkill(data);
        ok = 'Skill created';
      }
      cancelEdit();
      await load();
    } catch (e: any) { error = e?.message || 'Failed'; }
  }

  async function remove(id: string) {
    try {
      await deleteSkill(id);
      if (editId === id) cancelEdit();
      await load();
    } catch (e: any) { error = e?.message || 'Failed'; }
  }

  async function toggleEnabled(s: SkillOut) {
    try {
      await updateSkill(s.id, {
        name: s.name, triggers: s.triggers, system_prompt: s.system_prompt,
        examples: s.examples, output_schema: s.output_schema,
        token_budget: s.token_budget, model_min: s.model_min,
        enabled: !s.enabled,
      });
      await load();
    } catch {}
  }
</script>

<div class="grid2">
  <div class="card">
    <h2>{editId ? 'Edit Skill' : 'New Skill'}</h2>

    <label>Name</label>
    <input bind:value={name} placeholder="perkins-grant" />
    <div style="height:12px;"></div>

    <label>Triggers <span class="label-hint">(comma-separated keywords)</span></label>
    <input bind:value={triggers} placeholder="perkins, SMARTIE, grant narrative, IRC" />
    <div style="height:12px;"></div>

    <label>System Prompt</label>
    <textarea rows="4" bind:value={system_prompt} placeholder="You are a Perkins grant analyst. Extract SMARTIE goals..."></textarea>
    <div style="height:16px;"></div>

    <!-- Examples builder -->
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
      <label style="margin:0;">Examples <span class="label-hint">few-shot pairs</span></label>
      <button class="btn" style="font-size:0.75rem; padding:4px 12px;" on:click={addExample}>+ Add</button>
    </div>
    {#if examplePairs.length === 0}
      <div style="color:var(--text-muted); font-size:0.82rem; font-style:italic; padding:8px 0;">No examples yet. Add a few-shot pair to teach the model the expected format.</div>
    {/if}
    {#each examplePairs as pair, i}
      <div class="example-pair">
        <div class="example-header">
          <span class="example-num">Example {i + 1}</span>
          <button class="example-remove" on:click={() => removeExample(i)}>&times;</button>
        </div>
        <div style="margin-bottom:6px;">
          <span class="field-label">User says:</span>
          <textarea rows="2" bind:value={pair.user} placeholder="The CTE program will serve 200 students by June 2026..."></textarea>
        </div>
        <div>
          <span class="field-label">Assistant responds:</span>
          <textarea rows="2" bind:value={pair.assistant} placeholder="goal: serve 200 CTE students, deadline: June 2026..."></textarea>
        </div>
      </div>
    {/each}
    <div style="height:16px;"></div>

    <!-- Schema builder -->
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
      <label style="margin:0;">Output Schema <span class="label-hint">validation fields</span></label>
      <button class="btn" style="font-size:0.75rem; padding:4px 12px;" on:click={addSchemaField}>+ Add Field</button>
    </div>
    {#if schemaFields.length === 0}
      <div style="color:var(--text-muted); font-size:0.82rem; font-style:italic; padding:8px 0;">No schema. Add fields to validate the model's JSON output.</div>
    {/if}
    {#each schemaFields as field, i}
      <div class="schema-row">
        <input bind:value={field.name} placeholder="field name" class="schema-name" />
        <select bind:value={field.type} class="schema-type">
          <option value="string">string</option>
          <option value="number">number</option>
          <option value="boolean">boolean</option>
          <option value="array">array</option>
          <option value="object">object</option>
        </select>
        <button class="example-remove" on:click={() => removeSchemaField(i)}>&times;</button>
      </div>
    {/each}
    <div style="height:16px;"></div>

    <div class="row">
      <div class="col">
        <label>Token Budget</label>
        <input type="number" bind:value={token_budget} />
      </div>
      <div class="col">
        <label>Model Min</label>
        <input bind:value={model_min} placeholder="7B" />
      </div>
    </div>
    <div style="height:12px;"></div>

    <label style="display:inline-flex; align-items:center; gap:8px; text-transform:none; letter-spacing:0; cursor:pointer; font-weight:500;">
      <input type="checkbox" bind:checked={enabled} style="width:auto;" />
      Enabled
    </label>
    <div style="height:20px;"></div>

    <div style="display:flex; gap:8px;">
      <button class="btn primary" style="flex:1;" on:click={save}>
        {editId ? 'Save Changes' : 'Create Skill'}
      </button>
      {#if editId}
        <button class="btn" on:click={cancelEdit}>Cancel</button>
      {/if}
    </div>
    {#if error}<div class="msg-error">{error}</div>{/if}
    {#if ok}<div class="msg-success">{ok}</div>{/if}
  </div>

  <div class="card">
    <h2>Your Skills</h2>
    <div class="list">
      {#each skills as s}
        <div class="skill-item" class:active-item={editId === s.id} on:click={() => editSkill(s)}>
          <div class="skill-info">
            <div class="skill-header">
              <span class="skill-name">{s.name}</span>
              <div class="skill-badges">
                {#if !s.enabled}
                  <span class="badge" style="opacity:0.6;">disabled</span>
                {/if}
                {#if s.examples?.length}
                  <span class="badge">{s.examples.length} {s.examples.length === 1 ? 'example' : 'examples'}</span>
                {/if}
                {#if s.output_schema}
                  <span class="badge">schema</span>
                {/if}
              </div>
            </div>
            <div class="skill-triggers">Triggers: {s.triggers}</div>
            <div class="skill-prompt">{s.system_prompt}</div>
          </div>
          <div class="skill-actions">
            <button class="skill-btn" on:click|stopPropagation={() => toggleEnabled(s)}>
              {s.enabled ? 'Disable' : 'Enable'}
            </button>
            <button class="skill-btn" on:click|stopPropagation={() => editSkill(s)}>Edit</button>
            <button class="skill-btn danger" on:click|stopPropagation={() => remove(s.id)}>Delete</button>
          </div>
        </div>
      {/each}
      {#if skills.length === 0}
        <div class="empty-state">No skills yet. Create one to auto-route messages.</div>
      {/if}
    </div>
  </div>
</div>

<style>
  .active-item {
    border-color: var(--gold) !important;
    background: var(--gold-bg) !important;
  }

  .skill-item {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px 16px;
    border: 1.5px solid var(--border-light);
    border-radius: var(--radius);
    background: var(--card-alt);
    cursor: pointer;
    transition: all var(--duration) var(--ease);
  }
  .skill-item:hover {
    border-color: var(--border);
    background: var(--card);
    box-shadow: 0 2px 8px rgba(26, 22, 18, 0.05);
  }
  .skill-info {
    min-width: 0;
    flex: 1;
  }
  .skill-header {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 6px;
  }
  .skill-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text);
  }
  .skill-badges {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  .skill-triggers {
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 2px;
    word-break: break-word;
  }
  .skill-prompt {
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.4;
  }
  .skill-actions {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    padding-top: 8px;
    border-top: 1px solid var(--border-light);
  }
  .skill-btn {
    flex: 1;
    min-width: 70px;
    padding: 6px 12px;
    font-size: 0.76rem;
    font-weight: 500;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    cursor: pointer;
    transition: all var(--duration) var(--ease);
    font-family: inherit;
  }
  .skill-btn:hover {
    background: var(--bg-warm);
    border-color: var(--border-strong);
  }
  .skill-btn.danger {
    color: var(--brand);
    border-color: var(--brand-border);
  }
  .skill-btn.danger:hover {
    background: var(--brand-bg);
    border-color: var(--brand);
  }
  .label-hint {
    text-transform: none;
    letter-spacing: 0;
    font-weight: 400;
    opacity: 0.6;
  }
  .field-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    display: block;
    margin-bottom: 4px;
  }

  .example-pair {
    background: var(--card-alt);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
  }
  .example-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .example-num {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .example-remove {
    width: 22px;
    height: 22px;
    border-radius: 4px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-size: 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: inherit;
    transition: all 0.15s;
    padding: 0;
    flex-shrink: 0;
  }
  .example-remove:hover {
    background: var(--danger-bg);
    color: var(--brand);
  }

  .schema-row {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 6px;
  }
  .schema-name {
    flex: 1;
  }
  .schema-type {
    width: 120px;
    flex-shrink: 0;
  }
</style>
