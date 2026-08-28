from rag_assistant.pipeline import DocumentStore, chunk_text


def test_chunking_preserves_overlap():
    chunks = chunk_text(" ".join(f"word{i}" for i in range(10)), chunk_size=5, overlap=2)
    assert chunks == [
        "word0 word1 word2 word3 word4",
        "word3 word4 word5 word6 word7",
        "word6 word7 word8 word9",
    ]


def test_search_ranks_relevant_passage():
    store = DocumentStore(chunk_size=50, overlap=5)
    store.add_text("The refund window is thirty days from purchase.", "policy.pdf", 1)
    store.add_text("Support is available by email during business hours.", "contact.pdf", 2)
    results = store.search("How long is the refund window?", top_k=1)
    assert results[0].source == "policy.pdf"
    assert results[0].score > 0


def test_empty_or_unknown_question_has_no_answer_context():
    store = DocumentStore()
    store.add_text("The office is in Berlin.", "about.pdf", 1)
    assert store.search("") == []
    assert store.search("What is the launch date?", top_k=2)[0].score == 0.0
