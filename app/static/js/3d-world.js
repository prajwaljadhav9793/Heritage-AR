document.addEventListener("DOMContentLoaded", () => {
	const models = {
		raigad: [
			["royal-palace", "Royal Palace", "royal-palace.glb", "Royal precinct"],
			["queens-palace", "Queen's Palace", "queens-palace.glb", "Royal precinct"],
			["royal-complex", "Royal Complex", "royal-complex.glb", "Royal precinct"],
			["marketplace", "Marketplace", "marketplace.glb", "Civic life"],
			["manore", "Manore", "manore.glb", "Historic pavilion"],
			["pleasure-pavilions", "Pleasure Pavilions", "pleasure-pavilions.glb", "Historic pavilion"],
			["wadeshwar-temple", "Wadeshwar Temple", "wadeshwar-temple.glb", "Religious precinct"],
			["khublada-buruj", "Khublada Buruj", "khublada-buruj.glb", "Defensive tower"],
		],
		hampi: [
			["achyutaraya-temple", "Achyutaraya Temple", "Achyutaraya Temple.glb", "Sacred architecture"],
			["hazara-rama-temple", "Hazara Rama Temple", "Hazara Rama Temple.glb", "Sacred architecture"],
			["krishna-temple", "Krishna Temple", "Krishna Temple.glb", "Sacred architecture"],
			["lotus-mahal", "Lotus Mahal", "Lotus Mahal.glb", "Royal enclosure"],
			["mahanavami-dibba", "Mahanavami Dibba", "Mahanavami Dibba.glb", "Ceremonial platform"],
			["royal-palace", "Royal Palace", "Royal Palace.glb", "Royal enclosure"],
			["vittala-temple", "Vittala Temple", "Vittala Temple.glb", "Sacred architecture"],
			["zanana-enclosure", "Zanana Enclosure", "Zanana Enclosure.glb", "Royal enclosure"],
		],
		nalanda: [
			["assembly-areas", "Assembly Areas", "Assembly Areas.glb", "Monastic campus"],
			["entrance-gateways", "Entrance Gateways", "Entrance Gateways.glb", "Monastic campus"],
			["library-buildings", "Library Buildings", "Library Buildings.glb", "Learning centre"],
			["main-shrine", "Main Shrine", "Main Shrine.glb", "Sacred architecture"],
			["residential-cells", "Residential Cells", "Residential Cells.glb", "Monastic campus"],
			["temple-complexes", "Temple Complexes", "Temple Complexes.glb", "Sacred architecture"],
		],
	};
	const siteNames = { raigad: "Raigad Fort", hampi: "Hampi", nalanda: "Nalanda Mahavihara" };
	const viewer = document.querySelector("#heritage-model");
	const list = document.querySelector("#monument-list");
	const error = document.querySelector("#model-error");
	const progress = document.querySelector("#model-progress");
	const progressBar = progress?.querySelector("span");
	const rotationButton = document.querySelector("#toggle-rotation");
	const resetButton = document.querySelector("#reset-model");
	let currentSite = "raigad";
	let currentModel;
	let rotationEnabled = true;

	const text = (selector, value) => { const element = document.querySelector(selector); if (element) element.textContent = value; };
	const showError = (message = "") => { if (error) { error.hidden = !message; error.textContent = message; } };
	const renderList = () => {
		list.innerHTML = models[currentSite].map(([id, title, file, category], index) => `
			<button type="button" class="monument-card${index === 0 ? " is-selected" : ""}" role="listitem" data-monument="${id}" aria-pressed="${index === 0}">
				<span class="monument-index">${String(index + 1).padStart(2, "0")}</span><span><strong>${title}</strong><small>${siteNames[currentSite]} · ${category}</small></span><i aria-hidden="true">↗</i>
			</button>`).join("");
		list.querySelectorAll("[data-monument]").forEach((card, index) => card.addEventListener("click", () => selectModel(index)));
		selectModel(0);
	};
	const selectModel = (index) => {
		currentModel = models[currentSite][index];
		const [id, title, file, category] = currentModel;
		list.querySelectorAll("[data-monument]").forEach((card, cardIndex) => { const selected = cardIndex === index; card.classList.toggle("is-selected", selected); card.setAttribute("aria-pressed", selected); });
		text("#monument-category", `${category} · reconstructed model`); text("#monument-title", title); text("#monument-status", `Explore the reconstructed ${title} from every angle.`);
		text("#detail-number", `${String(index + 1).padStart(2, "0")} / ${String(models[currentSite].length).padStart(2, "0")}`); text("#detail-title", title); text("#detail-description", `${title} is part of the ${siteNames[currentSite]} collection. Compare its reconstructed form with the history of this remarkable heritage site.`); text("#detail-survival", "Archaeological remains and historical records"); text("#detail-era", currentSite === "hampi" ? "14th–16th Century Vijayanagara Empire" : currentSite === "nalanda" ? "5th–12th Century CE" : "17th Century Maratha Empire");
		viewer?.setAttribute("alt", `Interactive 3D reconstruction of ${title} at ${siteNames[currentSite]}`); viewer?.setAttribute("src", `/static/models/${currentSite}/${encodeURIComponent(file)}`); showError();
	};
	document.querySelectorAll("[data-site]").forEach((tab) => tab.addEventListener("click", () => { currentSite = tab.dataset.site; document.querySelectorAll("[data-site]").forEach((item) => { const selected = item === tab; item.classList.toggle("is-selected", selected); item.setAttribute("aria-selected", selected); }); renderList(); }));
	viewer?.addEventListener("progress", (event) => { const value = event.detail?.totalProgress ?? 0; if (progress && progressBar) { progress.hidden = value >= 1; progressBar.style.width = `${Math.round(value * 100)}%`; } });
	viewer?.addEventListener("load", () => { if (progress) progress.hidden = true; showError(); });
	viewer?.addEventListener("error", () => { if (progress) progress.hidden = true; showError("This reconstruction could not load. Please refresh the page and try again."); });
	rotationButton?.addEventListener("click", () => { rotationEnabled = !rotationEnabled; if (rotationEnabled) viewer?.setAttribute("auto-rotate", ""); else viewer?.removeAttribute("auto-rotate"); rotationButton.setAttribute("aria-pressed", rotationEnabled); rotationButton.title = rotationEnabled ? "Pause rotation" : "Start rotation"; });
	resetButton?.addEventListener("click", () => { viewer?.setAttribute("camera-orbit", "45deg 70deg auto"); viewer?.jumpCameraToGoal?.(); });
	renderList();
});
