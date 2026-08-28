from app.services.heritage_ai.rag_service import retrieve_context, is_relevant

questions = [
    "Tell me about the Stone Chariot",
    "Who founded the Vijayanagara Empire?",
    "What happened at the Battle of Talikota?",
    "What is the musical pillar temple called?",
    "What is the capital of France?",
    "Where is Shivaji Maharaj samadhi?",
    "Tell me about the Hirakani Buruj",
]

for q in questions:
    retrieved = retrieve_context(q)
    relevant = is_relevant(q, retrieved)
    top = retrieved[0] if retrieved else None
    print(f"{q!r:55} relevant={relevant}  top={top['section'] if top else None} ({top['source'] if top else '-'})")
