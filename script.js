/* ==========================================================================
   Galaxy Shooters — Official Website JavaScript Engine
   Interactive logic, animations, modals & form handlers (@harshalGamearena)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ------------------------------------------------------------------------
   * 1. Top Equalizer Bar Generator (Matches Figma Header Components)
   * ------------------------------------------------------------------------ */
  function generateEqualizerBars() {
    const container = document.getElementById('equalizer-bars');
    if (!container) return;

    // Heights pattern replicating Figma vertical bar instances
    const pattern = [
      121, 85, 151, 79, 165, 118, 182, 103, 140, 179, 121, 87, 121, 85, 151,
      79, 165, 118, 182, 103, 140, 179, 121, 100, 79, 76, 54, 85, 52, 66, 72,
      43, 38, 74, 64, 72, 46, 23, 13, 63, 83, 64, 29, 22, 69, 47, 75, 44, 29,
      36, 75, 56, 33, 36, 76, 29, 36, 46, 61, 36, 73, 53, 42, 73, 36, 29, 52,
      73, 36, 73, 52, 73, 52, 73, 36, 36, 73, 36, 73, 36, 61, 36, 36, 61, 36,
      36, 61, 118, 182, 103, 140, 179, 121, 87, 121, 85, 151, 79, 165, 118, 182
    ];

    container.innerHTML = '';
    const fragment = document.createDocumentFragment();

    pattern.forEach((h, idx) => {
      const bar = document.createElement('div');
      bar.className = 'eq-bar';
      // Scale height relative to container max height
      const normalizedHeight = Math.min(130, Math.max(12, h * 0.7));
      bar.style.height = `${normalizedHeight}px`;

      // Subtle pulse animation staggered by index
      bar.style.animation = `pulseBar ${1.5 + (idx % 5) * 0.3}s ease-in-out infinite alternate`;
      bar.style.animationDelay = `${(idx % 10) * 0.1}s`;

      fragment.appendChild(bar);
    });

    container.appendChild(fragment);
  }

  // Inject keyframes for equalizer pulsing
  const styleSheet = document.createElement('style');
  styleSheet.type = 'text/css';
  styleSheet.innerText = `
    @keyframes pulseBar {
      0% { transform: scaleY(0.85); opacity: 0.45; }
      100% { transform: scaleY(1.15); opacity: 0.85; }
    }
  `;
  document.head.appendChild(styleSheet);
  generateEqualizerBars();

  /* ------------------------------------------------------------------------
   * 2. Background Space Starfield Particle Canvas
   * ------------------------------------------------------------------------ */
  function initSpaceBackground() {
    const canvas = document.getElementById('space-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const stars = Array.from({ length: 140 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      radius: Math.random() * 1.5 + 0.3,
      alpha: Math.random() * 0.8 + 0.2,
      speed: Math.random() * 0.3 + 0.05
    }));

    function animate() {
      ctx.clearRect(0, 0, width, height);

      stars.forEach(star => {
        star.y += star.speed;
        if (star.y > height) {
          star.y = 0;
          star.x = Math.random() * width;
        }

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${star.alpha})`;
        ctx.fill();
      });

      requestAnimationFrame(animate);
    }

    animate();
  }
  initSpaceBackground();

  /* ------------------------------------------------------------------------
   * 3. Navigation Scroll & Active Link Tracking
   * ------------------------------------------------------------------------ */
  const navButtons = document.querySelectorAll('.nav-btn');
  const sections = document.querySelectorAll('section');

  navButtons.forEach(btn => {
    btn.addEventListener('click', e => {
      const targetId = btn.getAttribute('data-target');
      const targetSection = document.getElementById(targetId);

      if (targetSection) {
        e.preventDefault();
        targetSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  window.addEventListener('scroll', () => {
    let current = '';
    const scrollPos = window.scrollY + 200;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        current = section.getAttribute('id');
      }
    });

    navButtons.forEach(btn => {
      btn.classList.remove('active');
      if (btn.getAttribute('data-target') === current) {
        btn.classList.add('active');
      }
    });
  });

  /* ------------------------------------------------------------------------
   * 4. Game Visuals Gallery Slider & Lightbox
   * ------------------------------------------------------------------------ */
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  const prevBtn = document.getElementById('gallery-prev');
  const nextBtn = document.getElementById('gallery-next');
  let currentSlide = 0;

  function showSlide(index) {
    if (slides.length === 0) return;
    slides.forEach(s => s.classList.remove('active'));
    dots.forEach(d => d.classList.remove('active'));

    currentSlide = (index + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
    if (dots[currentSlide]) dots[currentSlide].classList.add('active');
  }

  if (prevBtn && nextBtn) {
    prevBtn.addEventListener('click', () => showSlide(currentSlide - 1));
    nextBtn.addEventListener('click', () => showSlide(currentSlide + 1));
  }

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const index = parseInt(dot.getAttribute('data-index'), 10);
      showSlide(index);
    });
  });

  // Lightbox functionality
  const lightboxModal = document.getElementById('lightbox-modal');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxCaption = document.getElementById('lightbox-caption');
  const closeLightboxBtn = document.getElementById('close-lightbox');

  document.querySelectorAll('.visual-img').forEach(img => {
    img.addEventListener('click', () => {
      if (lightboxModal && lightboxImg) {
        lightboxImg.src = img.src;
        lightboxImg.alt = img.alt;
        if (lightboxCaption) {
          lightboxCaption.textContent = img.alt || 'Galaxy Shooters Visual';
        }
        lightboxModal.classList.add('active');
        lightboxModal.setAttribute('aria-hidden', 'false');
      }
    });
  });

  if (closeLightboxBtn && lightboxModal) {
    closeLightboxBtn.addEventListener('click', () => {
      lightboxModal.classList.remove('active');
      lightboxModal.setAttribute('aria-hidden', 'true');
    });
    lightboxModal.addEventListener('click', e => {
      if (e.target === lightboxModal) {
        lightboxModal.classList.remove('active');
        lightboxModal.setAttribute('aria-hidden', 'true');
      }
    });
  }

  /* ------------------------------------------------------------------------
   * 5. Play Online Modal, Download Modal & Clipboard Copy Handlers
   * ------------------------------------------------------------------------ */
  const playBtn = document.getElementById('open-play-modal');
  const playModal = document.getElementById('play-game-modal');
  const closePlayBtn = document.getElementById('close-play-modal');
  const switchToDownloadBtn = document.getElementById('switch-to-download');

  if (playBtn && playModal) {
    playBtn.addEventListener('click', () => {
      showToast('🚀 Play Online (Browser) is Coming Soon! Check back soon.');
      playModal.classList.add('active');
      playModal.setAttribute('aria-hidden', 'false');
    });
  }

  if (closePlayBtn && playModal) {
    closePlayBtn.addEventListener('click', () => {
      playModal.classList.remove('active');
      playModal.setAttribute('aria-hidden', 'true');
    });

    playModal.addEventListener('click', e => {
      if (e.target === playModal) {
        playModal.classList.remove('active');
        playModal.setAttribute('aria-hidden', 'true');
      }
    });
  }

  if (switchToDownloadBtn && playModal) {
    switchToDownloadBtn.addEventListener('click', () => {
      playModal.classList.remove('active');
      playModal.setAttribute('aria-hidden', 'true');
      const downloadModal = document.getElementById('download-modal');
      if (downloadModal) {
        downloadModal.classList.add('active');
        downloadModal.setAttribute('aria-hidden', 'false');
      }
    });
  }

  const downloadBtn = document.getElementById('open-download-modal');
  const downloadModal = document.getElementById('download-modal');
  const closeDownloadBtn = document.getElementById('close-download-modal');

  if (downloadBtn && downloadModal) {
    downloadBtn.addEventListener('click', () => {
      downloadModal.classList.add('active');
      downloadModal.setAttribute('aria-hidden', 'false');
    });
  }

  if (closeDownloadBtn && downloadModal) {
    closeDownloadBtn.addEventListener('click', () => {
      downloadModal.classList.remove('active');
      downloadModal.setAttribute('aria-hidden', 'true');
    });

    downloadModal.addEventListener('click', e => {
      if (e.target === downloadModal) {
        downloadModal.classList.remove('active');
        downloadModal.setAttribute('aria-hidden', 'true');
      }
    });
  }

  // Copy code to clipboard handler
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-copy');
      const targetEl = document.getElementById(targetId);

      if (targetEl) {
        const textToCopy = targetEl.textContent;
        navigator.clipboard.writeText(textToCopy).then(() => {
          showToast('Copied command to clipboard!');
          const icon = btn.querySelector('i');
          if (icon) {
            icon.className = 'fa-solid fa-check';
            setTimeout(() => {
              icon.className = 'fa-regular fa-copy';
            }, 2000);
          }
        }).catch(err => {
          console.error('Copy failed:', err);
          showToast('Failed to copy command.');
        });
      }
    });
  });

  /* ------------------------------------------------------------------------
   * 6. Support Contact Form Submission
   * ------------------------------------------------------------------------ */
  const supportForm = document.getElementById('support-form');

  if (supportForm) {
    supportForm.addEventListener('submit', e => {
      e.preventDefault();

      const emailInput = document.getElementById('email-input');
      const commentsInput = document.getElementById('comments-input');

      const email = emailInput ? emailInput.value.trim() : '';
      const comments = commentsInput ? commentsInput.value.trim() : '';

      if (!email || !validateEmail(email)) {
        showToast('Please enter a valid email address.');
        if (emailInput) emailInput.focus();
        return;
      }

      if (!comments) {
        showToast('Please enter your comments.');
        if (commentsInput) commentsInput.focus();
        return;
      }

      // Simulate successful transmission
      showToast('Thank you! Your message has been sent to @harshalGamearena.');
      supportForm.reset();
    });
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  /* ------------------------------------------------------------------------
   * 7. Toast Notification System
   * ------------------------------------------------------------------------ */
  function showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

});
