import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.heritage_ai.rag_service import ask_heritage_ai, retrieve_context

for q in [
    "Who built the Khajuraho temples?",
    "Where is Khajuraho located?",
    "Tell me about the Kandariya Mahadeva temple.",
    "What is the best food in Paris?",
]:
    result = ask_heritage_ai(q)
    print("=" * 60)
    print("Q:", q)
    print("A:", result["answer"][:200])
    print("Sources:", [s["source"] for s in result["sources"]][:2])
