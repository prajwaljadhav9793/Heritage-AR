import re
import chromadb
import ollama


# ==========================================================
# CONFIGURATION
# ==========================================================

VECTOR_DB_PATH = "data/vector_db"

# Based on your actual retrieval tests.
# Genuine questions can reach around 0.92,
# while the clearly unrelated favorite-food question
# was above 1.03.
MAX_DISTANCE = 0.95

MODEL_NAME = "qwen2.5:0.5b"


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
        r"[a-zA-Z]+",
        text.lower()
    )

    keywords = [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) >= 3
    ]

    return set(keywords)


# ==========================================================
# RETRIEVE FROM CHROMADB
# ==========================================================

def retrieve_context(question, n_results=3):

    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved = []

    for i, document in enumerate(
        results["documents"][0]
    ):

        retrieved.append({
            "content": document,
            "section": results["metadatas"][0][i]["section"],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })

    return retrieved


# ==========================================================
# RELEVANCE CHECK
# ==========================================================

def is_relevant(question, retrieved):

    if not retrieved:
        return False

    question_keywords = get_keywords(question)

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

    matching_keywords = []

    for keyword in question_keywords:

        if keyword in combined_context:
            matching_keywords.append(keyword)

    # If the question contains useful words but
    # none of them occur in the retrieved context,
    # reject the context.

    if question_keywords and not matching_keywords:
        return False

    return True


# ==========================================================
# HERITAGE AI
# ==========================================================

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

    response = ollama.chat(

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

    # ------------------------------------------------------
    # RETURN RESULT
    # ------------------------------------------------------

    return {
        "answer": answer,
        "sources": [
            {
                "section": item["section"],
                "source": item["source"]
            }
            for item in retrieved
        ]
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