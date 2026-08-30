from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def index():
    return render_template("home/index.html")


@home_bp.get("/world")
def world():
    """Display the 3D reconstructed models world."""
    return render_template("3d/world.html")
