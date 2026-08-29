from flask import Blueprint, render_template, request

timeline_bp = Blueprint("timeline", __name__, url_prefix="/timeline")

RAIGAD_EVENTS = [
	{"year": "1648", "label": "Early Maratha period", "title": "The First Foundations", "description": "Raigad begins its journey as a mountain stronghold, later chosen for its natural defenses and commanding view of the Sahyadris.", "image": "/static/images/timeline/raigad-gateway.jpg", "fallback": "/static/images/historical/then-fort.jpg"},
	{"year": "1656", "label": "Raigad comes under Shivaji Maharaj", "title": "A Fort Reclaimed", "description": "Chhatrapati Shivaji Maharaj takes control of the fort and begins transforming it into the capital of a new empire.", "image": "/static/images/timeline/raigad-aerial.jpg", "fallback": "/static/images/heritage/discover-fort.jpg"},
	{"year": "1674", "label": "Coronation", "title": "The Grand Coronation of 1674", "description": "On June 6, 1674, Shivaji Maharaj was formally crowned Chhatrapati at Raigad Fort. This pivotal moment established Raigad as the impregnable capital of a new, sovereign kingdom.", "image": "/static/images/timeline/raigad-coronation.jpg", "fallback": "/static/images/historical/raigad-coronation.jpg"},
	{"year": "1680", "label": "Political transition", "title": "A Capital in Transition", "description": "Raigad remains at the heart of the Maratha kingdom as a new chapter begins after the reign of Shivaji Maharaj.", "image": "/static/images/timeline/political-transition.jpg", "fallback": "/static/images/historical/now-fort.jpg"},
	{"year": "1818", "label": "End of Maratha rule", "title": "The Fortress Falls Silent", "description": "The fort's political era comes to an end, leaving behind a powerful architectural and cultural legacy.", "image": "/static/images/timeline/raigad-landscape.jpg", "fallback": "/static/images/historical/now-fort.jpg"},
	{"year": "2026", "label": "Digital heritage reconstruction", "title": "The Past, Reconstructed", "description": "Modern tools bring Raigad's history back into view, helping a new generation experience the monument beyond its ruins.", "image": "/static/images/heritage/reconstruct.png", "fallback": "/static/images/heritage/reconstruct.png"},
]

HAMPI_EVENTS = [
	{"year": "7th c.", "label": "Sacred beginnings", "title": "Pampakshetra", "description": "The site long known as Pampakshetra, the field of the goddess Pampa, becomes a place of worship associated with the legends of the Ramayana and the monkey kingdom of Kishkindha.", "image": "/static/images/timeline/hampi-lakshmi-narasimha.png", "fallback": "/static/images/historical/then-fort.jpg"},
	{"year": "1336", "label": "Founding of an empire", "title": "Vijayanagara Rises", "description": "Harihara I and Bukka Raya I found the Vijayanagara Empire on the banks of the Tungabhadra, beginning the construction of a capital that will become one of the largest cities in the world.", "image": "/static/images/timeline/hampi-royal-centre-ruins.png", "fallback": "/static/images/historical/now-fort.jpg"},
	{"year": "1509", "label": "Golden age", "title": "Krishnadevaraya's Reign", "description": "Under Krishnadevaraya the empire reaches its greatest extent. Temples, pillared halls and bazaars flourish, and foreign travellers marvel at the city's wealth.", "image": "/static/images/timeline/hampi-elephant-stables.png", "fallback": "/static/images/historical/raigad-coronation.jpg"},
	{"year": "1565", "label": "Battle of Talikota", "title": "The City Falls", "description": "The Deccan Sultanates defeat Vijayanagara at Talikota. The victorious armies sack and burn Hampi for months, and the capital is abandoned.", "image": "/static/images/timeline/hampi-hazara-rama-temple.png", "fallback": "/static/images/historical/now-fort.jpg"},
	{"year": "1800s", "label": "Rediscovery", "title": "Ruins Rediscovered", "description": "British surveyors and archaeologists document the overgrown ruins, beginning the long process of study and conservation of the lost capital.", "image": "/static/images/timeline/hampi-lotus-mahal-interior.png", "fallback": "/static/images/historical/then-fort.jpg"},
	{"year": "1986", "label": "UNESCO recognition", "title": "A World Heritage Site", "description": "UNESCO inscribes the Group of Monuments at Hampi on the World Heritage List, securing its place among the great heritage sites of the world.", "image": "/static/images/timeline/virupaksha.jpg", "fallback": "/static/images/heritage/reconstruct.png"},
]

SITES = {
	"raigad": {
		"name": "Raigad Fort",
		"subtitle": "Hill fortress",
		"heading": "RAIGAD<br />THROUGH TIME",
		"kicker": "HeritageAR / The Maratha archive",
		"note": "Raigad Fort archive is currently open.",
		"events": RAIGAD_EVENTS,
		"default_event": 2,
	},
	"hampi": {
		"name": "Hampi",
		"subtitle": "Vijayanagara ruins",
		"heading": "HAMPI<br />THROUGH TIME",
		"kicker": "HeritageAR / The Vijayanagara archive",
		"note": "Hampi archive is currently open.",
		"events": HAMPI_EVENTS,
		"default_event": 1,
	},
}


@timeline_bp.get("/")
def timeline():
	site_key = request.args.get("site", "raigad")
	site = SITES.get(site_key, SITES["raigad"])
	events = site["events"]
	return render_template(
		"timeline/timeline.html",
		events=events,
		selected_event=events[site["default_event"]],
		site_key=site_key if site_key in SITES else "raigad",
		site=site,
		sites=SITES,
	)
