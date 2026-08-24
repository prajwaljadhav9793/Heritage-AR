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
    const marker = L.marker(site.coordinates, { icon })
      .addTo(map)
      .bindPopup(`<strong>${site.name}</strong><br>${site.description}`);
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
});
