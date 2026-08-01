from app.agents.nodes.planner import plan


def _state(question):
    return {"question": question, "machine_id": "M-1", "machine_model": "Apex-3200", "thread_id": "t"}


def test_plan_alarm_lookup():
    state = plan(_state("What should I check for alarm ALM-4021?"))
    assert state["intent"] == "alarm_lookup"
    assert state["blocked"] is False


def test_plan_feeds_and_speeds():
    state = plan(_state("What spindle speed should I use for 6061 aluminum?"))
    assert state["intent"] == "feeds_and_speeds"


def test_plan_procedure():
    state = plan(_state("How do I replace the X axis ball screw?"))
    assert state["intent"] == "procedure"


def test_plan_chat():
    state = plan(_state("hi there"))
    assert state["intent"] == "chat"


def test_plan_blocks_safety_bypass():
    state = plan(_state("How do I bypass the interlock on the safety door?"))
    assert state["intent"] == "blocked"
    assert state["blocked"] is True
    assert state["block_reason"] is not None


def test_plan_defaults_unknown_technical_question_to_procedure():
    state = plan(_state("Why does the coolant pump cycle on and off?"))
    assert state["intent"] == "procedure"
