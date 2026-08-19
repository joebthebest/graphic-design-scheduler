/**
 * Portfolio Filtering and Lightbox Modal
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Portfolio Category Filtering
  const filterButtons = document.querySelectorAll('.filter-btn');
  const portfolioCards = document.querySelectorAll('.portfolio-card');

  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filterValue = btn.getAttribute('data-filter');

      portfolioCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (filterValue === 'all' || cardCategory === filterValue) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });

  // 2. Lightbox Modal Interaction
  const lightboxModal = document.getElementById('lightbox-modal');
  const lightboxClose = document.getElementById('lightbox-close');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxTitle = document.getElementById('lightbox-title');
  const lightboxCategory = document.getElementById('lightbox-category');
  const lightboxClient = document.getElementById('lightbox-client');
  const lightboxDesc = document.getElementById('lightbox-desc');
  const lightboxTools = document.getElementById('lightbox-tools');
  const lightboxBookBtn = document.getElementById('lightbox-book-btn');

  if (lightboxModal) {
    portfolioCards.forEach(card => {
      card.addEventListener('click', () => {
        const imgUrl = card.getAttribute('data-img');
        const title = card.getAttribute('data-title');
        const category = card.getAttribute('data-category-display');
        const client = card.getAttribute('data-client');
        const desc = card.getAttribute('data-desc');
        const tools = card.getAttribute('data-tools');
        const serviceSlug = card.getAttribute('data-service-slug');

        if (lightboxImg) lightboxImg.src = imgUrl;
        if (lightboxTitle) lightboxTitle.textContent = title;
        if (lightboxCategory) lightboxCategory.textContent = category;
        if (lightboxDesc) lightboxDesc.textContent = desc;
        if (lightboxTools) lightboxTools.textContent = tools;

        if (lightboxBookBtn) {
          if (serviceSlug) {
            lightboxBookBtn.href = `/schedule/book/${serviceSlug}/`;
            lightboxBookBtn.style.display = 'inline-flex';
          } else {
            lightboxBookBtn.href = '/schedule/book/';
            lightboxBookBtn.style.display = 'inline-flex';
          }
        }

        lightboxModal.classList.add('active');
        document.body.style.overflow = 'hidden';
      });
    });

    function closeLightbox() {
      lightboxModal.classList.remove('active');
      document.body.style.overflow = '';
    }

    if (lightboxClose) {
      lightboxClose.addEventListener('click', closeLightbox);
    }

    lightboxModal.addEventListener('click', (e) => {
      if (e.target === lightboxModal) {
        closeLightbox();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && lightboxModal.classList.contains('active')) {
        closeLightbox();
      }
    });
  }
});
