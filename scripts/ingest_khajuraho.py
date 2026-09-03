"""One-off: ingest Khajuraho chunks into the existing ChromaDB collection.

Writes precomputed ONNX MiniLM-L6-v2 embeddings directly and avoids
Chroma's embedding_function_conflict validation by using get_collection()
plus explicit embeddings (same EF as the persisted default).
"""
import json

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

chunks = json.load(open("data/heritage_chunks.json", encoding="utf-8"))
target_sources = {"Khajuraho Group of Monuments.docx"}
new_chunks = [c for c in chunks if c["source"] in target_sources]
print(f"Khajuraho chunks to upsert: {len(new_chunks)}")

client = chromadb.PersistentClient(path="data/vector_db")
col = client.get_collection("heritage_knowledge")

ef = ONNXMiniLM_L6_V2()
texts = [c["content"] for c in new_chunks]
print("Computing embeddings...")
embeddings = ef(texts)
print("Embeddings done.")

col.upsert(
    ids=[c["id"] for c in new_chunks],
    documents=texts,
    embeddings=embeddings,
    metadatas=[
        {"site": c["site"], "section": c["section"], "source": c["source"]}
        for c in new_chunks
    ],
)
print(f"Collection count: {col.count()}")

# quick sanity query
res = col.query(query_texts=["Who built the Khajuraho temples?"], n_results=3)
for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
    print(dist, meta["site"], "-", meta["section"])
print("INGEST COMPLETE")
