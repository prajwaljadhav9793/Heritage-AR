"""One-off: extract Meenakshi Temple.docx into chunks, add them to
data/heritage_chunks.json and upsert into the existing ChromaDB collection.

Run from the project root:  python scripts/ingest_meenakshi.py
"""
import json
import re
import sys
from pathlib import Path

import chromadb
import docx
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

DOC_PATH = Path("data/documents/Meenakshi Temple.docx")
CHUNKS_PATH = Path("data/heritage_chunks.json")
SITE = "Meenakshi Temple"
SOURCE = "Meenakshi Temple.docx"
ID_PREFIX = "MT"

MIN_CHUNK_CHARS = 300
MAX_CHUNK_CHARS = 1500


def extract_sections():
    """Group docx paragraphs under heading-like short paragraphs."""
    document = docx.Document(str(DOC_PATH))
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    sections = []
    current_title = "Introduction"
    buffer = []
    for text in paragraphs:
        is_heading = len(text) < 60 and not text.endswith((".", ":", ")"))
        if is_heading:
            if buffer:
                sections.append((current_title, " ".join(buffer)))
                buffer = []
            if text.lower() != SITE.lower():
                current_title = text
        else:
            buffer.append(text)
    if buffer:
        sections.append((current_title, " ".join(buffer)))
    return sections


def build_chunks(sections):
    chunks = []
    index = 1
    for title, body in sections:
        body = re.sub(r"\s+", " ", body).strip()
        if not body:
            continue
        sentences = re.split(r"(?<=[.!?])\s+", body)
        part, part_no = [], 1
        for sentence in sentences:
            part.append(sentence)
            if sum(len(s) + 1 for s in part) >= MAX_CHUNK_CHARS:
                text = " ".join(part).strip()
                chunk_id = f"{ID_PREFIX}-{index:03d}" + (f"-{part_no:02d}" if part_no > 1 else "")
                chunks.append({"id": chunk_id, "site": SITE, "section": title, "content": text, "source": SOURCE})
                part, part_no = [], part_no + 1
        if part:
            text = " ".join(part).strip()
            if len(text) < MIN_CHUNK_CHARS and chunks and chunks[-1]["section"] == title:
                chunks[-1]["content"] += " " + text
            else:
                chunk_id = f"{ID_PREFIX}-{index:03d}" + (f"-{part_no:02d}" if part_no > 1 else "")
                chunks.append({"id": chunk_id, "site": SITE, "section": title, "content": text, "source": SOURCE})
        index += 1
    return chunks


def main():
    sections = extract_sections()
    chunks = build_chunks(sections)
    print(f"Extracted {len(chunks)} chunks from {len(sections)} sections.")

    existing = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    known_ids = {c["id"] for c in existing}
    missing = [c for c in chunks if c["id"] not in known_ids]

    if missing:
        existing = existing + missing
        CHUNKS_PATH.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"heritage_chunks.json updated with {len(missing)} new chunks.")

    # Upsert every Meenakshi chunk currently in the JSON (deduped by id).
    seen_ids = set()
    new_chunks = []
    for c in existing:
        if c["source"] == SOURCE and c["id"] not in seen_ids:
            seen_ids.add(c["id"])
            new_chunks.append(c)
    print(f"Chunks to upsert: {len(new_chunks)}")

    # Vector-DB upsert is OPTIONAL and slow (ONNX embeddings).
    # The RAG service reads data/heritage_chunks.json directly, so this
    # step is not required for answers. Run with --embed to enable it.
    if "--embed" not in sys.argv:
        print("Skipping vector DB upsert (use --embed to enable). DONE.")
        return

    client = chromadb.PersistentClient(path="data/vector_db")
    col = client.get_collection("heritage_knowledge")

    ef = ONNXMiniLM_L6_V2()
    texts = [c["content"] for c in new_chunks]
    if not texts:
        print("Nothing to upsert.")
        return
    print("Computing embeddings...", flush=True)
    embeddings = ef(texts)
    print("Embeddings done.")

    col.upsert(
        ids=[c["id"] for c in new_chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"site": c["site"], "section": c["section"], "source": c["source"]} for c in new_chunks],
    )
    print(f"Collection count: {col.count()}")

    res = col.query(query_texts=["Who built the Meenakshi Temple?"], n_results=3)
    for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
        print(round(dist, 3), meta["site"], "-", meta["section"])
    print("INGEST COMPLETE")


if __name__ == "__main__":
    main()
