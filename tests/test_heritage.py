from app.services.heritage_ai.rag_service import ask_heritage_ai


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
