from app.services.retrieval.qdrant_service import Chunk
from app.services.retrieval.ranking_service import rerank


def _chunk(chunk_id, text, doc_type="manual"):
    return Chunk(chunk_id=chunk_id, source="src.md", doc_type=doc_type, text=text)


def test_exact_code_match_is_boosted_to_top():
    results = [
        (_chunk("c1", "Some fuzzy prose that mentions overload issues generally."), 0.9),
        (_chunk("c2", "Alarm ALM-4021 — Spindle Overload details.", doc_type="alarm_code"), 0.2),
    ]
    reranked = rerank("What should I check for alarm ALM-4021?", results, top_n=2)
    assert reranked[0][0].chunk_id == "c2"


def test_no_code_in_query_leaves_order_by_score():
    results = [
        (_chunk("c1", "high score chunk"), 0.9),
        (_chunk("c2", "low score chunk"), 0.2),
    ]
    reranked = rerank("What spindle speed should I use?", results, top_n=2)
    assert [c.chunk_id for c, _ in reranked] == ["c1", "c2"]


def test_top_n_limits_results():
    results = [(_chunk(f"c{i}", "text"), 1.0 - i * 0.1) for i in range(5)]
    reranked = rerank("generic question", results, top_n=3)
    assert len(reranked) == 3
