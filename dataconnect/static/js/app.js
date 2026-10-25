/* Confirmación de eliminación con alternativa HTML y foco de teclado. */
(() => {
  'use strict';
  const dialog = document.getElementById('delete-dialog');
  let trigger = null;
  if (dialog && typeof dialog.showModal === 'function') {
    document.querySelectorAll('[data-delete-contact]').forEach(link => {
      link.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        trigger = link;
        document.getElementById('delete-name').textContent = link.dataset.deleteContact;
        document.getElementById('delete-form').action = link.href;
        dialog.showModal();
      });
    });
    dialog.querySelectorAll('[data-close-dialog]').forEach(button => {
      button.addEventListener('click', () => dialog.close());
    });
    dialog.addEventListener('click', event => {
      if (event.target === dialog) {
        const bounds = dialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right ||
            event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
      }
    });
    dialog.addEventListener('close', () => trigger?.focus());
  }

  const errors = document.querySelector('[data-error-summary]');
  if (errors) errors.focus();
})();
