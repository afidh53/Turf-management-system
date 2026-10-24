document.addEventListener('DOMContentLoaded', () => {
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');

  if (menuToggle && menu) {
    const closeMenu = () => {
      menu.classList.remove('is-open');
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.setAttribute('aria-label', 'Open navigation menu');
    };

    menuToggle.addEventListener('click', () => {
      const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!isOpen));
      menuToggle.setAttribute('aria-label', isOpen ? 'Open navigation menu' : 'Close navigation menu');
      menu.classList.toggle('is-open', !isOpen);
    });

    menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
  }

  document.querySelectorAll('[data-dismiss-flash]').forEach((button) => {
    button.addEventListener('click', () => button.closest('.flash-message')?.remove());
  });

  const header = document.querySelector('.site-header');
  const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 8);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  const today = new Date();
  const localToday = [today.getFullYear(), String(today.getMonth() + 1).padStart(2, '0'), String(today.getDate()).padStart(2, '0')].join('-');
  document.querySelectorAll('[data-min-date]').forEach((input) => {
    input.min = localToday;
  });

  const searchForm = document.querySelector('[data-availability-search]');
  if (searchForm) {
    searchForm.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!searchForm.reportValidity()) return;

      const formData = new FormData(searchForm);
      const selectedSport = formData.get('sport');
      const selectedTurf = Array.from(document.querySelectorAll('[data-turf-name]')).find((card) => card.dataset.turfName === selectedSport);
      const hint = document.querySelector('[data-search-hint]');

      if (!selectedTurf) {
        if (hint) hint.textContent = 'Choose a listed turf to continue.';
        return;
      }

      const destination = new URL(selectedTurf.dataset.bookingUrl, window.location.href);
      destination.searchParams.set('date', formData.get('booking_date'));
      destination.searchParams.set('time', formData.get('time_slot'));
      window.location.assign(destination.toString());
    });
  }

  const bookingForm = document.querySelector('[data-booking-form]');
  if (bookingForm) {
    const slotInput = bookingForm.querySelector('[data-selected-slot]');
    const slotButtons = bookingForm.querySelectorAll('[data-time-slot]');
    const feedback = bookingForm.querySelector('[data-booking-feedback]');

    slotButtons.forEach((button) => {
      button.addEventListener('click', () => {
        slotButtons.forEach((slotButton) => {
          const selected = slotButton === button;
          slotButton.classList.toggle('is-selected', selected);
          slotButton.setAttribute('aria-pressed', String(selected));
        });
        if (slotInput) slotInput.value = button.dataset.timeSlot || '';
        if (feedback) feedback.textContent = '';
      });
    });

    bookingForm.addEventListener('submit', (event) => {
      if (!slotInput?.value) {
        event.preventDefault();
        if (feedback) feedback.textContent = 'Please select an available time slot to continue.';
        bookingForm.querySelector('[data-time-slot]')?.focus();
        return;
      }
      if (!bookingForm.reportValidity()) event.preventDefault();
    });
  }

  const passwordForm = document.querySelector('[data-password-form]');
  if (passwordForm) {
    passwordForm.addEventListener('submit', (event) => {
      const password = passwordForm.querySelector('[name="password"]');
      const confirm = passwordForm.querySelector('[name="confirm"]');
      const feedback = passwordForm.querySelector('[data-password-feedback]');
      if (password && confirm && password.value !== confirm.value) {
        event.preventDefault();
        if (feedback) feedback.textContent = 'Your passwords do not match. Please check and try again.';
        confirm.focus();
      } else if (feedback) {
        feedback.textContent = '';
      }
    });
  }

  const revealItems = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && revealItems.length) {
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          currentObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }
});