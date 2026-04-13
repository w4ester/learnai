import { writable, get } from 'svelte/store';

export type Theme = {
  id: string;
  name: string;
  accentWord: string;
  brand: string;
  brandLight: string;
  brandBg: string;
  brandBorder: string;
  accent: string;
  accentLight: string;
  accentBg: string;
  headerBg: string;
  accentText: string;
  tagline: string;
  chatPlaceholder: string;
  pageTitle: string;
  themeColor: string;
};

const learnai: Theme = {
  id: 'learnai',
  name: 'LearnAI',
  accentWord: 'AI',

  brand: '#4a90d9',
  brandLight: '#5ba3ec',
  brandBg: 'rgba(74, 144, 217, 0.12)',
  brandBorder: 'rgba(74, 144, 217, 0.25)',
  accent: '#e8b83a',
  accentLight: '#f5c542',
  accentBg: 'rgba(232, 184, 58, 0.12)',
  headerBg: '#2c3e50',
  accentText: '#5ba3ec',

  tagline: 'Learn AI by building with it',
  chatPlaceholder: 'Message LearnAI...',
  pageTitle: 'LearnAI',
  themeColor: '#4a90d9',
};

export const currentTheme = writable<Theme>(learnai);

export function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.style.setProperty('--brand', theme.brand);
  root.style.setProperty('--brand-light', theme.brandLight);
  root.style.setProperty('--brand-bg', theme.brandBg);
  root.style.setProperty('--brand-border', theme.brandBorder);
  root.style.setProperty('--gold', theme.accent);
  root.style.setProperty('--gold-light', theme.accentLight);
  root.style.setProperty('--gold-bg', theme.accentBg);
  root.style.setProperty('--header-bg', theme.headerBg);
  root.style.setProperty('--accent-text', theme.accentText);

  document.title = theme.pageTitle;
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', theme.themeColor);
}

export function initTheme() {
  applyTheme(get(currentTheme));
}
