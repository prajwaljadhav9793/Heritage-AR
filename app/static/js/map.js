document.addEventListener("DOMContentLoaded", () => {
  const locations = {
    ajanta: {
      name: "Ajanta Caves",
      label: "Ajanta Caves",
      category: "UNESCO Heritage",
      rating: "4.8",
      reviews: "18.4k",
      hours: "9:00 AM – 5:00 PM",
      image: "/static/images/historical/then-fort.jpg",
      coordinates: [20.5519, 75.7033],
      directionsDestination: "Ajanta Caves, Maharashtra, India",
      description: "Buddhist rock-cut caves",
    },
    ellora: {
      name: "Ellora Caves",
      label: "Ellora Caves",
      category: "UNESCO Heritage",
      rating: "4.9",
      reviews: "21.7k",
      hours: "6:00 AM – 6:00 PM",
      image: "/static/images/historical/now-fort.jpg",
      coordinates: [20.0268, 75.1782],
      directionsDestination: "Ellora Caves, Maharashtra, India",
      description: "Monolithic temple complex",
    },
    raigad: {
      name: "Raigad Fort",
      label: "Raigad Fort",
      category: "Maratha Heritage",
      rating: "4.8",
      reviews: "9.6k",
      hours: "8:00 AM – 6:00 PM",
      coordinates: [18.2345, 73.4407],
      directionsDestination: "Raigad Fort, Maharashtra, India",
      description: "Historic hill fortress",
      image: "/static/images/heritage/discover-fort.jpg",
      eyebrow: "Capital of Swarajya",
      era: "17th century - Maratha Empire",
      elevation: "820 m above sea level",
      significance:
        "The hilltop capital where Chhatrapati Shivaji Maharaj was crowned in 1674.",
    },
    hampi: {
      name: "Hampi",
      label: "Hampi",
      category: "UNESCO Heritage",
      rating: "4.7",
      reviews: "31.2k",
      hours: "6:00 AM – 6:00 PM",
      coordinates: [15.335, 76.46],
      directionsDestination: "Hampi, Karnataka, India",
      description: "Ruins of the Vijayanagara capital",
      image: "/static/images/historical/then-fort.jpg",
      eyebrow: "City of Victory",
      era: "14th-16th century - Vijayanagara Empire",
      elevation: "~470 m above sea level",
      significance:
        "The ruined capital of the Vijayanagara Empire on the banks of the Tungabhadra.",
    },
    nalanda: {
      name: "Nalanda Mahavihara",
      label: "Nalanda Mahavihara",
      category: "Buddhist Heritage",
      rating: "4.7",
      reviews: "6.8k",
      hours: "9:00 AM - 5:00 PM",
      coordinates: [25.14, 85.44],
      directionsDestination: "Nalanda Mahavihara, Bihar, India",
      description: "Ancient centre of learning",
      image: "/static/images/heritage/nalanda-ruins.jpg",
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
    html: '<span class="heritage-marker" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 10.2 12 4l9 6.2M5.8 10.5h12.4M7.4 10.5v7.1m4.6-7.1v7.1m4.6-7.1v7.1M4.5 19.4h15"/></svg></span>',
    iconSize: [38, 38],
    iconAnchor: [19, 19],
  });

  const markers = {};
  Object.entries(locations).forEach(([id, site]) => {
    const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(site.directionsDestination)}`;
    const timelineUrl = document.querySelector(".map-canvas").dataset.timelineUrl;
    const siteLink = id === "raigad" || id === "hampi" || id === "nalanda"
      ? `<a class="site-popup-link" href="${timelineUrl}${timelineUrl.includes("?") ? "&" : "?"}site=${id}">View more info <span aria-hidden="true">&rarr;</span></a>`
      : "";
    const popupContent = `
      <article class="site-popup ${id === "raigad" ? "site-popup-raigad" : ""}">
        <img class="site-popup-image" src="${site.image}" alt="${site.name}" />
        <div class="site-popup-heading">
          <span class="site-popup-eyebrow">${site.category}</span>
          <button class="site-popup-close" type="button" aria-label="Close details">&times;</button>
        </div>
        <h2>${site.name}</h2>
        <p class="site-popup-type">${site.description}</p>
        <div class="site-popup-meta"><span><b>&#9733;</b> ${site.rating} <small>(${site.reviews})</small></span><span><b>&#9716;</b> ${site.hours}</span></div>
        <div class="site-popup-actions"><a class="site-directions" href="${directionsUrl}" target="_blank" rel="noopener noreferrer">Directions <span aria-hidden="true">&nearr;</span></a>${siteLink}</div>
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
    marker.bindTooltip(site.label, { direction: "top", offset: [0, -16], opacity: 0.92 });
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
    Object.entries(markers).forEach(([markerId, marker]) => {
      marker.getElement()?.querySelector(".heritage-marker")?.classList.toggle("is-active", markerId === id);
    });
    map.setView(site.coordinates, 10, { animate: false });
    if (openPopup) markers[id].openPopup();
  };

  document.querySelectorAll(".site-item").forEach((item) => {
    item.addEventListener("click", () => selectSite(item.dataset.site));
  });
  requestAnimationFrame(() => markers.raigad?.getElement()?.querySelector(".heritage-marker")?.classList.add("is-active"));

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
