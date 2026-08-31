"""Augmented-reality reconstruction routes."""

from flask import Blueprint, render_template


ar_bp = Blueprint("ar", __name__, url_prefix="/ar")


@ar_bp.get("/")
def experience():
    """Open the camera-first AR experience."""
    return render_template("ar/camera_experience.html")


@ar_bp.get("/camera")
def camera():
    """Open the camera-first AR experience."""
    return render_template("ar/camera_experience.html")


@ar_bp.get("/field-guide")
def field_guide():
    """Open the full reconstruction explorer."""
    return render_template("ar/experience.html", initial_view="guide")
