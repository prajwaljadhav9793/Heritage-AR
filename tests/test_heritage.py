from app.services.heritage_ai.rag_service import ask_heritage_ai, retrieve_context


def test_nalanda_foundation_question_prioritizes_foundation_section():
    results = retrieve_context("Who founded Nalanda Mahavihara?")

    assert results
    assert results[0]["section"] in {"Gupta Period", "History"}
    assert "Kumaragupta" in results[0]["content"]


def test_nalanda_famous_question_prioritizes_faq_answer():
    results = retrieve_context("Why is Nalanda famous?")

    assert results
    assert results[0]["section"] == "2. Why is Nalanda famous?"


def test_konark_builder_question_prioritizes_direct_archive_context():
    results = retrieve_context("Who built the Konark Sun Temple?")

    assert results
    assert "Who built the Konark Sun Temple" in results[0]["content"]


def test_martand_question_does_not_mix_konark_context():
    results = retrieve_context("Who built Martand Sun Temple?")

    assert results
    assert all(result["source"] == "Martand sun temple.docx" for result in results)


def test_heritage_ai_falls_back_without_ollama(monkeypatch):
    sample_context = [{
        "section": "Hampi overview",
        "source": "heritage_sites.json",
        "content": "Hampi is a UNESCO World Heritage Site in Karnataka and was the capital of Vijayanagara."
    }]

    monkeypatch.setattr(
        "app.services.heritage_ai.rag_service.retrieve_context",
        lambda question, n_results=3: sample_context,
    )
    monkeypatch.setattr(
        "app.services.heritage_ai.rag_service.is_relevant",
        lambda question, retrieved: True,
    )
    monkeypatch.setattr(
        "app.services.heritage_ai.rag_service.ollama_client.chat",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("connection refused")),
    )

    result = ask_heritage_ai("What is Hampi?")

    assert result["sources"]
    assert "Hampi" in result["answer"]
    assert "temporarily unavailable" not in result["answer"].lower()
