from flask import Blueprint, render_template


voice_assistant_bp = Blueprint("voice_assistant", __name__, url_prefix="/voice-assistant")


@voice_assistant_bp.get("/")
def voice_assistant():
    return render_template("voice_assistant/index.html")
