document.addEventListener("DOMContentLoaded", () => {
  document.documentElement.dataset.ready = "true";

  const triggers = document.querySelectorAll(".menu-trigger");

  const closeMenus = () => {
    triggers.forEach((trigger) => {
      trigger.setAttribute("aria-expanded", "false");
      const menu = document.getElementById(
        trigger.getAttribute("aria-controls"),
      );
      if (menu) menu.hidden = true;
    });
  };

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      event.stopPropagation();
      const menu = document.getElementById(
        trigger.getAttribute("aria-controls"),
      );
      const isOpen = trigger.getAttribute("aria-expanded") === "true";
      closeMenus();
      if (menu && !isOpen) {
        trigger.setAttribute("aria-expanded", "true");
        menu.hidden = false;
      }
    });
  });

  document.querySelectorAll(".language-option").forEach((option) => {
    option.addEventListener("click", () => {
      option
        .closest(".header-popover")
        .querySelectorAll(".language-option")
        .forEach((item) => item.classList.remove("is-selected"));
      option.classList.add("is-selected");
      closeMenus();
    });
  });

  document.addEventListener("click", closeMenus);

});
