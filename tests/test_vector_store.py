import pytest

from app.services.retrieval.qdrant_service import VectorStore

SAMPLE_CHUNKS = [
    {
        "chunk_id": "a1",
        "source": "alarms.json",
        "doc_type": "alarm_code",
        "text": "Alarm ALM-4021 Spindle Overload check tool wear.",
    },
    {
        "chunk_id": "m1",
        "source": "manual.md",
        "doc_type": "manual",
        "text": "Feeds and speeds guidance for aluminum machining.",
    },
]


def test_build_and_search_returns_relevant_chunk(tmp_path):
    store = VectorStore(collection_name="test", persist_dir=tmp_path)
    store.build(SAMPLE_CHUNKS)
    results = store.search("spindle overload alarm", top_k=2)
    assert results[0][0].chunk_id == "a1"


def test_search_before_build_raises(tmp_path):
    store = VectorStore(collection_name="empty", persist_dir=tmp_path)
    with pytest.raises(RuntimeError):
        store.search("anything")


def test_save_and_load_round_trip(tmp_path):
    store = VectorStore(collection_name="roundtrip", persist_dir=tmp_path)
    store.build(SAMPLE_CHUNKS)
    store.save()

    reloaded = VectorStore(collection_name="roundtrip", persist_dir=tmp_path)
    assert reloaded.load() is True
    results = reloaded.search("aluminum feeds and speeds", top_k=1)
    assert results[0][0].chunk_id == "m1"


def test_load_returns_false_when_no_file_exists(tmp_path):
    store = VectorStore(collection_name="missing", persist_dir=tmp_path)
    assert store.load() is False
