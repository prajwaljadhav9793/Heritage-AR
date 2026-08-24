document.addEventListener("DOMContentLoaded", () => {
  const comparison = document.querySelector("[data-comparison]");
  const thenSide = document.querySelector(".comparison-then");
  const divider = document.querySelector("[data-divider]");
  const handle = document.querySelector(".comparison-handle");
  let isDragging = false;

  const setPosition = (clientX) => {
    const bounds = comparison.getBoundingClientRect();
    const percentage = Math.max(
      4,
      Math.min(96, ((clientX - bounds.left) / bounds.width) * 100),
    );
    thenSide.style.clipPath = `inset(0 ${100 - percentage}% 0 0)`;
    divider.style.left = `${percentage}%`;
    handle.setAttribute("aria-valuenow", Math.round(percentage));
  };

  const stopDragging = () => {
    isDragging = false;
  };

  handle.addEventListener("pointerdown", (event) => {
    isDragging = true;
    handle.setPointerCapture(event.pointerId);
  });
  handle.addEventListener("pointermove", (event) => {
    if (isDragging) setPosition(event.clientX);
  });
  handle.addEventListener("pointerup", stopDragging);
  handle.addEventListener("pointercancel", stopDragging);
  comparison.addEventListener("click", (event) => {
    if (event.target !== handle) setPosition(event.clientX);
  });

  handle.addEventListener("keydown", (event) => {
    const current = Number(handle.getAttribute("aria-valuenow"));
    if (event.key === "ArrowLeft")
      setPosition(
        comparison.getBoundingClientRect().left +
          comparison.offsetWidth * ((current - 5) / 100),
      );
    if (event.key === "ArrowRight")
      setPosition(
        comparison.getBoundingClientRect().left +
          comparison.offsetWidth * ((current + 5) / 100),
      );
  });
});
