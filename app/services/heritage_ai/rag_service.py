import re
import os
import json
import time
import threading
from functools import lru_cache
from pathlib import Path

# ==========================================================
# CONFIGURATION
# ==========================================================

VECTOR_DB_PATH = str(Path(__file__).resolve().parents[3] / "data" / "vector_db")
CHUNKS_PATH = Path(__file__).resolve().parents[3] / "data" / "heritage_chunks.json"
MAX_DISTANCE = 1.55

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "4"))

try:
    import ollama
    ollama_client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)
except Exception:
    ollama = None
    ollama_client = None


# ==========================================================
# CHROMADB (OPTIONAL AT RUNTIME)
# ==========================================================

try:
    import chromadb
    chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = chroma_client.get_collection(name="heritage_knowledge")
except Exception:
    chromadb = None
    chroma_client = None
    collection = None


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


@lru_cache(maxsize=128)
def retrieve_context_cached(question, n_results=3):
    return retrieve_context(question, n_results)


def retrieve_context(question, n_results=3):
    """Retrieve locally without triggering Chroma's first-use model download."""
    question_stems = get_keyword_stems(question)
    normalized_question = question.lower()
    site_aliases = {
        "halebidu": "hoysaleshwara",
        "meenakshi amman": "meenakshi",
        "martand sun": "martand",
        "konark sun": "konark",
    }
    requested_site = next(
        (site for site in ("raigad", "hampi", "nalanda", "konark", "martand", "khajuraho", "meenakshi", "hoysaleshwara")
         if site in normalized_question),
        None,
    )
    if not requested_site:
        for alias, site in site_aliases.items():
            if alias in normalized_question:
                requested_site = site
                break
    scored_chunks = []

    for chunk in load_heritage_chunks():
        if requested_site and requested_site not in chunk["site"].lower():
            continue
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
        normalized_question = re.sub(r"[^a-z0-9 ]", "", question.lower()).strip()
        normalized_content = re.sub(r"[^a-z0-9 ]", "", chunk["content"].lower())
        if normalized_question in normalized_content:
            score += 12
        if "built" in question_stems or "builder" in question_stems or "architect" in question_stems:
            construction_phrases = (
                "built by king narasimhadeva",
                "commissioned in the 13th century",
                "oversaw the construction and development",
                "chief engineer hiroji indulkar",
                "laitaditya muktapida commissions",
                "harihara i and bukka raya i found",
            )
            if any(phrase in normalized_content for phrase in construction_phrases):
                score += 8
            if any(name in normalized_content for name in ("hiroji indulkar", "narasimhadeva", "lalitaditya", "harihara")):
                score += 4
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
        # Konark Sun Temple terms
        "konark", "surya", "sun", "odisha", "odissi", "ganga", "narasimhadeva",
        "chariot", "wheel", "temple", "kalinga", "unesco", "odisha",
        # Martand Sun Temple terms
        "martand", "kashmir", "anantnag", "lalitaditya", "muktapida", "surya",
        "courtyard", "colonnade", "shrine", "pradakshina", "blackstone",
        # Meenakshi Amman Temple terms
        "meenakshi", "madurai", "sundareshwarar", "vaigai", "gopuram", "gopurams",
        "pandya", "thousand", "pillar", "potramarai", "kulam", "mandapa", "mandapam",
        "parvati", "shiva", "tamil", "nadu", "dravidian", "prakara",
        # Hoysaleshwara Temple terms
        "hoysaleshwara", "hoysala", "halebidu", "belur", "karnataka",
        "nandi", "madanika", "madanikas", "garbhagriha", "vimana", "shikhara",
        "soapstone", "ketamalla", "vishnuvardhana", "malik", "kafur",
    }
    has_historical_year = any(keyword.isdigit() and len(keyword) == 4 for keyword in matching_keywords)
    if not question_keywords.intersection(heritage_terms) and not has_historical_year and len(matching_keywords) < 2:
        return False

    return True


# ==========================================================
# HERITAGE AI
# ==========================================================

def build_context_fallback(question, retrieved):
    """Produce a focused answer by scoring individual sentences against the
    question, so the response contains the sentences that actually answer it
    (e.g. the 'who built it' sentence, not generic intro text)."""
    if not retrieved:
        return "I don't have this information in the HeritageAI knowledge base."

    question_stems = get_keyword_stems(question)
    question_words = get_keywords(question)

    scored_sentences = []
    for rank, item in enumerate(retrieved):
        text = re.sub(r"\s+", " ", item["content"]).strip()
        sentences = [
            s.strip() for s in re.split(r"(?<=[.!?])\s+", text)
            if len(s.strip()) > 25 and not s.strip().endswith("?")
        ]
        chunk_bonus = max(0, 3 - rank)  # earlier (higher-ranked) chunks score higher
        for position, sentence in enumerate(sentences):
            sent_stems = get_keyword_stems(sentence)
            overlap = len(question_stems.intersection(sent_stems))
            if overlap == 0:
                continue
            score = overlap * 2 + chunk_bonus - position * 0.05
            scored_sentences.append((score, position, sentence))

    if not scored_sentences:
        # No sentence matched - fall back to the start of the top chunk.
        top = re.sub(r"\s+", " ", retrieved[0]["content"]).strip()
        return top[:400] + ("..." if len(top) > 400 else "")

    # Keep sentences in their original reading order for a coherent answer.
    scored_sentences.sort(key=lambda item: (-item[0], item[1]))
    selected = []
    used_positions = set()
    total_len = 0
    for score, position, sentence in scored_sentences:
        if position in used_positions:
            continue
        if total_len + len(sentence) > 500 and selected:
            break
        selected.append(sentence)
        used_positions.add(position)
        total_len += len(sentence)
        if total_len > 350 and len(selected) >= 2:
            break

    selected.sort(key=lambda s: scored_sentences[[x[2] for x in scored_sentences].index(s)][1])
    return " ".join(selected)


def _warm_up_model():
    """Pre-load the Ollama model in the background so user questions are fast."""
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return
    if not ollama_client:
        return

    def warm():
        try:
            ollama_client.chat(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": "hi"}],
                options={"temperature": 0, "num_predict": 1},
                keep_alive="30m",
            )
        except Exception:
            pass

    threading.Thread(target=warm, daemon=True).start()


_warm_up_model()


_llm_state = {"healthy": True, "retry_after": 0.0}
_LLM_RETRY_SECONDS = 60.0


def _llm_available():
    return ollama_client is not None and (_llm_state["healthy"] or time.time() >= _llm_state["retry_after"])


def _mark_llm_unhealthy():
    _llm_state["healthy"] = False
    _llm_state["retry_after"] = time.time() + _LLM_RETRY_SECONDS


def _mark_llm_healthy():
    _llm_state["healthy"] = True


def ask_heritage_ai(question):

    question = (question or "").strip()
    retrieved = retrieve_context_cached(question)

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

    if _llm_available():
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
                    "temperature": 0,
                    "num_predict": 300,
                },
                keep_alive="30m",
            )
            answer = response["message"]["content"].strip()
            _mark_llm_healthy()
            if answer.lower().startswith("i don't have this information") or not answer:
                answer = build_context_fallback(question, retrieved)
        except Exception as exc:
            _mark_llm_unhealthy()
            print(f"HeritageAI model unavailable: {exc}")
            answer = build_context_fallback(question, retrieved)
    else:
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