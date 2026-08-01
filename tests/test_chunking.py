from app.ingestion.chunking.splitter import split_document


def test_alarm_code_doc_passes_through_as_single_chunk():
    doc = {
        "doc_id": "alarms::ALM-4021",
        "source": "apex3200_alarms.json",
        "doc_type": "alarm_code",
        "text": "Alarm ALM-4021 — Spindle Overload",
    }
    chunks = list(split_document(doc))
    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "alarms::ALM-4021"
    assert chunks[0]["text"] == doc["text"]


def test_manual_doc_splits_on_markdown_headers():
    text = (
        "# Intro\n"
        "Some preamble text.\n"
        "## 3.2 Spindle Alarm Codes\n"
        "Section A content.\n"
        "### 3.2.1 Detail\n"
        "Section B content.\n"
    )
    doc = {"doc_id": "manual", "source": "manual.md", "doc_type": "manual", "text": text}
    chunks = list(split_document(doc))
    assert len(chunks) == 2
    assert "Section A content" in chunks[0]["text"]
    assert "Section B content" in chunks[1]["text"]
    assert chunks[0]["chunk_id"] == "manual::0"


def test_doc_without_headers_falls_back_to_fixed_size_chunks():
    doc = {"doc_id": "flat", "source": "flat.md", "doc_type": "bulletin", "text": "x" * 2500}
    chunks = list(split_document(doc, max_chars=900))
    assert len(chunks) == 3
    assert all(len(c["text"]) <= 900 for c in chunks)


def test_oversized_section_is_further_split():
    text = "## Big Section\n" + ("y" * 2000)
    doc = {"doc_id": "big", "source": "big.md", "doc_type": "manual", "text": text}
    chunks = list(split_document(doc, max_chars=900))
    assert len(chunks) > 1
    assert all(c["chunk_id"].startswith("big::0.") for c in chunks)
