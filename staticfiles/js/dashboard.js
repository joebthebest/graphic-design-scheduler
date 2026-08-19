/**
 * Designer Dashboard Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Status Update Modal
  const statusModal = document.getElementById('status-modal');
  const statusModalClose = document.getElementById('status-modal-close');
  const statusForm = document.getElementById('status-update-form');
  const statusModalTitle = document.getElementById('status-modal-title');
  const statusSelect = document.getElementById('status-select');
  const notesTextarea = document.getElementById('designer-notes-input');

  const editStatusButtons = document.querySelectorAll('.btn-edit-status');

  editStatusButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const ref = btn.getAttribute('data-ref');
      const client = btn.getAttribute('data-client');
      const currentStatus = btn.getAttribute('data-current-status');
      const notes = btn.getAttribute('data-notes') || '';

      if (statusForm) statusForm.action = `/dashboard/appointment/${ref}/status/`;
      if (statusModalTitle) statusModalTitle.textContent = `Update Booking: ${ref} (${client})`;
      if (statusSelect) statusSelect.value = currentStatus;
      if (notesTextarea) notesTextarea.value = notes;

      if (statusModal) statusModal.classList.add('active');
    });
  });

  function closeModal() {
    if (statusModal) statusModal.classList.remove('active');
  }

  if (statusModalClose) {
    statusModalClose.addEventListener('click', closeModal);
  }

  if (statusModal) {
    statusModal.addEventListener('click', (e) => {
      if (e.target === statusModal) closeModal();
    });
  }

  // 2. Quick Copy Helper
  const copyButtons = document.querySelectorAll('.btn-copy');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const textToCopy = btn.getAttribute('data-copy');
      if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
          const originalText = btn.innerHTML;
          btn.innerHTML = '✓ Copied!';
          setTimeout(() => {
            btn.innerHTML = originalText;
          }, 2000);
        });
      }
    });
  });
});
