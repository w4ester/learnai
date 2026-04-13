import { writable, get } from 'svelte/store';
import { sendMessage } from './api';
import { activeFileIds } from './rag';

export const selectedModel = writable<string>('');
// Sidebar defaults to open on desktop, closed on mobile (≤768px)
const initialSidebarOpen = typeof window !== 'undefined' ? window.innerWidth > 768 : true;
export const sidebarOpen = writable<boolean>(initialSidebarOpen);
export const chatList = writable<Array<{ id: string; title?: string; updatedAt: string }>>([]);
export const modelList = writable<Array<{ id: string }>>([]);

// Pending message state — survives navigation
export type PendingMsg = {
  chatId: string;
  busy: boolean;
  error: string | null;
  resultMessages: Array<{ role: string; content: string; createdAt: string }> | null;
};
export const pendingMessage = writable<PendingMsg | null>(null);

// Workshop CTA auto-send — set by Workshops page, consumed once by Chat page
export const workshopAutoSend = writable<{ chatId: string; text: string } | null>(null);

export async function sendChatMessage(
  chatId: string,
  input: string,
  opts: { profileId?: string; useRag?: boolean }
) {
  pendingMessage.set({ chatId, busy: true, error: null, resultMessages: null });
  try {
    let files: Array<{ type: 'file' | 'collection'; id: string }> | undefined;
    const ids = get(activeFileIds);
    if (opts.useRag && ids.length > 0) files = ids.map(id => ({ type: 'file' as const, id }));

    const res = await sendMessage(chatId, {
      model: opts.profileId ? undefined : (get(selectedModel) || undefined),
      profile_id: opts.profileId || undefined,
      message: { role: 'user', content: input },
      files
    });
    pendingMessage.set({ chatId, busy: false, error: null, resultMessages: res.messages });

    // Update sidebar title if it came back from the server
    if (res.chat?.title) {
      chatList.update(list => list.map(c => c.id === chatId ? { ...c, title: res.chat.title } : c));
    }
  } catch (e: any) {
    pendingMessage.set({ chatId, busy: false, error: e?.message || 'Failed to send', resultMessages: null });
  }
}
