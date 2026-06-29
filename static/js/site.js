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

  /* ---------- Сертификаты: фильмстрип + lightbox ---------- */
  (function () {
    var film = document.querySelector('[data-cert-film]');
    var lb = document.querySelector('[data-cert-lb]');
    if (!film || !lb) return;

    var cards = Array.prototype.slice.call(film.querySelectorAll('[data-cert-idx]'));
    if (!cards.length) return;

    // данные сертификатов берём из карточек ленты (url крупного фото = src превью, title = alt)
    var items = cards.map(function (c) {
      var img = c.querySelector('img');
      return { src: img ? img.src : '', title: img ? img.alt : '' };
    });

    // листание ленты кнопками (на 2 карточки за шаг)
    function step(dir) {
      var w = cards[0].offsetWidth + 16; // ширина карточки + gap
      film.scrollBy({ left: dir * w * 2, behavior: 'smooth' });
    }
    var filmPrev = document.querySelector('[data-cert-prev]');
    var filmNext = document.querySelector('[data-cert-next]');
    if (filmPrev) filmPrev.addEventListener('click', function () { step(-1); });
    if (filmNext) filmNext.addEventListener('click', function () { step(1); });

    // lightbox
    var lbImg = lb.querySelector('[data-cert-lb-img]');
    var lbTitle = lb.querySelector('[data-cert-lb-title]');
    var lbCounter = lb.querySelector('[data-cert-counter]');
    var idx = 0;
    var lastFocus = null;

    function render() {
      var it = items[idx];
      lbImg.src = it.src;
      lbImg.alt = it.title;
      lbTitle.textContent = it.title;
      lbCounter.textContent = (idx + 1) + ' / ' + items.length;
    }
    function open(i) {
      idx = i;
      lastFocus = document.activeElement;
      render();
      lb.hidden = false;
      lb.classList.add('open');
      document.documentElement.style.overflow = 'hidden';
    }
    function close() {
      lb.classList.remove('open');
      lb.hidden = true;
      document.documentElement.style.overflow = '';
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    function move(d) {
      idx = (idx + d + items.length) % items.length; // зацикленная навигация
      render();
    }

    cards.forEach(function (c) {
      c.addEventListener('click', function () { open(+c.getAttribute('data-cert-idx')); });
    });
    lb.querySelector('[data-cert-close]').addEventListener('click', close);
    lb.querySelector('[data-cert-lb-prev]').addEventListener('click', function () { move(-1); });
    lb.querySelector('[data-cert-lb-next]').addEventListener('click', function () { move(1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') move(-1);
      else if (e.key === 'ArrowRight') move(1);
    });
  })();
})();
