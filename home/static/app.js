/* ==========================================================================
   RMS — UI animation layer
   Progressive enhancement only: with JS off, every page stays fully usable
   (reveals default to visible via the .no-js fallback in base.html).
   ========================================================================== */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ----------------------------------------------------------------
       Scroll progress bar + nav elevation
       ---------------------------------------------------------------- */
    function initScrollUI() {
        var bar = document.querySelector('.scroll-progress');
        var nav = document.querySelector('.navbar');
        var ticking = false;

        function update() {
            if (bar) {
                var doc = document.documentElement;
                var max = doc.scrollHeight - doc.clientHeight;
                var pct = max > 0 ? (doc.scrollTop / max) * 100 : 0;
                bar.style.width = pct + '%';
            }
            if (nav) nav.classList.toggle('scrolled', window.scrollY > 8);
            ticking = false;
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                ticking = true;
                window.requestAnimationFrame(update);
            }
        }, { passive: true });

        update();
    }

    /* ----------------------------------------------------------------
       Reveal on scroll (IntersectionObserver)
       ---------------------------------------------------------------- */
    function initReveals() {
        var targets = document.querySelectorAll('.reveal');

        if (reduceMotion || !('IntersectionObserver' in window)) {
            targets.forEach(function (el) { el.classList.add('in'); });
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        targets.forEach(function (el) { observer.observe(el); });
    }

    /* ----------------------------------------------------------------
       Count-up animation for numbers marked [data-count]
       ---------------------------------------------------------------- */
    function initCounters() {
        var els = document.querySelectorAll('[data-count]');
        if (!els.length) return;

        function animate(el) {
            var target = parseFloat(el.getAttribute('data-count')) || 0;
            if (reduceMotion) { el.textContent = target; return; }

            var duration = 1100;
            var start = null;

            function step(ts) {
                if (start === null) start = ts;
                var p = Math.min((ts - start) / duration, 1);
                // easeOutCubic
                var eased = 1 - Math.pow(1 - p, 3);
                el.textContent = Math.round(target * eased);
                if (p < 1) window.requestAnimationFrame(step);
                else el.textContent = target;
            }
            window.requestAnimationFrame(step);
        }

        if (!('IntersectionObserver' in window)) {
            els.forEach(animate);
            return;
        }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) { animate(e.target); io.unobserve(e.target); }
            });
        }, { threshold: 0.4 });

        els.forEach(function (el) { io.observe(el); });
    }

    /* ----------------------------------------------------------------
       Progress bars: set width from [data-pct] once visible
       ---------------------------------------------------------------- */
    function initBars() {
        var bars = document.querySelectorAll('.bar > span[data-pct]');
        if (!bars.length) return;

        function fill(el) {
            var wrapper = el.parentElement;
            var width = el.getAttribute('data-pct');
            if (!wrapper.dataset.w) {
                wrapper.dataset.w = wrapper.style.width || (el.dataset.width || '');
            }
            el.style.width = width + '%';
        }

        if (reduceMotion) { bars.forEach(fill); return; }

        if (!('IntersectionObserver' in window)) {
            setTimeout(function () { bars.forEach(fill); }, 150);
            return;
        }
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) { fill(e.target); io.unobserve(e.target); }
            });
        }, { threshold: 0.3 });
        bars.forEach(function (el) { io.observe(el); });
    }

    /* ----------------------------------------------------------------
       Submit buttons: show a spinner and disable to prevent double posts
       ---------------------------------------------------------------- */
    function initSubmitFeedback() {
        document.querySelectorAll('form').forEach(function (form) {
            form.addEventListener('submit', function () {
                var btn = form.querySelector('button[type=submit], button:not([type])');
                if (!btn || btn.dataset.busy) return;
                if (btn.form && !form.checkValidity()) return;

                btn.dataset.busy = '1';
                var original = btn.innerHTML;
                btn.innerHTML = '<span class="spinner"></span> Working…';
                btn.disabled = true;
                btn.style.opacity = '.85';

                // If the page does not navigate (validation error), restore.
                setTimeout(function () {
                    if (btn.dataset.busy) {
                        btn.innerHTML = original;
                        btn.disabled = false;
                        btn.style.opacity = '';
                        delete btn.dataset.busy;
                    }
                }, 12000);
            });
        });
    }

    /* ----------------------------------------------------------------
       Auto-dismiss flash messages
       ---------------------------------------------------------------- */
    function initMessages() {
        document.querySelectorAll('.messages li').forEach(function (li, i) {
            setTimeout(function () {
                li.style.transition = 'opacity .5s ease, transform .5s ease, height .5s ease, margin .5s ease';
                li.style.opacity = '0';
                li.style.transform = 'translateX(-14px)';
                li.style.height = '0';
                li.style.marginBottom = '0';
                li.style.paddingTop = '0';
                li.style.paddingBottom = '0';
                li.style.overflow = 'hidden';
                setTimeout(function () { li.remove(); }, 520);
            }, 6000 + i * 400);
        });
    }

    /* ----------------------------------------------------------------
       Card tilt on pointer move (skip on touch / reduced motion)
       ---------------------------------------------------------------- */
    function initTilt() {
        if (reduceMotion || !window.matchMedia || !window.matchMedia('(hover: hover)').matches) return;

        document.querySelectorAll('.card[data-tilt]').forEach(function (card) {
            var raf = null;
            card.addEventListener('pointermove', function (e) {
                if (raf) return;
                raf = window.requestAnimationFrame(function () {
                    var r = card.getBoundingClientRect();
                    var x = (e.clientX - r.left) / r.width - 0.5;
                    var y = (e.clientY - r.top) / r.height - 0.5;
                    card.style.transform =
                        'perspective(900px) rotateY(' + (x * 5) + 'deg) rotateX(' +
                        (-y * 5) + 'deg) translateY(-3px)';
                    raf = null;
                });
            });
            card.addEventListener('pointerleave', function () {
                card.style.transform = '';
            });
        });
    }

    /* ---------------------------------------------------------------- */
    function init() {
        document.documentElement.classList.remove('no-js');
        initScrollUI();
        initReveals();
        initCounters();
        initBars();
        initSubmitFeedback();
        initMessages();
        initTilt();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
