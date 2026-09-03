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

NALANDA_EVENTS = [
	{"year": "5th c.", "label": "Gupta foundation", "title": "A Mahavihara Takes Shape", "description": "Nalanda develops as a major Buddhist centre of learning in the Gupta period, traditionally associated with Kumaragupta I.", "image": "/static/images/timeline/images.jpg", "fallback": "/static/images/heritage/nalanda-ruins.jpg"},
	{"year": "7th c.", "label": "Harsha's patronage", "title": "Scholars Gather from Asia", "description": "Under Harshavardhana and other patrons, Nalanda flourishes and attracts scholars including the Chinese Buddhist traveller Xuanzang.", "image": "/static/images/timeline/9f75259e9233645e4c07bc46c926289f.jpg", "fallback": "/static/images/heritage/nalanda-ruins.jpg"},
	{"year": "8th-12th c.", "label": "Pala period", "title": "The Scholarly Centre Expands", "description": "Pala rulers support Nalanda's monasteries, scholarship and connections with other Buddhist centres such as Vikramashila and Odantapuri.", "image": "/static/images/timeline/nalanda-ruins.jpg", "fallback": "/static/images/heritage/nalanda-ruins.jpg"},
	{"year": "c. 1200", "label": "Invasions and decline", "title": "A Long Tradition Falls Silent", "description": "Attacks, political change and the loss of royal patronage damage Nalanda and eventually end its role as a major residential centre of learning.", "image": "/static/images/timeline/images (1).jpg", "fallback": "/static/images/heritage/nalanda-ruins.jpg"},
	{"year": "2016", "label": "UNESCO recognition", "title": "A World Heritage Site", "description": "Nalanda Mahavihara is inscribed as a UNESCO World Heritage Site, recognizing its global importance as an ancient centre of learning and culture.", "image": "/static/images/timeline/images.jpg", "fallback": "/static/images/heritage/nalanda-ruins.jpg"},
]

KONARK_EVENTS = [
	{"year": "13th c.", "label": "Eastern Ganga dynasty", "title": "The Sun Temple Rises", "description": "King Narasimhadeva I commissions a monumental temple dedicated to Surya on the coast of Odisha.", "image": "/static/images/timeline/konark-07.png", "fallback": "/static/images/timeline/konark-01.jpg"},
	{"year": "13th c.", "label": "Chariot architecture", "title": "A Temple Built as the Sun's Chariot", "description": "The temple is conceived as Surya's stone chariot, with richly carved walls, horses and 24 monumental wheels.", "image": "/static/images/timeline/konark-01.jpg", "fallback": "/static/images/timeline/konark-07.png"},
	{"year": "13th c.", "label": "Astronomy in stone", "title": "The Wheels Read the Sun", "description": "The carved wheels express movement, time and solar symbolism, combining architectural detail with astronomical ideas.", "image": "/static/images/timeline/konark-02.jpg", "fallback": "/static/images/timeline/konark-04.png"},
	{"year": "Later centuries", "label": "Coastal exposure", "title": "Stone, Salt and Time", "description": "Monsoon rain, salty coastal air, strong winds, sand and structural weakness gradually damage the temple complex.", "image": "/static/images/timeline/konark-03.png", "fallback": "/static/images/timeline/konark-05.png"},
	{"year": "20th c.", "label": "Conservation", "title": "A Monument Carefully Preserved", "description": "The surviving ruins and sculptures are protected and studied as an exceptional example of Kalinga architecture.", "image": "/static/images/timeline/konark-05.png", "fallback": "/static/images/timeline/konark-06.png"},
	{"year": "1984", "label": "UNESCO recognition", "title": "A World Heritage Site", "description": "UNESCO recognizes the Konark Sun Temple for its outstanding architecture, sculpture and cultural importance.", "image": "/static/images/timeline/konark-01.jpg", "fallback": "/static/images/timeline/konark-07.png"},
]

