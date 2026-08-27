document.addEventListener("DOMContentLoaded", () => {
  const locations = {
    ajanta: {
      name: "Ajanta Caves",
      coordinates: [20.5519, 75.7033],
      description: "Buddhist rock-cut caves",
    },
    ellora: {
      name: "Ellora Caves",
      coordinates: [20.0268, 75.1782],
      description: "Monolithic temple complex",
    },
    raigad: {
      name: "Raigad Fort",
      coordinates: [18.2345, 73.4407],
      description: "Historic hill fortress",
      image: "/static/images/heritage/discover-fort.jpg",
      eyebrow: "Capital of Swarajya",
      era: "17th century - Maratha Empire",
      elevation: "820 m above sea level",
      significance:
        "The hilltop capital where Chhatrapati Shivaji Maharaj was crowned in 1674.",
    },
  };

  const map = L.map("heritage-map", {
    preferCanvas: true,
    zoomControl: false,
    minZoom: 6,
    zoomAnimation: false,
    fadeAnimation: false,
    markerZoomAnimation: false,
  }).setView([19.2, 74.7], 7);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    keepBuffer: 1,
    maxZoom: 18,
    updateWhenIdle: true,
    updateWhenZooming: false,
  }).addTo(map);

  const icon = L.divIcon({
    className: "heritage-pin-wrapper",
    html: '<span class="custom-pin"></span>',
    iconSize: [24, 24],
    iconAnchor: [12, 24],
  });

  const markers = {};
  Object.entries(locations).forEach(([id, site]) => {
    const popupContent = `
      <article class="site-popup ${id === "raigad" ? "site-popup-raigad" : ""}">
        ${site.image ? `<img class="site-popup-image" src="${site.image}" alt="Raigad Fort ruins" />` : ""}
        <div class="site-popup-heading">
          <span class="site-popup-eyebrow">${site.eyebrow || "Heritage site"}</span>
          <button class="site-popup-close" type="button" aria-label="Close details">&times;</button>
        </div>
        <h2>${site.name}</h2>
        <p class="site-popup-type">${site.description}</p>
        ${
          site.significance
            ? `<p class="site-popup-significance">${site.significance}</p>
               <dl class="site-popup-facts">
                 <div><dt>Period</dt><dd>${site.era}</dd></div>
                 <div><dt>Elevation</dt><dd>${site.elevation}</dd></div>
               </dl>`
            : ""
        }
        ${
          id === "raigad"
            ? `<a class="site-popup-link" href="${document.querySelector(".map-canvas").dataset.timelineUrl}">View more info <span aria-hidden="true">&rarr;</span></a>`
            : ""
        }
      </article>`;
    const marker = L.marker(site.coordinates, { icon })
      .addTo(map)
      .bindPopup(popupContent, {
        className: "heritage-popup",
        closeButton: false,
        offset: [0, -12],
        autoPan: true,
        autoPanPaddingTopLeft: [20, 88],
        autoPanPaddingBottomRight: [20, 20],
      });
    let closeTimer;
    const keepPopupOpen = () => {
      window.clearTimeout(closeTimer);
    };
    const closeOnHoverEnd = () => {
      closeTimer = window.setTimeout(() => marker.closePopup(), 180);
    };
    marker.on("mouseover", () => {
      keepPopupOpen();
      marker.openPopup();
    });
    marker.on("mouseout", closeOnHoverEnd);
    marker.on("popupopen", (event) => {
      const popupElement = event.popup.getElement();
      popupElement.addEventListener("mouseenter", keepPopupOpen);
      popupElement.addEventListener("mouseleave", closeOnHoverEnd);
      const closeButton = popupElement.querySelector(".site-popup-close");
      closeButton.addEventListener("click", () => marker.closePopup());
    });
    marker.on("click", () => selectSite(id, false));
    markers[id] = marker;
  });

  const selectSite = (id, openPopup = true) => {
    const site = locations[id];
    if (!site) return;
    document.querySelectorAll(".site-item").forEach((item) => {
      item.classList.toggle("is-selected", item.dataset.site === id);
    });
    map.setView(site.coordinates, 10, { animate: false });
    if (openPopup) markers[id].openPopup();
  };

  document.querySelectorAll(".site-item").forEach((item) => {
    item.addEventListener("click", () => selectSite(item.dataset.site));
  });

  const panel = document.querySelector(".heritage-panel");
  const siteItems = [...document.querySelectorAll(".site-item")];
  if (panel && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const effects = siteItems.map((item) => item.classList.contains("is-selected") ? 1 : 0);
    const targets = [...effects];
    let animationFrame;
    let lastTime = performance.now();
    const animatePanel = (now) => {
      const easing = 1 - Math.exp(-Math.min(now - lastTime, 50) / 90);
      lastTime = now;
      let moving = false;
      siteItems.forEach((item, index) => {
        effects[index] += (targets[index] - effects[index]) * easing;
        if (Math.abs(targets[index] - effects[index]) > .002) moving = true;
        item.style.setProperty("--effect", effects[index].toFixed(3));
      });
      animationFrame = moving ? requestAnimationFrame(animatePanel) : undefined;
    };
    const start = () => { if (!animationFrame) animationFrame = requestAnimationFrame(animatePanel); };
    panel.addEventListener("pointermove", (event) => {
      siteItems.forEach((item, index) => {
        const box = item.getBoundingClientRect();
        const distance = Math.abs(event.clientY - (box.top + box.height / 2));
        const proximity = Math.max(0, 1 - distance / 95);
        targets[index] = proximity * proximity * (3 - 2 * proximity);
      });
      start();
    });
    panel.addEventListener("pointerleave", () => {
      siteItems.forEach((item, index) => { targets[index] = item.classList.contains("is-selected") ? 1 : 0; });
      start();
    });
    siteItems.forEach((item) => item.addEventListener("click", () => {
      siteItems.forEach((site, index) => { targets[index] = site === item ? 1 : 0; });
      start();
    }));
  }
});
