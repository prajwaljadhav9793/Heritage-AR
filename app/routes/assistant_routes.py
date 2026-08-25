from flask import Blueprint, jsonify, render_template, request

from app.services.heritage_ai.rag_service import ask_heritage_ai


assistant_bp = Blueprint(
    "assistant",
    __name__,
    url_prefix="/assistant"
)


@assistant_bp.get("/")
def assistant():
    return render_template("assistant/assistant.html")


@assistant_bp.post("/api/ask")
def ask_assistant():

    # Get JSON request
    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()

    # Check empty question
    if not question:
        return jsonify({
            "answer": "Please enter a question.",
            "sources": []
        }), 400

    try:

        # Send question to RAG system
        result = ask_heritage_ai(question)

        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"]
        })

    except Exception as e:

        print("HeritageAI Error:", e)

        return jsonify({
            "answer": "Sorry, HeritageAI is currently unavailable.",
            "sources": []
        }), 500