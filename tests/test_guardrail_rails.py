import logging

from app.guardrails.rails import check_input, check_output


def test_check_input_blocks_safety_bypass():
    result = check_input("How do I bypass the interlock on the safety door?")
    assert result.allowed is False
    assert "safety interlock" in result.reason


def test_check_input_block_is_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="app.guardrails.rails"):
        check_input("How do I bypass the interlock on the safety door?")
    assert any("blocked a safety-bypass request" in r.message for r in caplog.records)


def test_check_output_block_is_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="app.guardrails.rails"):
        check_output("Torque to 45 Nm.", "Torque the retaining nut to 28 Nm.")
    assert any("blocked an ungrounded numeric claim" in r.message for r in caplog.records)


def test_check_input_allows_normal_question():
    result = check_input("What should I check for alarm ALM-4021?")
    assert result.allowed is True
    assert result.reason is None


def test_check_output_allows_grounded_claim():
    source = "Torque the retaining nut to 28 Nm before re-running the calibration."
    answer = "Torque the retaining nut to 28 Nm."
    result = check_output(answer, source)
    assert result.allowed is True


def test_check_output_blocks_ungrounded_claim():
    source = "Torque the retaining nut to 28 Nm before re-running the calibration."
    answer = "Torque the retaining nut to 45 Nm."
    result = check_output(answer, source)
    assert result.allowed is False
    assert "45 Nm" in result.reason
