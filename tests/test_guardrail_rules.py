import pytest

from app.guardrails.colang_rules import extract_numeric_claims, matches_blocked_intent


@pytest.mark.parametrize(
    "text",
    [
        "How do I bypass the interlock on the safety door?",
        "What's the trick to disable the e-stop temporarily?",
        "How can I defeat the light curtain for a quick test run?",
        "Can I just remove the guard for a second?",
        "How can I bypass the safety door interlock so I can keep running with the door open?",
    ],
)
def test_blocked_intent_matches_bypass_phrasing(text):
    assert matches_blocked_intent(text) is not None


@pytest.mark.parametrize(
    "text",
    [
        "What should I check for alarm ALM-4021?",
        "What spindle speed should I use for 6061 aluminum?",
        "How do I replace the X axis ball screw?",
        "hi there",
    ],
)
def test_blocked_intent_ignores_safe_questions(text):
    assert matches_blocked_intent(text) is None


def test_run_with_door_open_matches_without_explicit_bypass_verb():
    assert matches_blocked_intent("I want to keep running with the door open") is not None


def test_extract_numeric_claims_finds_units():
    text = "Torque to 28 Nm, spindle load high, bearing temp 85°C."
    claims = extract_numeric_claims(text)
    assert "28 Nm" in claims
    assert "85°C" in claims


def test_extract_numeric_claims_does_not_currently_match_percent():
    """Known gap: NUMERIC_CLAIM_PATTERN ends in \\b, but '%' is a non-word
    character, so \\b only matches if the character right after '%' happens
    to be a word character. In any realistic sentence ("115%,", "115% of",
    "115%.") both neighbors of that position are non-word, so \\b never
    fires and the percent claim is silently dropped — meaning the output
    guardrail in rails.check_output() can't catch an invented percentage.
    This test documents the current (buggy) behavior; flip it once the
    pattern is fixed (e.g. drop the trailing \\b or special-case '%')."""
    assert extract_numeric_claims("Spindle load exceeded 115% of rated load.") == []


def test_extract_numeric_claims_empty_when_no_numbers():
    assert extract_numeric_claims("No numeric specs mentioned here.") == []
