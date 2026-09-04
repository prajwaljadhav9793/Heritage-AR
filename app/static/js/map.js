document.addEventListener("DOMContentLoaded", () => {
  const locations = {
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
    konark: {
      name: "Konark Sun Temple",
      label: "Konark Sun Temple",
      category: "UNESCO Heritage",
      rating: "4.8",
      reviews: "8.2k",
      hours: "6:00 AM - 8:00 PM",
      coordinates: [19.8876, 86.0945],
      directionsDestination: "Konark Sun Temple, Odisha, India",
      description: "13th-century chariot temple",
      image: "/static/images/timeline/konark-01.jpg",
    },
    martand: {
      name: "Martand Sun Temple",
      label: "Martand Sun Temple",
      category: "Kashmir Heritage",
      rating: "4.8",
      reviews: "5.4k",
      hours: "8:00 AM - 7:00 PM",
      coordinates: [33.7462, 75.2206],
      directionsDestination: "Martand Sun Temple, Anantnag, Jammu and Kashmir, India",
      description: "Ancient Kashmiri Sun temple",
      image: "/static/images/timeline/martand-01.png",
    },
    meenakshi: {
      name: "Meenakshi Temple",
      label: "Meenakshi Temple",
      category: "Tamil Heritage",
      rating: "4.8",
      reviews: "9.1k",
      hours: "5:00 AM - 12:30 PM, 4:00 PM - 9:30 PM",
      coordinates: [9.9195, 78.1193],
      directionsDestination: "Meenakshi Amman Temple, Madurai, Tamil Nadu, India",
      description: "Dravidian temple of Madurai",
      image: "/static/images/timeline/meenakshi-gopuram.jpg",
    },
    hoysaleshwara: {
      name: "Hoysaleshwara Temple",
      label: "Hoysaleshwara Temple",
      category: "Karnataka Heritage",
      rating: "4.7",
      reviews: "4.9k",
      hours: "6:00 AM - 6:00 PM",
      coordinates: [13.2158, 75.9941],
      directionsDestination: "Hoysaleshwara Temple, Halebidu, Karnataka, India",
      description: "12th-century Hoysala temple",
      image: "/static/images/timeline/halebidu-temple-exterior.jpg",
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

  // Wishlist and Favorites Handling
  let wishlistSites = [];
  try {
    const panelEl = document.querySelector(".heritage-panel");
    if (panelEl && panelEl.dataset.wishlist) {
      wishlistSites = JSON.parse(panelEl.dataset.wishlist);
    }
  } catch (err) {
    wishlistSites = [];
  }

  const isSiteInWishlist = (siteName) => {
    if (!siteName) return false;
    const nameLower = siteName.trim().toLowerCase();
    return wishlistSites.some((s) => {
      const wLower = (s || "").trim().toLowerCase();
      return wLower === nameLower || wLower.includes(nameLower) || nameLower.includes(wLower);
    });
  };

  const toastEl = document.querySelector(".map-toast");
  let toastTimer;
  const showToast = (message, icon = "❤️") => {
    if (!toastEl) return;
    window.clearTimeout(toastTimer);
    toastEl.innerHTML = `<span aria-hidden="true">${icon}</span><span>${message}</span>`;
    toastEl.classList.add("show");
    toastTimer = window.setTimeout(() => {
      toastEl.classList.remove("show");
    }, 2800);
  };

  const toggleFavorite = async (siteName, locationName, clickedBtn) => {
    if (clickedBtn) {
      clickedBtn.classList.add("heart-beat");
      setTimeout(() => clickedBtn.classList.remove("heart-beat"), 400);
    }

    try {
      const response = await fetch("/profile/wishlist/toggle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          site: siteName,
          location: locationName || "",
        }),
      });

      if (response.status === 401) {
        showToast("Please sign in to save heritage places to your favorites.", "🔒");
        return;
      }

      if (!response.ok) {
        showToast("Could not update favorites. Please try again.", "⚠️");
        return;
      }

      const result = await response.json();
      if (result.success) {
        const added = result.added;
        if (added) {
          if (!wishlistSites.includes(siteName)) {
            wishlistSites.push(siteName);
          }
          showToast(`${siteName} added to your favorites!`, "❤️");
        } else {
          wishlistSites = wishlistSites.filter(
            (s) => (s || "").trim().toLowerCase() !== siteName.trim().toLowerCase()
          );
          showToast(`${siteName} removed from favorites.`, "🤍");
        }

        // Synchronize all matching favorite buttons across sidebar and popups
        const normName = siteName.trim().toLowerCase();
        document.querySelectorAll(".site-fav-btn, .site-popup-fav-btn").forEach((btn) => {
          const btnSite = (btn.dataset.site || "").trim().toLowerCase();
          if (btnSite === normName || btnSite.includes(normName) || normName.includes(btnSite)) {
            btn.classList.toggle("is-active", added);
            btn.setAttribute("title", added ? "Remove from Favorites" : "Add to Favorites");
            btn.setAttribute("aria-label", `${added ? "Remove" : "Add"} ${siteName} to favorites`);
          }
        });
      }
    } catch (err) {
      console.error("Favorite toggle error:", err);
      showToast("Unable to connect. Please check your connection.", "⚠️");
    }
  };

  // Attach favorite button click handler on sidebar
  document.querySelectorAll(".site-fav-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const siteName = btn.dataset.site;
      const siteLocation = btn.dataset.location || "";
      toggleFavorite(siteName, siteLocation, btn);
    });
  });

  const markers = {};
  Object.entries(locations).forEach(([id, site]) => {
    const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(site.directionsDestination)}`;
    const timelineUrl = document.querySelector(".map-canvas").dataset.timelineUrl;
    const siteLink = id === "raigad" || id === "hampi" || id === "nalanda" || id === "konark" || id === "martand" || id === "meenakshi" || id === "hoysaleshwara"
      ? `<a class="site-popup-link" href="${timelineUrl}${timelineUrl.includes("?") ? "&" : "?"}site=${id}">View more info <span aria-hidden="true">&rarr;</span></a>`
      : "";
    const isFav = isSiteInWishlist(site.name);
    const popupContent = `
      <article class="site-popup ${id === "raigad" ? "site-popup-raigad" : ""}">
        <img class="site-popup-image" src="${site.image}" alt="${site.name}" />
        <div class="site-popup-heading">
          <span class="site-popup-eyebrow">${site.category}</span>
          <button class="site-popup-close" type="button" aria-label="Close details">&times;</button>
          <div class="site-popup-controls">
            <button
              class="site-popup-fav-btn ${isFav ? "is-active" : ""}"
              type="button"
              data-site="${site.name}"
              data-location="${site.directionsDestination}"
              aria-label="${isFav ? "Remove" : "Add"} ${site.name} to favorites"
              title="${isFav ? "Remove from Favorites" : "Add to Favorites"}"
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </button>
            <button class="site-popup-close" type="button" aria-label="Close details">&times;</button>
          </div>
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
      if (closeButton) {
        closeButton.addEventListener("click", () => marker.closePopup());
      }
      const popupFavBtn = popupElement.querySelector(".site-popup-fav-btn");
      if (popupFavBtn) {
        // Sync active status on open
        const currentlyFav = isSiteInWishlist(site.name);
        popupFavBtn.classList.toggle("is-active", currentlyFav);
        popupFavBtn.setAttribute("title", currentlyFav ? "Remove from Favorites" : "Add to Favorites");
        popupFavBtn.setAttribute("aria-label", `${currentlyFav ? "Remove" : "Add"} ${site.name} to favorites`);

        popupFavBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          toggleFavorite(site.name, site.directionsDestination, popupFavBtn);
        });
      }
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
