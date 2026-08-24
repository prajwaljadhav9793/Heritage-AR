from flask import Blueprint, render_template

timeline_bp = Blueprint("timeline", __name__, url_prefix="/timeline")

EVENTS = [
	{"year": "1648", "label": "Early Maratha period", "title": "The First Foundations", "description": "Raigad begins its journey as a mountain stronghold, later chosen for its natural defenses and commanding view of the Sahyadris."},
	{"year": "1656", "label": "Raigad comes under Shivaji Maharaj", "title": "A Fort Reclaimed", "description": "Chhatrapati Shivaji Maharaj takes control of the fort and begins transforming it into the capital of a new empire."},
	{"year": "1674", "label": "Coronation", "title": "The Grand Coronation of 1674", "description": "On June 6, 1674, Shivaji Maharaj was formally crowned Chhatrapati at Raigad Fort. This pivotal moment established Raigad as the impregnable capital of a new, sovereign kingdom."},
	{"year": "1680", "label": "Political transition", "title": "A Capital in Transition", "description": "Raigad remains at the heart of the Maratha kingdom as a new chapter begins after the reign of Shivaji Maharaj."},
	{"year": "1818", "label": "End of Maratha rule", "title": "The Fortress Falls Silent", "description": "The fort's political era comes to an end, leaving behind a powerful architectural and cultural legacy."},
	{"year": "2026", "label": "Digital heritage reconstruction", "title": "The Past, Reconstructed", "description": "Modern tools bring Raigad's history back into view, helping a new generation experience the monument beyond its ruins."},
]


@timeline_bp.get("/")
def timeline():
	return render_template("timeline/timeline.html", events=EVENTS, selected_event=EVENTS[2])
