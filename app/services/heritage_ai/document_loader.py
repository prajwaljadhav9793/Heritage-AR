from docx import Document


def load_docx(file_path):
    """
    Extract text from a Word document.
    Returns a list of non-empty paragraphs.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return paragraphs


if __name__ == "__main__":

    file_path = "data/documents/RAIGAD FORT.docx"

    paragraphs = load_docx(file_path)

    print(f"Total paragraphs extracted: {len(paragraphs)}")

    for i, paragraph in enumerate(paragraphs[:10], start=1):
        print(f"\n{i}. {paragraph}")