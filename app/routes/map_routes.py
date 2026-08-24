from flask import Blueprint, render_template

map_bp = Blueprint("map", __name__, url_prefix="/map")


@map_bp.get("/")
def heritage_map():
	return render_template("map/heritage_map.html")
