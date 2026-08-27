from flask import Blueprint, render_template

timeline_bp = Blueprint("timeline", __name__, url_prefix="/timeline")

EVENTS = [
	{"year": "1648", "label": "Early Maratha period", "title": "The First Foundations", "description": "Raigad begins its journey as a mountain stronghold, later chosen for its natural defenses and commanding view of the Sahyadris.", "image": "/static/images/timeline/raigad-gateway.jpg", "fallback": "/static/images/historical/then-fort.jpg"},
	{"year": "1656", "label": "Raigad comes under Shivaji Maharaj", "title": "A Fort Reclaimed", "description": "Chhatrapati Shivaji Maharaj takes control of the fort and begins transforming it into the capital of a new empire.", "image": "/static/images/timeline/raigad-aerial.jpg", "fallback": "/static/images/heritage/discover-fort.jpg"},
	{"year": "1674", "label": "Coronation", "title": "The Grand Coronation of 1674", "description": "On June 6, 1674, Shivaji Maharaj was formally crowned Chhatrapati at Raigad Fort. This pivotal moment established Raigad as the impregnable capital of a new, sovereign kingdom.", "image": "/static/images/timeline/raigad-coronation.jpg", "fallback": "/static/images/historical/raigad-coronation.jpg"},
	{"year": "1680", "label": "Political transition", "title": "A Capital in Transition", "description": "Raigad remains at the heart of the Maratha kingdom as a new chapter begins after the reign of Shivaji Maharaj.", "image": "/static/images/timeline/political-transition.jpg", "fallback": "/static/images/historical/now-fort.jpg"},
	{"year": "1818", "label": "End of Maratha rule", "title": "The Fortress Falls Silent", "description": "The fort's political era comes to an end, leaving behind a powerful architectural and cultural legacy.", "image": "/static/images/timeline/raigad-landscape.jpg", "fallback": "/static/images/historical/now-fort.jpg"},
	{"year": "2026", "label": "Digital heritage reconstruction", "title": "The Past, Reconstructed", "description": "Modern tools bring Raigad's history back into view, helping a new generation experience the monument beyond its ruins.", "image": "/static/images/heritage/reconstruct.png", "fallback": "/static/images/heritage/reconstruct.png"},
]


@timeline_bp.get("/")
def timeline():
	return render_template("timeline/timeline.html", events=EVENTS, selected_event=EVENTS[2])
