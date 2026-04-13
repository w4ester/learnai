import { writable } from 'svelte/store';

export type User = { id: string; email: string; role?: string };

const TOKEN_KEY = 'learnai.jwt';
const USER_KEY = 'learnai.user';

function readToken(): string | null { return localStorage.getItem(TOKEN_KEY); }
function readUser(): User | null { const s = localStorage.getItem(USER_KEY); return s ? JSON.parse(s) as User : null; }

export const token = writable<string | null>(readToken());
export const user = writable<User | null>(readUser());

token.subscribe(v => { v ? localStorage.setItem(TOKEN_KEY, v) : localStorage.removeItem(TOKEN_KEY); });
user.subscribe(v => { v ? localStorage.setItem(USER_KEY, JSON.stringify(v)) : localStorage.removeItem(USER_KEY); });

export function setAuth(t: string, u: User) { token.set(t); user.set(u); }
export function clearAuth() { token.set(null); user.set(null); }

export function authHeader() {
  let t: string | null = null;
  token.subscribe(v => t = v)();
  return t ? { 'Authorization': `Bearer ${t}` } : {};
}
