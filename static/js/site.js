/* ============================================================
   DemoPlast — клиентская логика (ваниль, без фреймворков)
   Бургер-меню · модалка «Заказать звонок» · кнопка настроек cookie
   Формы работают через htmx (см. base.html / form.html).
   ============================================================ */
(function () {
  'use strict';

  /* ---------- Бургер-меню ---------- */
  var burger = document.getElementById('burger');
  var menu = document.getElementById('mobileMenu');
  if (burger && menu) {
    var iOpen = burger.querySelector('[data-burger-open]');
    var iClose = burger.querySelector('[data-burger-close]');
    function setMenu(open) {
      menu.classList.toggle('hidden', !open);
      burger.setAttribute('aria-expanded', String(open));
      if (iOpen) iOpen.classList.toggle('hidden', open);
      if (iClose) iClose.classList.toggle('hidden', !open);
    }
    burger.addEventListener('click', function () {
      setMenu(menu.classList.contains('hidden'));
    });
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { setMenu(false); });
    });
  }

  /* ---------- Модалка «Заказать звонок» ---------- */
  var modal = document.getElementById('callbackModal');
  var lastFocus = null;
  function openModal() {
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.classList.remove('hidden');
    document.documentElement.style.overflow = 'hidden';
    var first = modal.querySelector('input[name="name"]');
    if (first) setTimeout(function () { first.focus(); }, 30);
  }
  function closeModal() {
    if (!modal) return;
    modal.classList.add('hidden');
    document.documentElement.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  // делегирование: любые ссылки на #callback и [data-modal-open] открывают модалку
  document.addEventListener('click', function (e) {
    var open = e.target.closest('a[href$="#callback"], [data-modal-open]');
    if (open) { e.preventDefault(); openModal(); return; }
    if (e.target.closest('[data-modal-close]')) { e.preventDefault(); closeModal(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) closeModal();
  });

  /* ---------- Кнопка «Настройки cookie» в футере ---------- */
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-cookie-settings]')) {
      e.preventDefault();
      var banner = document.getElementById('cookieBanner');
      if (banner) banner.classList.remove('hidden');
    }
  });

  /* ---------- Галерея товара (scroll-snap карусель) ---------- */
  document.querySelectorAll('[data-gallery]').forEach(function (gal) {
    var track = gal.querySelector('[data-gallery-track]');
    if (!track) return;
    var slides = track.children;
    if (slides.length < 2) return;  // нечего листать

    var dots = gal.querySelectorAll('[data-gallery-dot]');
    var thumbs = gal.querySelectorAll('[data-gallery-thumb]');
    var prev = gal.querySelector('[data-gallery-prev]');
    var next = gal.querySelector('[data-gallery-next]');
    var active = 0;

    function goTo(i) {
      i = Math.max(0, Math.min(slides.length - 1, i));
      track.scrollTo({ left: i * track.clientWidth, behavior: 'smooth' });
    }
    function setActive(i) {
      active = i;
      dots.forEach(function (d, di) {
        d.classList.toggle('bg-brand', di === i);
        d.classList.toggle('w-5', di === i);
        d.classList.toggle('w-2', di !== i);
        d.classList.toggle('bg-ink/20', di !== i);
        d.classList.toggle('hover:bg-ink/40', di !== i);
      });
      thumbs.forEach(function (t, ti) {
        t.classList.toggle('border-brand', ti === i);
        t.classList.toggle('border-line', ti !== i);
        t.classList.toggle('hover:border-brand', ti !== i);
      });
    }

    var scrollT;
    track.addEventListener('scroll', function () {
      clearTimeout(scrollT);
      scrollT = setTimeout(function () {
        var i = Math.round(track.scrollLeft / track.clientWidth);
        if (i !== active) setActive(i);
      }, 60);
    });
    dots.forEach(function (d) {
      d.addEventListener('click', function () { goTo(+d.getAttribute('data-gallery-dot')); });
    });
    thumbs.forEach(function (t) {
      t.addEventListener('click', function () { goTo(+t.getAttribute('data-gallery-thumb')); });
    });
    if (prev) prev.addEventListener('click', function () { goTo(active - 1); });
    if (next) next.addEventListener('click', function () { goTo(active + 1); });
  });
})();
