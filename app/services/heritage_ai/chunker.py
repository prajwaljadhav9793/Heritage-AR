from docx import Document
import json
import os
import re


DOCX_PATH = "data/documents/RAIGAD FORT.docx"
OUTPUT_PATH = "data/heritage_chunks.json"


def clean_text(text):
    """Clean unnecessary spaces and characters."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_heading(text):
    """
    Detect headings from the Raigad document.
    """
    text = text.strip()

    if not text:
        return False

    headings = [
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
    ]

    return text.lower() in [h.lower() for h in headings]


def load_document():
    document = Document(DOCX_PATH)

    sections = []
    current_section = "Introduction"
    current_text = []

    for paragraph in document.paragraphs:

        text = clean_text(paragraph.text)

        if not text:
            continue

        if is_heading(text):

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


def create_chunks(sections):
    chunks = []

    for index, section in enumerate(sections, start=1):

        content = section["content"]

        # Keep the content together if it is reasonably sized.
        max_length = 1800

        if len(content) <= max_length:

            chunks.append({
                "id": f"RG-{index:03d}",
                "site": "Raigad Fort",
                "section": section["section"],
                "content": content,
                "source": "RAIGAD FORT.docx"
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
                        "id": f"RG-{index:03d}-{part:02d}",
                        "site": "Raigad Fort",
                        "section": section["section"],
                        "content": " ".join(current_chunk),
                        "source": "RAIGAD FORT.docx"
                    })

                    current_chunk = []
                    current_length = 0
                    part += 1

                current_chunk.append(word)
                current_length += len(word) + 1

            if current_chunk:

                chunks.append({
                    "id": f"RG-{index:03d}-{part:02d}",
                    "site": "Raigad Fort",
                    "section": section["section"],
                    "content": " ".join(current_chunk),
                    "source": "RAIGAD FORT.docx"
                })

    return chunks


def main():

    print("Reading Raigad document...")

    sections = load_document()

    print(f"Sections found: {len(sections)}")

    chunks = create_chunks(sections)

    os.makedirs("data", exist_ok=True)

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"Chunks created: {len(chunks)}")
    print(f"Dataset saved to: {OUTPUT_PATH}")

    print("\nFirst 5 chunks:\n")

    for chunk in chunks[:5]:

        print("=" * 60)
        print("ID:", chunk["id"])
        print("Section:", chunk["section"])
        print("Content:", chunk["content"][:300], "...")


if __name__ == "__main__":
    main()