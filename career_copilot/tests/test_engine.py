from career_copilot.backend.engine import retrieve_evidence, split_resume


def test_resume_is_split_into_evidence_units():
    assert split_resume("Skills\n- Python\n\nExperience") == ["Skills", "Python", "Experience"]


def test_retrieval_surfaces_matching_resume_evidence():
    evidence = retrieve_evidence(
        "Built Python forecasting models.\nDesigned logos for a local club.",
        "Need Python analytics and forecasting experience.",
        top_k=1,
    )
    assert evidence[0].text == "Built Python forecasting models."
    assert evidence[0].score > 0
