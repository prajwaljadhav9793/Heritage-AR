document.addEventListener("DOMContentLoaded", () => {
  const events = window.timelineEvents || [];
  const points = document.querySelectorAll(".event-point");
  const title = document.querySelector("[data-event-title]");
  const description = document.querySelector("[data-event-description]");
  const eventImage = document.querySelector("[data-event-image]");
  const note = document.querySelector("#reconstruction-note");
  const reconstructionButton = document.querySelector("#view-reconstruction");

  const selectEvent = (index) => {
    const event = events[index];
    if (!event) return;
    points.forEach((point, pointIndex) => {
      point.classList.toggle("is-selected", pointIndex === index);
    });
    title.textContent = event.title;
    description.textContent = event.description;
    if (eventImage) {
      eventImage.classList.add("is-changing");
      const nextImage = new Image();
      nextImage.onload = () => {
        eventImage.src = event.image;
        eventImage.alt = `${event.title} at Raigad Fort`;
        eventImage.classList.remove("is-changing");
      };
      nextImage.onerror = () => {
        eventImage.src = event.fallback;
        eventImage.alt = `${event.title} at Raigad Fort`;
        eventImage.classList.remove("is-changing");
      };
      nextImage.src = event.image;
    }
    note.hidden = true;
    reconstructionButton.textContent = "View reconstruction ->";
  };

  points.forEach((point) => {
    point.addEventListener("click", () =>
      selectEvent(Number(point.dataset.eventIndex)),
    );
  });

  reconstructionButton.addEventListener("click", () => {
    note.hidden = !note.hidden;
    reconstructionButton.textContent = note.hidden
      ? "View reconstruction ->"
      : "Reconstruction ready ->";
  });
});
