import { writable, get } from 'svelte/store';
export type RagFile = { id: string; filename: string; size: number };
const KEY = 'learnai.rag.files';
function read(): RagFile[] { const s = localStorage.getItem(KEY); return s ? JSON.parse(s) as RagFile[] : []; }
export const ragFiles = writable<RagFile[]>(read());
export const currentFileId = writable<string | null>(null); // legacy, kept for compat
export const activeFileIds = writable<string[]>([]);
ragFiles.subscribe(v => localStorage.setItem(KEY, JSON.stringify(v)));

export function toggleFileActive(id: string) {
  activeFileIds.update(ids => ids.includes(id) ? ids.filter(i => i !== id) : [...ids, id]);
  // keep legacy store in sync with first active file
  const ids = get(activeFileIds);
  currentFileId.set(ids.length > 0 ? ids[0] : null);
}

export function getActiveFilenames(): string[] {
  const files = get(ragFiles);
  const ids = get(activeFileIds);
  return files.filter(f => ids.includes(f.id)).map(f => f.filename);
}
