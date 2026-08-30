document.addEventListener("DOMContentLoaded", () => {
  const comparison = document.querySelector("[data-comparison]");
  const thenSide = document.querySelector(".comparison-then");
  const divider = document.querySelector("[data-divider]");
  const handle = document.querySelector(".comparison-handle");
  const uploadInput = document.querySelector("#then-now-upload");
  const thenImage = document.querySelector("#comparison-then-image");
  const nowImage = document.querySelector("#comparison-now-image");
  const modelViewer = document.querySelector("#history-model-viewer");
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

  handle?.addEventListener("pointerdown", (event) => {
    isDragging = true;
    handle.setPointerCapture(event.pointerId);
  });
  handle?.addEventListener("pointermove", (event) => {
    if (isDragging) setPosition(event.clientX);
  });
  handle?.addEventListener("pointerup", stopDragging);
  handle?.addEventListener("pointercancel", stopDragging);
  comparison?.addEventListener("click", (event) => {
    if (event.target !== handle) setPosition(event.clientX);
  });

  handle?.addEventListener("keydown", (event) => {
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

  uploadInput?.addEventListener("change", (event) => {
    const [file] = event.target.files || [];
    if (!file || !thenImage) return;
    const reader = new FileReader();
    reader.onload = () => {
      thenImage.src = String(reader.result);
      thenImage.hidden = false;
    };
    reader.readAsDataURL(file);
  });

  if (modelViewer) {
    modelViewer.setAttribute("camera-orbit", "30deg 75deg auto");
  }

  if (nowImage) {
    nowImage.src = nowImage.src || '{{ url_for("static", filename="models/raigad/royal-palace.glb") }}';
  }
});
