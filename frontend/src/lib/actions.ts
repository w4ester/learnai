export function clickOutside(node: HTMLElement) {
  function handle(e: MouseEvent) {
    if (!node.contains(e.target as Node)) {
      node.dispatchEvent(new CustomEvent('clickoutside'));
    }
  }
  document.addEventListener('mousedown', handle, true);
  return {
    destroy() {
      document.removeEventListener('mousedown', handle, true);
    }
  };
}
