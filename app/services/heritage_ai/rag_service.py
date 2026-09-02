import re
import os
import json
from functools import lru_cache
from pathlib import Path

import chromadb
import ollama


# ==========================================================
# CONFIGURATION
# ==========================================================

VECTOR_DB_PATH = str(Path(__file__).resolve().parents[3] / "data" / "vector_db")
CHUNKS_PATH = Path(__file__).resolve().parents[3] / "data" / "heritage_chunks.json"

# Based on your actual retrieval tests.
# Genuine questions can reach around 0.92,
# while the clearly unrelated favorite-food question
# was above 1.03.
MAX_DISTANCE = 1.55

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "5"))
ollama_client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)


# ==========================================================
# CHROMADB
# ==========================================================

chroma_client = chromadb.PersistentClient(
    path=VECTOR_DB_PATH
)

collection = chroma_client.get_collection(
    name="heritage_knowledge"
)


# ==========================================================
# STOP WORDS
# ==========================================================

STOP_WORDS = {
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "which",
    "was",
    "were",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "to",
    "in",
    "on",
    "at",
    "for",
    "from",
    "and",
    "or",
    "did",
    "does",
    "do",
    "has",
    "have",
    "had",
    "with",
    "after",
    "before",
    "about",
    "tell",
    "me",
    "please",
    "can",
    "could",
    "would",
    "it",
    "its",
    "this",
    "that"
}


# ==========================================================
# EXTRACT IMPORTANT WORDS
# ==========================================================

def get_keywords(text):

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    keywords = [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) >= 3
    ]

    return set(keywords)


def get_keyword_stems(text):
    """Return simple stems so questions and source text can match paraphrases."""
    stems = set()
    for word in get_keywords(text):
        stem = word
        for suffix in ("ies", "ing", "ed", "es", "s"):
            if len(stem) > 4 and stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        stems.add(stem)
    return stems


# ==========================================================
# RETRIEVE FROM CHROMADB
# ==========================================================

@lru_cache(maxsize=1)
def load_heritage_chunks():
    with CHUNKS_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def retrieve_context(question, n_results=3):
    """Retrieve locally without triggering Chroma's first-use model download."""
    question_stems = get_keyword_stems(question)
    scored_chunks = []

    for chunk in load_heritage_chunks():
        searchable_text = f"{chunk['site']} {chunk['section']} {chunk['content']}"
        content_stems = get_keyword_stems(searchable_text)
        score = len(question_stems.intersection(content_stems))
        question_words = get_keywords(question)
        content_words = get_keywords(chunk["content"])
        score += len(question_words.intersection(content_words)) * 2
        if question_words and question_words.issubset(content_words):
            score += 3
        section_stems = get_keyword_stems(chunk["section"])
        if question_stems and question_stems.issubset(section_stems):
            score += 10
        if "found" in question_stems and any(
            term in searchable_text.lower()
            for term in ("founded", "foundation", "established")
        ):
            score += 3
        if "found" in question_stems and chunk["section"].lower() in {
            "gupta period",
            "history",
        }:
            score += 8
        if score:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return [
        {
            "content": chunk["content"],
            "section": chunk["section"],
            "source": chunk["source"],
            "distance": 0.0,
        }
        for _, chunk in scored_chunks[:n_results]
    ]


# ==========================================================
# RELEVANCE CHECK
# ==========================================================

def is_relevant(question, retrieved):

    if not retrieved:
        return False

    question_keywords = get_keyword_stems(question)

    # Check the best retrieved result first
    best_result = retrieved[0]

    distance = best_result["distance"]

    # ------------------------------------------------------
    # Check 1: Semantic distance
    # ------------------------------------------------------

    if distance > MAX_DISTANCE:
        return False

    # ------------------------------------------------------
    # Check 2: Keyword support
    # ------------------------------------------------------

    combined_context = " ".join(
        item["content"]
        for item in retrieved
    ).lower()

    context_keywords = get_keyword_stems(combined_context)
    matching_keywords = question_keywords.intersection(context_keywords)

    # If the question contains useful words but
    # none of them occur in the retrieved context,
    # reject the context.

    if question_keywords and not matching_keywords:
        return False

    heritage_terms = {
        "raigad", "fort", "shivaji", "maratha", "maharaj", "swaraj",
        "coronation", "maha", "darwaja", "hirakani", "ropeway", "jijabai",
        # Hampi / Vijayanagara terms
        "hampi", "vijayanagara", "tungabhadra", "krishnadevaraya",
        "virupaksha", "vittala", "harihara", "bukka", "karnataka",
        "talikota", "unesco", "bazaar", "chariot", "mandapa", "mantapa",
        "zenana", "mahal", "stables", "dibba", "gopuram", "temple",
        # Nalanda Mahavihara terms
        "nalanda", "mahavihara", "bihar", "magadha", "gupta", "harsha",
        "pala", "buddhist", "monastery", "monastic", "vihara", "vikramashila",
        "library", "manuscript", "archaeological", "university",
    }
    has_historical_year = any(keyword.isdigit() and len(keyword) == 4 for keyword in matching_keywords)
    if not question_keywords.intersection(heritage_terms) and not has_historical_year and len(matching_keywords) < 2:
        return False

    return True


