/**
 * James Design Studio - Core JavaScript
 * Handles Dark/Light Mode, Mobile Navigation, and Global UI Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Theme Management (Dark / Light)
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const savedTheme = localStorage.getItem('studio-theme') || 'dark';

  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('studio-theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggleBtn) return;
    const icon = themeToggleBtn.querySelector('i');
    if (icon) {
      if (theme === 'light') {
        icon.setAttribute('data-lucide', 'moon');
      } else {
        icon.setAttribute('data-lucide', 'sun');
      }
      if (window.lucide) {
        lucide.createIcons();
      }
    }
  }

  // 2. Mobile Menu Navigation
  const mobileToggle = document.getElementById('mobile-menu-toggle');
  const navMenu = document.getElementById('navbar-menu');

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      const isExpanded = navMenu.classList.contains('active');
      mobileToggle.setAttribute('aria-expanded', isExpanded);
    });
  }

  // 3. Auto-Dismiss Alert Messages
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      });
    }
    // Auto fade after 6 seconds
    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      }
    }, 6000);
  });

  // 4. Initialize Lucide Icons if loaded
  if (window.lucide) {
    lucide.createIcons();
  }
});
