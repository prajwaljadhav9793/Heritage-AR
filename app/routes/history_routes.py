from flask import Blueprint, render_template

history_bp = Blueprint("history", __name__, url_prefix="/history")


@history_bp.get("/then-vs-now")
def then_vs_now():
    return render_template("history/then_vs_now.html")