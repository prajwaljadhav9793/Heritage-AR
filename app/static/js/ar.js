document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-ar-experience]");
  if (!root) return;

  const models = {
    "royal-palace": {
      number: "01",
      title: "Royal Palace",
      category: "Royal precinct · reconstructed model",
      file: "royal-palace.glb",
      description:
        "The palace was a central part of Raigad's royal precinct. Today, surviving base pillars and archaeological remains indicate the footprint of the former royal residence.",
      survival: "Foundations and base pillars",
      era: "17th Century Maratha Empire",
      status: "Reconstruction from the surviving palace base.",
      arNote: "Place the reconstructed residence at the scale of the space around you.",
    },
    "queens-palace": {
      number: "02",
      title: "Queen's Palace",
      category: "Royal precinct · reconstructed model",
      file: "queens-palace.glb",
      description:
        "Known as Rani Vasa, this was the residential area associated with the royal women of the Maratha court. Its remains show how Raigad functioned as a permanent royal capital.",
      survival: "Portions of the royal residential complex",
      era: "17th Century Maratha Empire",
      status: "Reconstruction of the damaged Rani Vasa precinct.",
      arNote: "Compare the reconstructed quarters with the surviving palace remains.",
    },
    "royal-complex": {
      number: "03",
      title: "Royal Complex",
      category: "Royal precinct · reconstructed model",
      file: "royal-complex.glb",
      description:
        "The wider royal complex formed part of Raigad's ceremonial and residential heart. The visible archaeological remains represent only a portion of the former royal settlement.",
      survival: "Deteriorated royal settlement remains",
      era: "17th Century Maratha Empire",
      status: "Reconstruction of the wider royal precinct.",
      arNote: "Use AR to understand how the separate royal structures relate to one another.",
    },
    marketplace: {
      number: "04",
      title: "Marketplace",
      category: "Civic life · reconstructed model",
      file: "marketplace.glb",
      description:
        "Raigad's market area shows that the fort was also a working capital. It would have served residents, soldiers, officials, traders, and visitors alongside the royal and military precincts.",
      survival: "Ruins and foundations of the market street",
      era: "17th Century Maratha Empire",
      status: "Reconstruction of the historic market avenue.",
      arNote: "Place the market reconstruction beside its remains to compare the lost built form.",
    },
    manore: {
      number: "05",
      title: "Manore",
      category: "Historic pavilion · reconstructed model",
      file: "manore.glb",
      description:
        "The Manore are among Raigad's damaged non-military structures. Their remains preserve evidence of the fort's royal and residential life beyond walls, gates, and defences.",
      survival: "Pavilion remains in poor preservation condition",
      era: "17th Century Maratha Empire",
      status: "Reconstruction of a damaged historic pavilion.",
      arNote: "Use the rotatable model to inspect the pavilion's reconstructed form from every side.",
    },
    "pleasure-pavilions": {
      number: "06",
      title: "Pleasure Pavilions",
      category: "Historic pavilion · reconstructed model",
      file: "pleasure-pavilions.glb",
      description:
        "These pavilions represent the non-military spaces within Raigad's royal capital. The reconstruction helps interpret a structure that now survives only in a damaged condition.",
      survival: "Damaged pavilion remains",
      era: "17th Century Maratha Empire",
      status: "Reconstruction of the lost pavilion architecture.",
      arNote: "Place this reconstruction at ground level to compare its scale with the surviving site.",
    },
    "wadeshwar-temple": {
      number: "07",
      title: "Wadeshwar Temple",
      category: "Religious precinct · reconstructed model",
      file: "wadeshwar-temple.glb",
      description:
        "Wadeshwar Temple is one of the Raigad structures identified as being in poor preservation condition. Its archaeological remains show the religious layer of life in the former capital.",
      survival: "Archaeological temple remains",
      era: "17th Century Maratha Empire",
      status: "Reconstruction of the temple's lost built form.",
      arNote: "Use the AR model to study the reconstructed temple while looking at the surviving remains.",
    },
    "khublada-buruj": {
      number: "08",
      title: "Khublada Buruj",
      category: "Defensive tower · reconstructed model",
      file: "khublada-buruj.glb",
      description:
        "Khublada Buruj is a strategically placed defensive tower. It formed part of the fort's protective system, with a position that allowed people to observe approaching movement.",
      survival: "Deteriorated defensive bastion",
      era: "17th Century Maratha Empire",
      status: "Reconstruction of the strategic defensive tower.",
      arNote: "Rotate the bastion to see the defensive form from all sides, then place it in AR on a supported phone.",
    },
  };

  const viewer = document.querySelector("#heritage-model");
  const cards = [...document.querySelectorAll("[data-monument]")];
  const progress = document.querySelector("#model-progress");
  const progressBar = progress?.querySelector("span");
  const error = document.querySelector("#model-error");
  const rotationButton = document.querySelector("#toggle-rotation");
  const resetButton = document.querySelector("#reset-model");
  const cameraWorkflow = document.querySelector("#camera-workflow");
  const cameraVideo = document.querySelector("#camera-video");
  const capturedPhoto = document.querySelector("#captured-photo");
  const cameraMessage = document.querySelector("#camera-message");
  const startCameraButton = document.querySelector("#start-camera");
  const takePhotoButton = document.querySelector("#take-photo");
  const photoInput = document.querySelector("#monument-photo");
  const comparisonBefore = document.querySelector("#comparison-before");
  const comparisonBeforePlaceholder = document.querySelector("#comparison-before-placeholder");
  const arState = window.heritageArState || (window.heritageArState = { selectedId: "royal-palace", isValidUpload: false });
  let selectedId = arState.selectedId;
  let cameraStream;
  let rotationEnabled = true;

  const text = (selector, value) => {
    const element = document.querySelector(selector);
    if (element) element.textContent = value;
  };

  const showError = (message = "") => {
    if (!error) return;
    error.hidden = !message;
    error.textContent = message;
  };

  const setActiveNav = (view) => {
    document.querySelectorAll("[data-view-link]").forEach((link) => {
      link.classList.toggle("is-active", link.dataset.viewLink === view);
    });
  };

  const updateModelDetails = (model) => {
    text("#monument-category", model.category);
    text("#monument-title", model.title);
    text("#monument-status", model.status);
    text("#detail-number", `${model.number} / 08`);
    text("#detail-title", model.title);
    text("#detail-description", model.description);
    text("#detail-survival", model.survival);
    text("#detail-era", model.era);
    text("#detail-ar-note", model.arNote);
    text("#camera-selected-model", `${model.title} is selected. Switch monuments from the left guide if you are viewing a different ruin.`);
  };

  const selectModel = (id) => {
    const model = models[id];
    if (!model) return;

    selectedId = id;
    arState.selectedId = id;
    showError();
    cards.forEach((card) => {
      const selected = card.dataset.monument === id;
      card.classList.toggle("is-selected", selected);
      card.setAttribute("aria-pressed", String(selected));
    });
    updateModelDetails(model);

    if (!viewer) return;
    viewer.setAttribute("alt", `Interactive 3D reconstruction of ${model.title} at Raigad Fort`);
    // Set attributes rather than element properties so selection also works while
    // the model-viewer web component is still finishing its initial load.
    viewer.setAttribute("src", `/static/models/raigad/${model.file}`);
    viewer.setAttribute("camera-orbit", "45deg 70deg auto");
    if (typeof viewer.jumpCameraToGoal === "function") viewer.jumpCameraToGoal();
  };

  cards.forEach((card) => card.addEventListener("click", () => selectModel(card.dataset.monument)));

  viewer?.addEventListener("progress", (event) => {
    const totalProgress = event.detail?.totalProgress ?? 0;
    if (progress && progressBar) {
      progress.hidden = totalProgress >= 1;
      progressBar.style.width = `${Math.round(totalProgress * 100)}%`;
    }
  });

  viewer?.addEventListener("load", () => {
    if (progress) progress.hidden = true;
    showError();
  });

  viewer?.addEventListener("error", () => {
    if (progress) progress.hidden = true;
    showError("This reconstruction could not load. Please refresh the page and try again.");
  });

  rotationButton?.addEventListener("click", () => {
    rotationEnabled = !rotationEnabled;
    if (rotationEnabled) viewer?.setAttribute("auto-rotate", "");
    else viewer?.removeAttribute("auto-rotate");
    rotationButton.setAttribute("aria-pressed", String(rotationEnabled));
    rotationButton.setAttribute("title", rotationEnabled ? "Pause rotation" : "Start rotation");
  });

  resetButton?.addEventListener("click", () => {
    if (!viewer) return;
    viewer.setAttribute("camera-orbit", "45deg 70deg auto");
    viewer.setAttribute("field-of-view", "auto");
    if (typeof viewer.jumpCameraToGoal === "function") viewer.jumpCameraToGoal();
  });

  const stopCamera = () => {
    cameraStream?.getTracks().forEach((track) => track.stop());
    cameraStream = undefined;
    if (cameraVideo) cameraVideo.srcObject = null;
    if (takePhotoButton) takePhotoButton.disabled = true;
  };

  const openCamera = () => {
    if (!cameraWorkflow) return;
    cameraWorkflow.hidden = false;
    document.body.style.overflow = "hidden";
    setActiveNav("camera");
    window.setTimeout(() => startCameraButton?.focus(), 0);
  };

  const closeCamera = () => {
    if (!cameraWorkflow) return;
    stopCamera();
    cameraWorkflow.hidden = true;
    document.body.style.overflow = "";
    setActiveNav("explore");
  };

  const setCapturedImage = (source) => {
    if (!capturedPhoto || !cameraVideo) return;
    capturedPhoto.src = source;
    capturedPhoto.hidden = false;
    cameraVideo.hidden = true;
    if (comparisonBefore) {
      comparisonBefore.src = source;
      comparisonBefore.hidden = false;
    }
    if (comparisonBeforePlaceholder) comparisonBeforePlaceholder.hidden = true;
    cameraMessage.textContent = "";
  };

  const startCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      cameraMessage.textContent = "Live camera is unavailable in this browser. Choose a photo instead.";
      return;
    }
    try {
      stopCamera();
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false,
      });
      cameraVideo.srcObject = cameraStream;
      cameraVideo.hidden = false;
      capturedPhoto.hidden = true;
      takePhotoButton.disabled = false;
      cameraMessage.textContent = "Camera ready. Frame the visible remains, then take a reference photo.";
    } catch (cameraError) {
      cameraMessage.textContent = "Camera permission was not granted. Choose a photo instead, or allow camera access and try again.";
    }
  };

  const takePhoto = () => {
    if (!cameraVideo?.videoWidth || !cameraVideo?.videoHeight) return;
    const canvas = document.createElement("canvas");
    canvas.width = cameraVideo.videoWidth;
    canvas.height = cameraVideo.videoHeight;
    canvas.getContext("2d")?.drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);
    // Camera capture captured - but validation happens when user uploads file
    // Do NOT set isValidUpload here - user must upload/match a known monument
    setCapturedImage(canvas.toDataURL("image/jpeg", 0.9));
    stopCamera();
  };

  document.querySelector("#open-camera")?.addEventListener("click", openCamera);
  document.querySelector(".close-camera")?.addEventListener("click", closeCamera);
  startCameraButton?.addEventListener("click", startCamera);
  takePhotoButton?.addEventListener("click", takePhoto);
  document.querySelector("#show-reconstruction")?.addEventListener("click", () => {
    // Block reconstruction view if no valid monument image was uploaded
    if (!arState.isValidUpload) {
      if (cameraMessage) {
        cameraMessage.textContent = "I can't convert this image because that monument is not available in the heritage reconstruction database. Please upload another image.";
        cameraMessage.classList.add("is-error");
      }
      return; // Block the action
    }
    
    closeCamera();
    const openViewer = () => document.querySelector(".viewer-stage")?.scrollIntoView({ behavior: "smooth", block: "center" });
    if (typeof viewer?.activateAR !== "function") {
      openViewer();
      return;
    }
    // On a supported mobile device, this moves directly from the reference
    // photo into native AR placement. Desktop browsers fall back to the viewer.
    Promise.resolve(viewer.activateAR()).catch(openViewer);
  });
  photoInput?.addEventListener("change", (event) => {
    const image = event.target.files?.[0];
    if (!image) return;

    const fileName = image.name.toLowerCase();
    const monumentLookup = {
      "royal palace": "royal-palace",
      "royalpalace": "royal-palace",
      "queen's palace": "queens-palace",
      "queens palace": "queens-palace",
      "queens_palace": "queens-palace",
      "royal complex": "royal-complex",
      "royalcomplex": "royal-complex",
      "marketplace": "marketplace",
      "manore": "manore",
      "pleasure pavilion": "pleasure-pavilions",
      "pleasure pavilions": "pleasure-pavilions",
      "wadeshwar": "wadeshwar-temple",
      "wadeshwar temple": "wadeshwar-temple",
      "khublada": "khublada-buruj",
      "khublada buruj": "khublada-buruj",
      "buruj": "khublada-buruj",
    };

    const matchedKey = Object.keys(monumentLookup).find((key) => fileName.includes(key));
    
    if (!matchedKey) {
      // Invalid upload - show error and block capture
      arState.isValidUpload = false;
      if (cameraMessage) {
        cameraMessage.textContent = "I can't convert this image because that monument is not available in the heritage reconstruction database. Please upload another image.";
        cameraMessage.classList.add("is-error");
      }
      return; // Stop processing - don't capture image
    }

    // Valid upload - proceed normally
    arState.isValidUpload = true;
    selectModel(monumentLookup[matchedKey]);
    
    if (cameraMessage) {
      cameraMessage.classList.remove("is-error");
    }

    const reader = new FileReader();
    reader.addEventListener("load", () => setCapturedImage(String(reader.result)));
    reader.readAsDataURL(image);
  });
  cameraWorkflow?.addEventListener("click", (event) => {
    if (event.target === cameraWorkflow) closeCamera();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !cameraWorkflow?.hidden) closeCamera();
  });

  const initialView = root.dataset.initialView || "explore";
  setActiveNav(initialView);
  if (initialView === "camera") window.setTimeout(openCamera, 200);
  selectModel(selectedId);
});
