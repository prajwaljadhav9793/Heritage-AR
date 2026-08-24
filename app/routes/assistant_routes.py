import json
from pathlib import Path

from flask import Blueprint, jsonify, render_template, request

assistant_bp = Blueprint("assistant", __name__, url_prefix="/assistant")
SAMPLES_PATH = Path(__file__).resolve().parents[2] / "data" / "assistant_samples.json"


def load_samples():
	return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


@assistant_bp.get("/")
def assistant():
	return render_template("assistant/assistant.html")


@assistant_bp.post("/api/ask")
def ask_assistant():
	question = request.get_json(silent=True).get("question", "") if request.is_json else ""
	normalized_question = question.lower()
	samples = load_samples()
	answer = samples["fallback"]
	for topic in samples["topics"]:
		if any(keyword in normalized_question for keyword in topic["keywords"]):
			answer = topic["answer"]
			break
	return jsonify({"answer": answer})