MARTAND_EVENTS = [
	{"year": "8th c.", "label": "Karkota dynasty", "title": "A Sun Temple in Kashmir", "description": "King Lalitaditya Muktapida commissions Martand as a monumental temple dedicated to Surya in the Kashmir Valley.", "image": "/static/images/timeline/martand-01.png", "fallback": "/static/images/timeline/martand-02.jpg"},
	{"year": "8th c.", "label": "Central shrine", "title": "Architecture of the Main Temple", "description": "The temple is built around a central shrine and an expansive colonnaded courtyard, combining sacred space with a powerful mountain setting.", "image": "/static/images/timeline/martand-04.png", "fallback": "/static/images/timeline/martand-01.png"},
	{"year": "8th c.", "label": "Stone craftsmanship", "title": "Pillars, Arches and Carvings", "description": "Stone pillars, gateways, arches and carved panels reveal the scale and craftsmanship of the early medieval Kashmiri temple complex.", "image": "/static/images/timeline/martand-03.png", "fallback": "/static/images/timeline/martand-06.png"},
	{"year": "Later centuries", "label": "Damage and abandonment", "title": "A Sacred Complex Falls Silent", "description": "The complex was damaged and eventually abandoned, leaving its surviving walls, shrines and courtyard as an archaeological record of Kashmir's past.", "image": "/static/images/timeline/martand-05.jpg", "fallback": "/static/images/timeline/martand-08.jpg"},
	{"year": "Today", "label": "Protected heritage", "title": "Ruins in the Kashmir Valley", "description": "Martand remains an important heritage site, valued for its architecture, history, landscape and connection to the region's solar traditions.", "image": "/static/images/timeline/martand-02.jpg", "fallback": "/static/images/timeline/martand-11.jpg"},
]

MEENAKSHI_EVENTS = [
	{"year": "6th c. CE", "label": "Sangam-era origins", "title": "A Goddess on the Vaigai", "description": "Tamil texts from the 6th century CE first reference the temple city of Madurai, where Meenakshi, a form of Parvati, and Sundareswarar, a form of Shiva, come to be worshipped.", "image": "/static/images/timeline/meenakshi-shrine.jpg", "fallback": "/static/images/timeline/meenakshi-gopuram.jpg"},
	{"year": "12th-13th c.", "label": "Pandya expansion", "title": "The Pandya Kings Build", "description": "The temple is expanded under the Pandya dynasty, notably Maravarman Sundara Pandyan, growing into one of the largest temple complexes in South India.", "image": "/static/images/timeline/meenakshi-gopuram.jpg", "fallback": "/static/images/timeline/meenakshi-aerial.jpg"},
	{"year": "16th-17th c.", "label": "Nayak rebuilding", "title": "The Nayak Golden Age", "description": "Under the Nayaka rulers and prime minister Ariyanatha Mudaliar, the towering gopurams and the famous Thousand Pillar Hall are rebuilt and added.", "image": "/static/images/timeline/meenakshi-corridor.jpg", "fallback": "/static/images/timeline/meenakshi-gopuram.jpg"},
	{"year": "16th c.", "label": "Sacred geography", "title": "Gopurams, Shrines and the Golden Lotus Pond", "description": "Concentric enclosures, fourteen gopurams and the Potramarai Kulam give the temple its monumental Dravidian form on the southern bank of the Vaigai.", "image": "/static/images/timeline/meenakshi-gopuram.jpg", "fallback": "/static/images/timeline/meenakshi-corridor.jpg"},
	{"year": "Today", "label": "Living heritage", "title": "A Temple City Alive", "description": "Meenakshi Amman Temple remains one of India's most celebrated living temples, famed for its festivals, sculptures and vibrant Tamil tradition.", "image": "/static/images/timeline/meenakshi-aerial.jpg", "fallback": "/static/images/timeline/meenakshi-gopuram.jpg"},
]

