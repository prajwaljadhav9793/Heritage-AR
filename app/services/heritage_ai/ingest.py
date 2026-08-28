"""
Load heritage chunks into the ChromaDB vector store.

Run after chunker.py whenever a new place is added:

    python -m app.services.heritage_ai.ingest

Uses upsert, so re-running is safe and never duplicates data.
"""
import json

from app.services.heritage_ai.vector_store import CHUNKS_PATH, collection


def main():
    with open(CHUNKS_PATH, encoding="utf-8") as file:
        chunks = json.load(file)

    # Remove entries whose source document is no longer present
    # (e.g. a replaced or renamed docx).
    active_sources = {chunk["source"] for chunk in chunks}
    existing = collection.get(include=["metadatas"])
    stale_ids = [
        existing["ids"][i]
        for i, metadata in enumerate(existing["metadatas"])
        if metadata.get("source") not in active_sources
    ]
    if stale_ids:
        collection.delete(ids=stale_ids)
        print(f"Removed {len(stale_ids)} stale chunks.")

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "site": chunk["site"],
            "section": chunk["section"],
            "source": chunk["source"],
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Upserted {len(chunks)} chunks.")
    print(f"Collection now holds {collection.count()} chunks total.")


if __name__ == "__main__":
    main()
