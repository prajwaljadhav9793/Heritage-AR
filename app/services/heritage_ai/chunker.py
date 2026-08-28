from docx import Document
import json
import os
import re


# ==========================================================
# DOCUMENT REGISTRY
# To add a new heritage place, add an entry here with its
# docx file, unique ID prefix, site name and section headings,
# then run:  python -m app.services.heritage_ai.chunker
# and:       python -m app.services.heritage_ai.ingest
# ==========================================================

DOCUMENTS = [
    {
        "key": "raigad",
        "docx": "data/documents/RAIGAD FORT.docx",
        "site": "Raigad Fort",
        "prefix": "RG",
        "source": "RAIGAD FORT.docx",
        "headings": [
        "Major features",
        "Hirakani Buruj",
        "Raigad Ropeway",
        "Reasons for the Destruction of Raigad Fort",
        "Losses Due to the Destruction of Raigad Fort",
        "Chronological Timeline of Raigad Fort",
        "Original Name of Raigad",
        "Capture by Shivaji Maharaj",
        "Raigad as the Capital",
        "Importance of the Coronation",
        "Raj Darbar",
        "Maha Darwaja",
        "Takmak Tok",
        "Queen's Palace",
        "Jagadishwar Temple",
        "Shivaji Maharaj's Samadhi",
        "Market Area",
        "Water Management",
        "Architecture of Raigad",
        "Military Importance",
        "Administrative Importance",
        "Raigad After Shivaji Maharaj",
        "Raigad During British Rule",
        "Raigad as a Symbol of Swarajya",
        "Tourism and Present-Day Importance",
        "Educational Importance",
        "UNESCO World Heritage Status (2025)",
        "Nickname and Ownership History",
        "Key Historical Events at the Fort",
        "Modern Redevelopment Project",
        "A Related but Distinct Fort",
        "Geographical factors",
        "History of Raigad",
        "Ancient History",
        "Medieval Period",
        "Rairi Before Shivaji Maharaj",
        "Shivaji Maharaj and the Transformation of Rairi",
        "Coronation of Shivaji Maharaj",
        "Administration at Raigad",
        "Death of Shivaji Maharaj",
        "Raigad and the Later Maratha Period",
        "British Period",
        "Raigad After Independence",
        "Broken Parts",
        ],
    },
    {
        "key": "hampi",
        "docx": "data/documents/Hampi info.docx",
        "site": "Hampi",
        "prefix": "HM",
        "source": "Hampi info.docx",
        # Split on the document's real Heading 1/2/3 styles
        # instead of a hard-coded heading list.
        "use_styles": True,
        "headings": [],
    },
]

OUTPUT_PATH = "data/heritage_chunks.json"


def clean_text(text):
    """Clean unnecessary spaces and characters."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_heading(text, headings):
    text = text.strip()

    if not text:
        return False

    return text.lower() in [h.lower() for h in headings]


def is_style_heading(paragraph, doc_config):
    """Detect headings by the document's Heading styles when enabled."""
    if not doc_config.get("use_styles"):
        return False

    style = (paragraph.style.name or "").lower()
    return style.startswith("heading")


def load_document(doc_config):
    document = Document(doc_config["docx"])

    sections = []
    current_section = "Introduction"
    current_text = []

    for paragraph in document.paragraphs:

        text = clean_text(paragraph.text)

        if not text:
            continue

        if is_style_heading(paragraph, doc_config) or is_heading(text, doc_config["headings"]):

            if current_text:
                sections.append({
                    "section": current_section,
                    "content": " ".join(current_text)
                })

            current_section = text
            current_text = []

        else:
            current_text.append(text)

    # Add final section
    if current_text:
        sections.append({
            "section": current_section,
            "content": " ".join(current_text)
        })

    return sections


def create_chunks(sections, doc_config):
    chunks = []
    prefix = doc_config["prefix"]
    site = doc_config["site"]
    source = doc_config["source"]

    for index, section in enumerate(sections, start=1):

        content = section["content"]

        # Keep the content together if it is reasonably sized.
        max_length = 1800

        if len(content) <= max_length:

            chunks.append({
                "id": f"{prefix}-{index:03d}",
                "site": site,
                "section": section["section"],
                "content": content,
                "source": source
            })

        else:

            # Split long sections into smaller pieces.
            words = content.split()
            current_chunk = []
            current_length = 0
            part = 1

            for word in words:

                if current_length + len(word) + 1 > max_length:

                    chunks.append({
                        "id": f"{prefix}-{index:03d}-{part:02d}",
                        "site": site,
                        "section": section["section"],
                        "content": " ".join(current_chunk),
                        "source": source
                    })

                    current_chunk = []
                    current_length = 0
                    part += 1

                current_chunk.append(word)
                current_length += len(word) + 1

            if current_chunk:

                chunks.append({
                    "id": f"{prefix}-{index:03d}-{part:02d}",
                    "site": site,
                    "section": section["section"],
                    "content": " ".join(current_chunk),
                    "source": source
                })

    return chunks


def main(selected_keys=None):

    os.makedirs("data", exist_ok=True)

    all_chunks = []

    for doc_config in DOCUMENTS:

        if selected_keys and doc_config["key"] not in selected_keys:
            continue

        print(f"Reading {doc_config['docx']}...")

        sections = load_document(doc_config)

        print(f"Sections found: {len(sections)}")

        chunks = create_chunks(sections, doc_config)

        print(f"Chunks created for {doc_config['site']}: {len(chunks)}")

        all_chunks.extend(chunks)

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_chunks,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"Total chunks: {len(all_chunks)}")
    print(f"Dataset saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()