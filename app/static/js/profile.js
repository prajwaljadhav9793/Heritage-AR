/**
 * HeritageAR - Profile Page Interactivity
 * Handles animated counters, modals, AJAX wishlist toggles,
 * visit logging/removal, avatar uploading, and toast notifications.
 */

document.addEventListener("DOMContentLoaded", () => {
  initCounters();
  initScrollReveal();
  initModals();
  initAvatarPicker();
  initWishlistToggle();
  initVisitedActions();
  initFavoriteSelector();
});

/* ==========================================================================
   Animated Statistics Counters
   ========================================================================== */
function initCounters() {
  const counters = document.querySelectorAll("[data-count]");
  if (!counters.length) return;

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.getAttribute("data-count"), 10) || 0;
          animateCounter(el, 0, target, 1200);
          obs.unobserve(el);
        }
      });
    },
    { threshold: 0.3 }
  );

  counters.forEach((c) => observer.observe(c));
}

function animateCounter(el, start, end, duration) {
  if (start === end) {
    el.textContent = end;
    return;
  }
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out expo
    const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
    const current = Math.floor(start + (end - start) * ease);
    el.textContent = current;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = end;
    }
  }

  requestAnimationFrame(update);
}

function updateCounter(selector, delta) {
  const el = document.querySelector(selector);
  if (!el) return;
  const current = parseInt(el.textContent, 10) || 0;
  const next = Math.max(0, current + delta);
  el.textContent = next;
  el.setAttribute("data-count", next);
}

/* ==========================================================================
   Scroll Reveal Animations
   ========================================================================== */
function initScrollReveal() {
  const elements = document.querySelectorAll("[data-reveal]");
  if (!elements.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
        }
      });
    },
    { threshold: 0.1 }
  );

  elements.forEach((el) => observer.observe(el));
}

/* ==========================================================================
   Modal Management
   ========================================================================== */
function initModals() {
  const triggers = document.querySelectorAll("[data-modal-open]");
  const closeButtons = document.querySelectorAll("[data-modal-close]");

  triggers.forEach((btn) => {
    btn.addEventListener("click", () => {
      const modalId = btn.getAttribute("data-modal-open");
      openModal(modalId);
    });
  });

  closeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal-backdrop");
      if (modal) closeModal(modal);
    });
  });

  // Close on backdrop click
  document.querySelectorAll(".modal-backdrop").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeModal(modal);
    });
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const openModalEl = document.querySelector(".modal-backdrop.is-open");
      if (openModalEl) closeModal(openModalEl);
    }
  });
}

function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.removeAttribute("hidden");
  // Force reflow
  void modal.offsetWidth;
  modal.classList.add("is-open");
  const firstInput = modal.querySelector("input, select");
  if (firstInput) firstInput.focus();
}

function closeModal(modal) {
  modal.classList.remove("is-open");
  setTimeout(() => {
    modal.setAttribute("hidden", "");
  }, 220);
}

/* ==========================================================================
   Avatar Upload Picker & Instant Preview
   ========================================================================== */
function initAvatarPicker() {
  const pickBtn = document.querySelector("[data-avatar-pick]");
  const fileInput = document.getElementById("avatar-input");
  const form = document.querySelector(".avatar-upload-form");
  const avatarImg = document.querySelector(".avatar-img");

  if (!pickBtn || !fileInput) return;

  pickBtn.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", async () => {
    if (!fileInput.files || !fileInput.files[0]) return;
    const file = fileInput.files[0];

    // Local instant preview
    const reader = new FileReader();
    reader.onload = (e) => {
      if (avatarImg) avatarImg.src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Upload via AJAX
    const formData = new FormData();
    formData.append("picture", file);

    try {
      const resp = await fetch("/profile/picture", {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const data = await resp.json();
      if (data.success) {
        showToast("Profile picture updated successfully! ✨");
        if (avatarImg && data.profilePic) {
          avatarImg.src = data.profilePic;
        }
      } else {
        showToast(data.error || "Failed to upload picture.", "error");
      }
    } catch (err) {
      // Fallback submit form if AJAX fails
      if (form) form.submit();
    }
  });
}

/* ==========================================================================
   Wishlist Heart Interactive AJAX Toggle
   ========================================================================== */
function initWishlistToggle() {
  document.addEventListener("click", async (e) => {
    const heartBtn = e.target.closest(".btn-wishlist-heart");
    if (!heartBtn) return;

    e.preventDefault();
    const site = heartBtn.getAttribute("data-site");
    const location = heartBtn.getAttribute("data-location") || "";
    if (!site) return;

    heartBtn.classList.add("heart-beat");
    setTimeout(() => heartBtn.classList.remove("heart-beat"), 400);

    try {
      const resp = await fetch("/profile/wishlist/toggle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ site, location }),
      });
      const res = await resp.json();

      if (res.success) {
        const isAdded = res.added;
        heartBtn.classList.toggle("is-active", isAdded);
        heartBtn.setAttribute(
          "aria-label",
          isAdded ? `Remove ${site} from wishlist` : `Add ${site} to wishlist`
        );

        // Update stats counter
        const wishlistCounter = document.querySelector('[data-stat="wishlist"]');
        if (wishlistCounter) {
          wishlistCounter.textContent = res.count;
          wishlistCounter.setAttribute("data-count", res.count);
        }

        showToast(res.message || (isAdded ? "Saved to your Wishlist ❤️" : "Removed from Wishlist"));

        // If removed and inside wishlist section, smoothly remove card
        if (!isAdded) {
          const card = heartBtn.closest(".place-card");
          if (card && card.closest(".wishlist-section")) {
            card.style.transition = "all 300ms ease";
            card.style.opacity = "0";
            card.style.transform = "scale(0.95)";
            setTimeout(() => {
              card.remove();
              const remaining = document.querySelectorAll(".wishlist-section .place-card");
              if (remaining.length === 0) {
                location.reload(); // Show empty state
              }
            }, 300);
          }
        }
      }
    } catch (err) {
      console.error("Wishlist toggle error:", err);
      // Fallback form submit
      const form = heartBtn.closest("form");
      if (form) form.submit();
    }
  });
}

