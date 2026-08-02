"use strict";

/* ============================================================================
   ARSC — site behaviour. Zero dependencies, shared by every page.

   Scroll reveals, animated counters, sticky-header condense, mobile menu,
   FAQ accordion, and the YouTube lesson player.

   Every page here is complete and readable with this file removed. Nothing
   in it is load-bearing for content or navigation.
   ========================================================================= */

(function () {

  var reduce = window.matchMedia &&
               window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canObserve = "IntersectionObserver" in window;

  function each(list, fn) { Array.prototype.forEach.call(list, fn); }

  /* ------------------------------------------------------------- reveals -- */

  var items = document.querySelectorAll("[data-reveal]");

  if (reduce || !canObserve) {
    // No observer support, or motion is unwanted: show everything at once.
    each(items, function (el) { el.classList.add("is-visible"); });
  } else {
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-visible");
        obs.unobserve(e.target);      // one-shot; callback cost trends to zero
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    each(items, function (el) { io.observe(el); });
  }

  /* ------------------------------------------------------------ counters --
     The final value is written into the HTML, so a visitor with JS disabled
     or reduced motion enabled sees the real figure, never a zero. */

  function easeOutExpo(t) { return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); }

  function count(el) {
    var to = parseFloat(el.getAttribute("data-count-to"));
    var suffix = el.getAttribute("data-suffix") || "";
    var dur = 1400, t0 = null;
    function frame(now) {
      if (t0 === null) t0 = now;
      var p = Math.min((now - t0) / dur, 1);
      el.textContent = Math.round(to * easeOutExpo(p)) + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  if (!reduce && canObserve) {
    var io2 = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        count(e.target);
        obs.unobserve(e.target);
      });
    }, { threshold: 0.6 });
    each(document.querySelectorAll("[data-count-to]"), function (el) { io2.observe(el); });
  }

  /* -------------------------------------------------------------- header --
     The scroll listener only raises a flag; the class toggle happens once per
     frame inside rAF, so fast scrolling can never queue up layout work. */

  var header = document.querySelector(".site-header");
  var queued = false;

  function sync() {
    if (header) header.classList.toggle("is-condensed", window.scrollY > 24);
    queued = false;
  }

  window.addEventListener("scroll", function () {
    if (queued) return;
    queued = true;
    requestAnimationFrame(sync);
  }, { passive: true });

  sync();

  /* --------------------------------------------------------- mobile menu -- */

  var toggle = document.querySelector(".nav-toggle");

  if (toggle && header) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      header.classList.toggle("menu-open", !open);
    });

    // Escape closes the drawer and returns focus to the button, so keyboard
    // users are never stranded inside an open menu.
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      if (toggle.getAttribute("aria-expanded") !== "true") return;
      toggle.setAttribute("aria-expanded", "false");
      header.classList.remove("menu-open");
      toggle.focus();
    });
  }

  /* ----------------------------------------------------------- accordion --
     aria-expanded is the source of truth; the class only drives the CSS row
     transition. Real <button>s inside headings, so screen reader users get
     both the document outline and the control. */

  each(document.querySelectorAll(".qa-btn"), function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".qa");
      var open = btn.getAttribute("aria-expanded") === "true";

      each(document.querySelectorAll(".qa.is-open"), function (other) {
        if (other === item) return;
        other.classList.remove("is-open");
        other.querySelector(".qa-btn").setAttribute("aria-expanded", "false");
      });

      btn.setAttribute("aria-expanded", String(!open));
      item.classList.toggle("is-open", !open);
    });
  });

  /* ------------------------------------------------- youtube lesson player --
     One facade, many lessons. Nothing is requested from YouTube until a
     lesson is played, and playback goes via youtube-nocookie.com so no
     tracking cookie is set even then.

     Each lesson keeps its own video ID in data-yt-id. Filling that attribute
     in is the only step needed to wire a lesson up — no code changes. */

  var player = document.getElementById("ytPlayer");
  var nowPlaying = document.getElementById("nowPlaying");

  function faceMarkup(label) {
    return '<span class="lite-yt-face">' +
             '<span class="lite-yt-play">' +
               '<svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
                 '<path d="M8 5.14v13.72L19 12 8 5.14Z"/>' +
               '</svg>' +
             '</span>' +
             '<span class="lite-yt-label">' + label + '</span>' +
           '</span>';
  }

  // Rebuild the poster state. Called on every lesson change so switching
  // lessons can never leave the previous video playing underneath.
  function showFacade(id, title, label) {
    if (!player) return;
    player.setAttribute("data-yt-id", id || "");
    player.setAttribute("data-yt-title", title || "");
    player.innerHTML = faceMarkup(label);

    if (id) {
      var poster = new Image();
      poster.src = "https://i.ytimg.com/vi/" + id + "/hqdefault.jpg";
      poster.alt = "";
      poster.decoding = "async";
      player.insertBefore(poster, player.firstChild);
    }
  }

  function play(box) {
    if (!box) return;
    var id = box.getAttribute("data-yt-id");
    if (!id) return;                       // lesson not linked yet
    var frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + id +
                "?autoplay=1&rel=0&modestbranding=1";
    frame.title = box.getAttribute("data-yt-title") || "Course lesson";
    frame.allow = "accelerometer; autoplay; encrypted-media; picture-in-picture";
    frame.allowFullscreen = true;
    box.innerHTML = "";
    box.appendChild(frame);
  }

  if (player) {
    var first = document.querySelector('.lesson[aria-current="true"]') ||
                document.querySelector(".lesson");
    if (first) {
      showFacade(
        first.getAttribute("data-yt-id"),
        first.getAttribute("data-lesson-title"),
        first.getAttribute("data-yt-id") ? "Play lesson" : "Video coming soon"
      );
    }
    player.addEventListener("click", function () { play(player); });
  }

  each(document.querySelectorAll(".lesson"), function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-yt-id");
      var no = btn.getAttribute("data-lesson-no");
      var title = btn.getAttribute("data-lesson-title");

      // aria-current is the source of truth for the selected lesson; styling
      // hangs off it rather than a parallel class.
      each(document.querySelectorAll(".lesson"), function (other) {
        other.removeAttribute("aria-current");
      });
      btn.setAttribute("aria-current", "true");

      if (nowPlaying) {
        nowPlaying.innerHTML = "<b>Lesson " + no + "</b> <span>" + title + "</span>";
      }

      showFacade(id, title, id ? "Play lesson" : "Video coming soon");
      if (id) play(player);   // a deliberate lesson click means play it
    });
  });

  /* --------------------------------------------------------- newsletter --
     No backend, so this composes a mailto rather than posting to a
     third-party list service. Swap for a real endpoint when one exists. */

  var signup = document.getElementById("signupForm");
  if (signup) {
    signup.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!signup.checkValidity()) { signup.reportValidity(); return; }
      var email = (document.getElementById("nl-email") || {}).value || "";
      location.href = "mailto:info@arscollegecanada.ca"
        + "?subject=" + encodeURIComponent("Newsletter subscription")
        + "&body=" + encodeURIComponent("Please add this address to the ARSC mailing list: " + email);
    });
  }

  /* ---------------------------------------------------- anchor focus fix --
     CSS handles the scrolling; this moves keyboard focus too. Without it,
     tabbing after an in-page link resumes from the top of the document. */

  each(document.querySelectorAll('a[href^="#"]'), function (link) {
    link.addEventListener("click", function () {
      var id = link.getAttribute("href").slice(1);
      if (!id) return;
      var target = document.getElementById(id);
      if (!target) return;
      setTimeout(function () {
        target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
      }, 420);
    });
  });

})();
