document.addEventListener("DOMContentLoaded",()=>{const c=document.querySelector("[data-heritage-carousel]");if(!c)return;const s=[...c.querySelectorAll("[data-slide]")],a=[...c.querySelectorAll(".story-card")],d=[...c.querySelectorAll(".rail-dot")],l=c.querySelector("[data-current-slide]"),r=matchMedia("(prefers-reduced-motion: reduce)").matches;let n=0,t;const show=i=>{n=(i+s.length)%s.length;s.forEach((x,j)=>x.classList.toggle("is-active",j===n));a.forEach((x,j)=>x.classList.toggle("is-current",j===n));d.forEach((x,j)=>x.classList.toggle("is-active",j===n));l.textContent=String(n+1).padStart(2,"0")},start=()=>{clearInterval(t);if(!r)t=setInterval(()=>show(n+1),6500)};c.querySelectorAll("[data-go-to]").forEach(x=>x.addEventListener("click",()=>{show(Number(x.dataset.goTo));start()}));c.querySelector("[data-next]").addEventListener("click",()=>{show(n+1);start()});c.querySelector("[data-previous]").addEventListener("click",()=>{show(n-1);start()});c.addEventListener("mouseenter",()=>clearInterval(t));c.addEventListener("mouseleave",start);start()});
document.addEventListener("DOMContentLoaded", () => {
  const carousel = document.querySelector("[data-heritage-carousel]");
  if (!carousel) return;

  const slides = [...carousel.querySelectorAll("[data-slide]")];
  const cards = [...carousel.querySelectorAll(".story-card")];
  const dots = [...carousel.querySelectorAll(".rail-dot")];
  const currentSlideEl = carousel.querySelector("[data-current-slide]");
  const totalSlidesEl = carousel.querySelector("[data-total-slides]");
  const railCountEl = carousel.querySelector(".rail-count");
  const storyDeck = carousel.querySelector(".story-deck");
  const prefersReducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const total = slides.length;
  if (totalSlidesEl) totalSlidesEl.textContent = String(total).padStart(2, "0");

  let currentIndex = 0;
  let autoTimer = null;
  const ROTATE_INTERVAL = 6500;

  const showSlide = (index) => {
    currentIndex = (index + total) % total;

    // Update active slide
    slides.forEach((slide, i) => {
      slide.classList.toggle("is-active", i === currentIndex);
    });

    // Update active story card
    cards.forEach((card, i) => {
      card.classList.toggle("is-current", i === currentIndex);
    });

    // Update rail dots
    dots.forEach((dot, i) => {
      dot.classList.toggle("is-active", i === currentIndex);
    });

    // Update slide counts
    const currentFormatted = String(currentIndex + 1).padStart(2, "0");
    const totalFormatted = String(total).padStart(2, "0");
    if (currentSlideEl) currentSlideEl.textContent = currentFormatted;
    if (railCountEl) railCountEl.textContent = `${currentFormatted} / ${totalFormatted}`;

    // Smoothly shift the story deck so the current card is always visible
    // Smoothly scroll the story deck so the current card is nicely centered
    if (storyDeck && cards[currentIndex]) {
      const cardWidth = cards[0].offsetWidth || 180;
      const gap = 16;
      const shift = Math.max(0, currentIndex - 1) * (cardWidth + gap);
      storyDeck.style.transform = `translateX(-${shift}px)`;
      const card = cards[currentIndex];
      const deckWidth = storyDeck.clientWidth;
      const cardLeft = card.offsetLeft;
      const cardWidth = card.offsetWidth;
      storyDeck.scrollTo({
        left: cardLeft - (deckWidth / 2) + (cardWidth / 2),
        behavior: "smooth"
      });
    }
  };

  const startAutoRotate = () => {
    clearInterval(autoTimer);
    if (!prefersReducedMotion) {
      autoTimer = setInterval(() => {
        showSlide(currentIndex + 1);
      }, ROTATE_INTERVAL);
    }
  };

  const stopAutoRotate = () => {
    clearInterval(autoTimer);
  };

  // Click on dots or cards with [data-go-to]
  carousel.querySelectorAll("[data-go-to]").forEach((btn) => {
    btn.addEventListener("click", () => {
      showSlide(Number(btn.dataset.goTo));
      startAutoRotate();
    });
  });

  // Next / Previous navigation buttons
  const nextBtn = carousel.querySelector("[data-next]");
  const prevBtn = carousel.querySelector("[data-previous]");

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      showSlide(currentIndex + 1);
      startAutoRotate();
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      showSlide(currentIndex - 1);
      startAutoRotate();
    });
  }

  // Keyboard navigation (Arrow keys)
  window.addEventListener("keydown", (e) => {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
    if (e.key === "ArrowRight") {
      showSlide(currentIndex + 1);
      startAutoRotate();
    } else if (e.key === "ArrowLeft") {
      showSlide(currentIndex - 1);
      startAutoRotate();
    }
  });

  // Touch swipe support for mobile and tablets
  let touchStartX = 0;
  let touchEndX = 0;

  carousel.addEventListener(
    "touchstart",
    (e) => {
      if (e.changedTouches && e.changedTouches.length) {
        touchStartX = e.changedTouches[0].screenX;
      }
    },
    { passive: true }
  );

  carousel.addEventListener(
    "touchend",
    (e) => {
      if (e.changedTouches && e.changedTouches.length) {
        touchEndX = e.changedTouches[0].screenX;
        const diff = touchStartX - touchEndX;
        if (Math.abs(diff) > 40) {
          if (diff > 0) {
            showSlide(currentIndex + 1);
          } else {
            showSlide(currentIndex - 1);
          }
          startAutoRotate();
        }
      }
    },
    { passive: true }
  );

  // Pause rotation on hover
  carousel.addEventListener("mouseenter", stopAutoRotate);
  carousel.addEventListener("mouseleave", startAutoRotate);

  // Initialize
  showSlide(0);
  startAutoRotate();
});