HOYSALESHWARA_EVENTS = [
	{"year": "12th c.", "label": "Hoysala patronage", "title": "Vishnuvardhana's Vision", "description": "The temple rises on the banks of a man-made lake at Halebidu, built during the Hoysala period under King Vishnuvardhana and dedicated to Shiva as Hoysaleshwara.", "image": "/static/images/timeline/halebidu-temple-exterior.jpg", "fallback": "/static/images/timeline/halebidu-entrance.jpg"},
	{"year": "12th c.", "label": "Master craftsmen", "title": "Sculpture in Soapstone", "description": "Artists carve the outer walls with friezes of the Ramayana, deities such as Harihara, Ganesha and Saraswati, and the graceful madanika bracket figures in soft chloritic schist.", "image": "/static/images/timeline/halebidu-deities-frieze.jpg", "fallback": "/static/images/timeline/halebidu-temple-exterior.jpg"},
	{"year": "12th c.", "label": "Temple layout", "title": "Twin Shrines and Nandi Pavilions", "description": "Two sanctums face Nandi shrines across a pillared mantapa, creating one of the finest ensembles of Hoysala sacred architecture.", "image": "/static/images/timeline/halebidu-sanctum-interior.jpg", "fallback": "/static/images/timeline/halebidu-entrance.jpg"},
	{"year": "1311-1326", "label": "Invasions", "title": "The Raids of Malik Kafur and the Sack of Halebidu", "description": "Two catastrophic raids by Malik Kafur's armies breach the Hoysala capital, toppling the superstructure towers and defacing the temple's sculptures.", "image": "/static/images/timeline/halebidu-entrance.jpg", "fallback": "/static/images/timeline/halebidu-deities-frieze.jpg"},
	{"year": "Today", "label": "UNESCO heritage", "title": "Belur and Halebidu Protected", "description": "The temple stands as the largest monument in Halebidu, part of the sacred ensembles recognized among UNESCO World Heritage sites, celebrated for its unmatched sculptural detail.", "image": "/static/images/timeline/halebidu-temple-exterior.jpg", "fallback": "/static/images/timeline/halebidu-sanctum-interior.jpg"},
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
	"nalanda": {
		"name": "Nalanda Mahavihara",
		"subtitle": "Ancient centre of learning",
		"heading": "NALANDA<br />THROUGH TIME",
		"kicker": "HeritageAR / The Nalanda archive",
		"note": "Nalanda Mahavihara archive is currently open.",
		"events": NALANDA_EVENTS,
		"default_event": 1,
	},
	"konark": {
		"name": "Konark Sun Temple",
		"subtitle": "13th-century chariot temple",
		"heading": "KONARK<br />THROUGH TIME",
		"kicker": "HeritageAR / The Konark archive",
		"note": "Konark Sun Temple archive is currently open.",
		"events": KONARK_EVENTS,
		"default_event": 1,
	},
	"martand": {
		"name": "Martand Sun Temple",
		"subtitle": "Ancient Kashmiri Sun temple",
		"heading": "MARTAND<br />THROUGH TIME",
		"kicker": "HeritageAR / The Martand archive",
		"note": "Martand Sun Temple archive is currently open.",
		"events": MARTAND_EVENTS,
		"default_event": 1,
	},
	"meenakshi": {
		"name": "Meenakshi Temple",
		"subtitle": "Temple city of Madurai",
		"heading": "MEENAKSHI<br />THROUGH TIME",
		"kicker": "HeritageAR / The Madurai archive",
		"note": "Meenakshi Temple archive is currently open.",
		"events": MEENAKSHI_EVENTS,
		"default_event": 1,
	},
	"hoysaleshwara": {
		"name": "Hoysaleshwara Temple",
		"subtitle": "12th-century Hoysala temple",
		"heading": "HOYSALESHWARA<br />THROUGH TIME",
		"kicker": "HeritageAR / The Halebidu archive",
		"note": "Hoysaleshwara Temple archive is currently open.",
		"events": HOYSALESHWARA_EVENTS,
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
