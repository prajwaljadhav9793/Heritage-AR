document.addEventListener("DOMContentLoaded", () => {
  const visual = document.querySelector("[data-auth-visual]");

  if (visual && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    visual.addEventListener("pointermove", (event) => {
      const bounds = visual.getBoundingClientRect();
      const x = (event.clientX - bounds.left) / bounds.width - 0.5;
      const y = (event.clientY - bounds.top) / bounds.height - 0.5;
      visual.style.setProperty("--parallax-x", `${x * 1.2}%`);
      visual.style.setProperty("--parallax-y", `${y * 1.2}%`);
    });

    visual.addEventListener("pointerleave", () => {
      visual.style.setProperty("--parallax-x", "0%");
      visual.style.setProperty("--parallax-y", "0%");
    });
  }

  document.querySelectorAll("[data-password-toggle]").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const field = toggle.closest(".password-field").querySelector("input");
      const isVisible = field.type === "text";
      field.type = isVisible ? "password" : "text";
      toggle.textContent = isVisible ? "Show" : "Hide";
      toggle.setAttribute("aria-label", isVisible ? "Show password" : "Hide password");
    });
  });
});