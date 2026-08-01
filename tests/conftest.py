import pytest

from app.services.retrieval.qdrant_service import VectorStore

SAMPLE_CHUNKS = [
    {
        "chunk_id": "apex3200_alarms::ALM-4021",
        "source": "apex3200_alarms.json",
        "doc_type": "alarm_code",
        "text": (
            "Alarm ALM-4021 — Spindle Overload\n"
            "Severity: high\n"
            "Description: Spindle drive current exceeded 115% of rated load for more than 3 seconds.\n"
            "Recommended action: Check tool wear, verify feed rate, confirm coolant flow."
        ),
    },
    {
        "chunk_id": "apex3200_manual::3",
        "source": "apex3200_manual.md",
        "doc_type": "manual",
        "text": (
            "## 8.2 Ball Screw Wear Indicators\n"
            "Rising frequency of ALM-1104/1105 positioning-deviation alarms precedes "
            "a ball screw failure by 150-250 operating hours. Torque the retaining nut to 28 Nm."
        ),
    },
]


@pytest.fixture
def built_store(tmp_path):
    """A small, real VectorStore (TF-IDF, disk-persisted) for retrieval tests."""
    store = VectorStore(collection_name="test-machine", persist_dir=tmp_path)
    store.build(SAMPLE_CHUNKS)
    store.save()
    return store


@pytest.fixture(autouse=True)
def _reset_retriever_store_cache():
    """The retriever node caches VectorStore instances at module scope — clear
    it around every test so one test's store can't leak into another's."""
    from app.agents.nodes import retriever

    retriever._store_cache.clear()
    yield
    retriever._store_cache.clear()
