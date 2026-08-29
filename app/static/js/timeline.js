document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-timeline]");
  if (!root) return;

  const cards = [...root.querySelectorAll("[data-era]")];
  const track = root.querySelector("[data-track]");
  const scroller = root.querySelector("[data-scroller]");
  const current = root.querySelector("[data-current]");
  const siteButtons = [...root.querySelectorAll("[data-site]")];
  const siteNote = root.querySelector("[data-site-note]");
  const sitePicker = root.querySelector(".timeline-site-picker");
  let index = 0;
  let pointerStart = 0;
  let dragging = false;

  const show = (nextIndex) => {
    index = Math.max(0, Math.min(nextIndex, cards.length - 1));
    const selected = cards[index];
    cards.forEach((card, cardIndex) => {
      card.classList.toggle("is-active", cardIndex === index);
      card.setAttribute("aria-current", cardIndex === index ? "true" : "false");
    });

    // Let the native scroller do the movement. Unlike a translated track, it
    // has a real scroll boundary, so the first and final eras centre correctly.
    const selectedBounds = selected.getBoundingClientRect();
    const scrollerBounds = scroller.getBoundingClientRect();
    const desiredOffset = scroller.scrollLeft
      + (selectedBounds.left - scrollerBounds.left)
      - (scroller.clientWidth - selectedBounds.width) / 2;
    const maximumOffset = Math.max(0, scroller.scrollWidth - scroller.clientWidth);
    const targetOffset = Math.max(0, Math.min(desiredOffset, maximumOffset));
    track.style.transform = "none";
    scroller.scrollTo({ left: targetOffset, behavior: "smooth" });
    current.textContent = String(index + 1).padStart(2, "0");
  };

  cards.forEach((card, cardIndex) => {
    card.addEventListener("click", () => show(cardIndex));
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        show(cardIndex);
      }
    });
  });

  siteButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.available !== "true") {
        siteNote.textContent = `${button.querySelector("strong").textContent} timeline is being added to the archive.`;
        return;
      }
      // Available sites are links that navigate to ?site=...
      if (button.tagName === "A") return;
      siteButtons.forEach((site) => {
        const active = site === button;
        site.classList.toggle("is-selected", active);
        site.setAttribute("aria-pressed", String(active));
      });
      siteNote.textContent = `${button.querySelector("strong").textContent} archive is currently open.`;
      show(0);
    });
  });

  if (sitePicker && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const effects = siteButtons.map((button) => button.classList.contains("is-selected") ? 1 : 0);
    const targets = [...effects];
    let animationFrame;
    let lastTime = performance.now();

    const animateSidebar = (now) => {
      const easing = 1 - Math.exp(-Math.min(now - lastTime, 50) / 90);
      lastTime = now;
      let moving = false;
      siteButtons.forEach((button, siteIndex) => {
        effects[siteIndex] += (targets[siteIndex] - effects[siteIndex]) * easing;
        if (Math.abs(targets[siteIndex] - effects[siteIndex]) > .002) moving = true;
        button.style.setProperty("--effect", effects[siteIndex].toFixed(3));
      });
      animationFrame = moving ? requestAnimationFrame(animateSidebar) : undefined;
    };
    const startSidebarAnimation = () => {
      if (!animationFrame) animationFrame = requestAnimationFrame(animateSidebar);
    };
    siteButtons.forEach((button, siteIndex) => {
      button.addEventListener("click", () => {
        siteButtons.forEach((site, index) => {
          targets[index] = site === button && button.dataset.available === "true" ? 1 : 0;
        });
        startSidebarAnimation();
      });
    });
    sitePicker.addEventListener("pointermove", (event) => {
      siteButtons.forEach((button, siteIndex) => {
        const box = button.getBoundingClientRect();
        const distance = Math.abs(event.clientY - (box.top + box.height / 2));
        const proximity = Math.max(0, 1 - distance / 95);
        targets[siteIndex] = proximity * proximity * (3 - 2 * proximity);
      });
      startSidebarAnimation();
    });
    sitePicker.addEventListener("pointerleave", () => {
      siteButtons.forEach((button, siteIndex) => { targets[siteIndex] = button.classList.contains("is-selected") ? 1 : 0; });
      startSidebarAnimation();
    });
  }

  root.querySelector("[data-next]").addEventListener("click", () => show(index + 1));
  root.querySelector("[data-prev]").addEventListener("click", () => show(index - 1));

  scroller.addEventListener("pointerdown", (event) => {
    dragging = true;
    pointerStart = event.clientX;
    scroller.setPointerCapture(event.pointerId);
  });
  scroller.addEventListener("pointerup", (event) => {
    if (!dragging) return;
    dragging = false;
    const distance = event.clientX - pointerStart;
    if (Math.abs(distance) > 35) show(index + (distance < 0 ? 1 : -1));
  });
  scroller.addEventListener("pointercancel", () => { dragging = false; });
  window.addEventListener("resize", () => show(index));

  show(0);
});
