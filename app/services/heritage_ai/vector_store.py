import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[3]
CHUNKS_PATH = str(PROJECT_DIR / "data" / "heritage_chunks.json")
VECTOR_DB_PATH = str(PROJECT_DIR / "data" / "vector_db")

try:
    import chromadb
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name="heritage_knowledge")
except Exception:
    chromadb = None
    client = None
    collection = None


def search_heritage(question, n_results=3):
    if not collection:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []

    for i, document in enumerate(results["documents"][0]):

        retrieved.append({
            "content": document,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved


if __name__ == "__main__":

    question = input("\nAsk HeritageAI: ")

    results = search_heritage(question)

    print("\n" + "=" * 70)
    print("RETRIEVED INFORMATION")
    print("=" * 70)

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")
        print("-" * 50)

        print("Section:", result["metadata"]["section"])
        print("Distance:", result["distance"])
        print("Content:")
        print(result["content"])