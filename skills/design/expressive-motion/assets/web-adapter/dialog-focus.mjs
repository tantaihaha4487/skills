// Browser focus semantics around the source immersive lifecycle. Presentation
// and reduced/performance policy remain owned by ImmersiveController.
export class DialogFocus {
  constructor(dialog, fallback) { this.dialog = dialog; this.fallback = fallback; this.opener = null; }
  remember() { if (!this.opener) this.opener = document.activeElement; }
  open() {
    if (!this.opener) this.opener = document.activeElement;
    if (!this.dialog.contains(document.activeElement)) this.dialog.querySelector('button')?.focus({ preventScroll: true });
  }
  close() {
    const active = document.activeElement;
    if (this.dialog.contains(active) || active === document.body) {
      const target = this.opener?.isConnected && !this.opener.closest('[inert]') ? this.opener : this.fallback;
      target?.focus({ preventScroll: true });
    }
    this.opener = null;
  }
  key(event) {
    if (event.key !== 'Tab' || this.dialog.hidden) return false;
    const nodes = [...this.dialog.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled),[tabindex="0"]')]
      .filter(node => node.getClientRects().length && !node.closest('[hidden],[inert]'));
    if (!nodes.length) return false;
    const index = nodes.indexOf(document.activeElement);
    const next = event.shiftKey ? (index <= 0 ? nodes.length - 1 : index - 1) : (index + 1) % nodes.length;
    event.preventDefault(); nodes[next].focus(); return true;
  }
}