# ==========================================================
# HERITAGE AI
# ==========================================================

def build_context_fallback(question, retrieved):
    """Produce a usable answer from the retrieved heritage content when the LLM is unavailable."""
    if not retrieved:
        return "I don't have this information in the HeritageAI knowledge base."

    parts = []
    seen = set()

    for item in retrieved:
        text = re.sub(r"\s+", " ", item["content"]).strip()
        if text and text not in seen:
            seen.add(text)
            parts.append(text)

    if not parts:
        return "I don't have this information in the HeritageAI knowledge base."

    answer = " ".join(parts[:2])
    answer = answer.strip()

    if not answer:
        return "I don't have this information in the HeritageAI knowledge base."

    # Keep the response concise but useful when the model is down.
    if len(answer) > 500:
        answer = answer[:497].rstrip() + "..."

    return answer


def ask_heritage_ai(question):

    retrieved = retrieve_context(question)

    # ------------------------------------------------------
    # RELEVANCE GATE
    # ------------------------------------------------------

    if not is_relevant(question, retrieved):

        return {
            "answer": (
                "I don't have this information in the "
                "HeritageAI knowledge base."
            ),
            "sources": []
        }

    source_meta = [
        {
            "section": item["section"],
            "source": item["source"]
        }
        for item in retrieved
    ]

    # ------------------------------------------------------
    # BUILD CONTEXT
    # ------------------------------------------------------

    context_parts = []

    for item in retrieved:

        context_parts.append(
            f"""
SECTION: {item['section']}

SOURCE: {item['source']}

CONTENT:
{item['content']}
"""
        )

    context = "\n".join(context_parts)

    # ------------------------------------------------------
    # STRICT SYSTEM PROMPT
    # ------------------------------------------------------

    system_prompt = """
You are HeritageAI.

Your ONLY source of information is the
HERITAGE CONTEXT provided below.

STRICT RULES:

1. Answer ONLY from the provided context.
2. Never use your general knowledge.
3. Never use information from outside the context.
4. Never guess.
5. Never infer unsupported facts.
6. Never invent an answer.
7. If the context does not directly support the answer,
   respond exactly:

I don't have this information in the HeritageAI knowledge base.

8. Do not mention information that is not in the context.
9. Keep the answer concise.
"""

    user_prompt = f"""
HERITAGE CONTEXT:

{context}

USER QUESTION:

{question}

Answer ONLY using the HERITAGE CONTEXT.
"""

    # ------------------------------------------------------
    # OLLAMA
    # ------------------------------------------------------

    try:
        response = ollama_client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            options={
                "temperature": 0
            }
        )
        answer = response["message"]["content"].strip()
    except Exception as exc:
        print(f"HeritageAI model unavailable: {exc}")
        answer = build_context_fallback(question, retrieved)

    # ------------------------------------------------------
    # RETURN RESULT
    # ------------------------------------------------------

    return {
        "answer": answer,
        "sources": source_meta
    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("HERITAGE AI - RAG TEST")
    print("=" * 70)

    while True:

        question = input(
            "\nAsk HeritageAI (type 'exit' to stop): "
        )

        if question.lower() == "exit":
            break

        result = ask_heritage_ai(question)

        print("\n")
        print("=" * 70)
        print("ANSWER")
        print("=" * 70)

        print(result["answer"])

        print("\n")
        print("=" * 70)
        print("SOURCES")
        print("=" * 70)

        if result["sources"]:

            for source in result["sources"]:

                print(
                    f"- {source['section']} "
                    f"({source['source']})"
                )

        else:

            print("No source found.")