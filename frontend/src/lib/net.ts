import { authHeader } from './auth';

const rawBase = import.meta.env.VITE_API_BASE ?? 'http://localhost:8080';
const normalizedBase = rawBase.replace(/\/+$/, '');
export const API_BASE = normalizedBase;

function buildUrl(path: string) {
  if (path.startsWith('http')) return path;
  if (!API_BASE) return path;
  const suffix = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE}${suffix}`;
}

export function apiFetch(path: string, init: RequestInit = {}) {
  const headers = { 'Content-Type': 'application/json', ...authHeader(), ...(init.headers || {}) };
  const url = buildUrl(path);
  return fetch(url, { ...init, headers });
}

export async function apiUpload(path: string, fd: FormData) {
  const headers = { ...authHeader() };
  const url = buildUrl(path);
  const res = await fetch(url, { method: 'POST', headers, body: fd });
  if (!res.ok) throw new Error(await res.text());
  return res;
}
