import { apiFetch, apiUpload } from './net';
import type { User } from './auth';

export async function me() {
  const res = await apiFetch('/api/auth/me');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<User>;
}

export async function login(email: string, password: string) {
  const res = await apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ token: string; user: User }>;
}

export async function register(email: string, password: string) {
  const res = await apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ token: string; user: User }>;
}

export async function listModels() {
  const res = await apiFetch('/api/models');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ data: Array<{ id: string }> }>;
}

export async function listChats() {
  const res = await apiFetch('/api/chats');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ items: Array<{ id: string; title?: string; updatedAt: string }> }>;
}

export async function createChat(title?: string) {
  const res = await apiFetch('/api/chats', { method: 'POST', body: JSON.stringify(title ? { title } : {}) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ id: string; title?: string }>;
}

export async function deleteChat(id: string) {
  const res = await apiFetch(`/api/chats/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
}

export async function renameChat(id: string, title: string) {
  const res = await apiFetch(`/api/chats/${id}`, { method: 'PATCH', body: JSON.stringify({ title }) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ id: string; title: string }>;
}

export async function getChat(id: string) {
  const res = await apiFetch(`/api/chats/${id}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ chat: { id: string; title?: string }, messages: Array<{ role: string; content: string; createdAt: string }> }>;
}

export async function sendMessage(chatId: string, body: {
  model?: string,
  profile_id?: string,
  message: { role: 'user'|'system'|'assistant'; content: string },
  files?: Array<{ type: 'file' | 'collection'; id: string }>
}) {
  const res = await apiFetch(`/api/chats/${chatId}/message`, { method: 'POST', body: JSON.stringify(body) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ chat: { id: string; title?: string }, messages: Array<{ role: string; content: string; createdAt: string }> }>;
}

export async function listRagFiles() {
  const res = await apiFetch('/api/rag/files');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ items: Array<{ id: string; filename: string; size: number }> }>;
}

export async function deleteRagFile(id: string) {
  const res = await apiFetch(`/api/rag/files/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
}

export async function deleteAllRagFiles() {
  const res = await apiFetch('/api/rag/files', { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
}

export async function uploadRagFile(file: File) {
  const fd = new FormData();
  fd.append('file', file);
  const res = await apiUpload('/api/rag/files', fd);
  return res.json() as Promise<{ id: string; filename: string; size: number }>;
}

export async function listTools() {
  const res = await apiFetch('/api/tools');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ items: Array<{ name: string; schema: any }> }>;
}

export async function callTool(name: string, args: any) {
  const res = await apiFetch('/api/tools/call', { method: 'POST', body: JSON.stringify({ name, args }) });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateTool(description: string, model?: string) {
  const res = await apiFetch('/api/tools/generate', { method: 'POST', body: JSON.stringify({ description, model }) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ name: string; description: string; schema: any; code: string }>;
}

export async function deleteTool(name: string) {
  const res = await apiFetch(`/api/tools/${name}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
}

export async function listProfiles() {
  const res = await apiFetch('/api/profiles');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<Array<{ id: string; name: string; base_model: string }>>;
}

export async function createProfile(p: { name: string; base_model: string; system_prompt?: string; params?: any }) {
  const res = await apiFetch('/api/profiles', { method: 'POST', body: JSON.stringify(p) });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateProfile(id: string, p: { name: string; base_model: string; system_prompt?: string; params?: any }) {
  const res = await apiFetch(`/api/profiles/${id}`, { method: 'PATCH', body: JSON.stringify(p) });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteProfile(id: string) {
  const res = await apiFetch(`/api/profiles/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
}

export async function listPrompts() {
  const res = await apiFetch('/api/prompts');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<Array<{ id: string; name: string; template: string }>>;
}

export async function createPrompt(p: { name: string; template: string }) {
  const res = await apiFetch('/api/prompts', { method: 'POST', body: JSON.stringify(p) });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deletePrompt(id: string) {
  const res = await apiFetch(`/api/prompts/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
}

// Skills
export type SkillData = {
  name: string; triggers: string; system_prompt: string;
  examples?: Array<{ user: string; assistant: string }>;
  output_schema?: Record<string, string>;
  token_budget?: number; model_min?: string; enabled?: boolean;
};
export type SkillOut = SkillData & { id: string; created_at: string };

export async function listSkills() {
  const res = await apiFetch('/api/skills');
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<SkillOut[]>;
}

export async function createSkill(s: SkillData) {
  const res = await apiFetch('/api/skills', { method: 'POST', body: JSON.stringify(s) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<SkillOut>;
}

export async function updateSkill(id: string, s: SkillData) {
  const res = await apiFetch(`/api/skills/${id}`, { method: 'PATCH', body: JSON.stringify(s) });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<SkillOut>;
}

export async function deleteSkill(id: string) {
  const res = await apiFetch(`/api/skills/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await res.text());
}