/* ==========================================================================
   Visited Places Actions (Add / Remove via AJAX)
   ========================================================================== */
function initVisitedActions() {
  // Remove visited place
  document.addEventListener("click", async (e) => {
    const removeBtn = e.target.closest(".journey-remove-btn");
    if (!removeBtn) return;

    e.preventDefault();
    const site = removeBtn.getAttribute("data-site");
    if (!site) return;

    try {
      const resp = await fetch("/profile/visited/remove", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ site }),
      });
      const res = await resp.json();

      if (res.success) {
        const item = removeBtn.closest(".journey-item");
        if (item) {
          item.style.transition = "all 250ms ease";
          item.style.opacity = "0";
          item.style.transform = "translateX(20px)";
          setTimeout(() => item.remove(), 250);
        }

        // Also remove corresponding card from Visited Places grid
        const card = document.querySelector(`.visited-section [data-site-card="${site}"]`);
        if (card) {
          card.style.transition = "all 250ms ease";
          card.style.opacity = "0";
          card.style.transform = "scale(0.9)";
          setTimeout(() => card.remove(), 250);
        }

        // Update stats counter
        const visitedCounter = document.querySelector('[data-stat="visited"]');
        if (visitedCounter) {
          visitedCounter.textContent = res.count;
          visitedCounter.setAttribute("data-count", res.count);
        }

        showToast(res.message || `${site} removed from visits.`);
      }
    } catch (err) {
      console.error("Remove visit error:", err);
      const form = removeBtn.closest("form");
      if (form) form.submit();
    }
  });

  // Add visited place
  const addForm = document.querySelector(".journey-add-form");
  if (addForm) {
    addForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const select = addForm.querySelector('select[name="site"]');
      const site = select ? select.value : "";
      if (!site) return;

      try {
        const resp = await fetch("/profile/visited/add", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ site }),
        });
        const res = await resp.json();

        if (res.success) {
          showToast(res.message || `${site} added to your journeys!`);
          setTimeout(() => window.location.reload(), 600);
        }
      } catch (err) {
        addForm.submit();
      }
    });
  }
}

/* ==========================================================================
   Favorite Heritage Place Quick Selector
   ========================================================================== */
function initFavoriteSelector() {
  const favForm = document.querySelector(".favorite-set-form");
  if (!favForm) return;

  favForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const select = favForm.querySelector('select[name="site"]');
    const site = select ? select.value : "";
    if (!site) return;

    try {
      const resp = await fetch("/profile/favorite", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ site }),
      });
      const res = await resp.json();
      if (res.success) {
        showToast(res.message || `${site} set as your favorite!`);
        setTimeout(() => window.location.reload(), 600);
      }
    } catch (err) {
      favForm.submit();
    }
  });
}

/* ==========================================================================
   Toast Feedback Notification
   ========================================================================== */
function showToast(message, type = "success") {
  let toast = document.querySelector(".profile-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "profile-toast";
    document.body.appendChild(toast);
  }

  const icon = type === "error" ? "⚠️" : "🏛️";
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  toast.classList.add("show");

  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

