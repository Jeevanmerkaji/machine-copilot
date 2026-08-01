import json

from app.ingestion.loaders.json_loader import load_json_records
from app.ingestion.loaders.text import load_markdown_or_text


def test_load_markdown_or_text_tags_manual_type(tmp_path):
    path = tmp_path / "apex3200_manual.md"
    path.write_text("## Section\nBody text.", encoding="utf-8")
    docs = list(load_markdown_or_text(path))
    assert len(docs) == 1
    assert docs[0]["doc_type"] == "manual"
    assert docs[0]["source"] == "apex3200_manual.md"
    assert docs[0]["doc_id"] == "apex3200_manual"


def test_load_markdown_or_text_tags_non_manual_as_bulletin(tmp_path):
    path = tmp_path / "SB-2024-011.md"
    path.write_text("Bulletin body.", encoding="utf-8")
    docs = list(load_markdown_or_text(path))
    assert docs[0]["doc_type"] == "bulletin"


def test_load_json_records_builds_one_doc_per_alarm(tmp_path):
    path = tmp_path / "alarms.json"
    records = [
        {
            "code": "ALM-4021",
            "title": "Spindle Overload",
            "severity": "high",
            "description": "desc",
            "recommended_action": "action",
            "source": "apex3200_alarms.json",
        },
        {
            "code": "ALM-4022",
            "title": "Spindle Overtemp",
            "severity": "high",
            "description": "desc2",
            "recommended_action": "action2",
        },
    ]
    path.write_text(json.dumps(records), encoding="utf-8")
    docs = list(load_json_records(path))
    assert len(docs) == 2
    assert docs[0]["doc_id"] == "alarms::ALM-4021"
    assert "ALM-4021" in docs[0]["text"]
    assert docs[0]["doc_type"] == "alarm_code"
    # falls back to the filename when a record has no explicit "source" key
    assert docs[1]["source"] == "alarms.json"
