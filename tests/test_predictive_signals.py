from app.telemetry.plc_listener import TelemetryEvent
from app.telemetry.predictive_signals import analyze_window


def _event(code=None, event_type="sensor", bearing_temp_c=50.0, severity=None):
    return TelemetryEvent(
        machine_id="M-1",
        timestamp="2026-01-01T00:00:00Z",
        event_type=event_type,
        code=code,
        severity=severity,
        spindle_load_pct=70.0,
        bearing_temp_c=bearing_temp_c,
    )


def test_flags_ball_screw_wear_risk_above_threshold():
    events = [_event(code="ALM-1104", event_type="alarm") for _ in range(2)] + [
        _event(code="ALM-1105", event_type="alarm") for _ in range(2)
    ]
    result = analyze_window(events)
    signals = [f["signal"] for f in result["flags"]]
    assert "ball_screw_wear_risk" in signals
    assert result["alarm_counts"]["ALM-1104"] == 2


def test_no_flag_below_threshold():
    events = [_event(code="ALM-1104", event_type="alarm")]
    result = analyze_window(events)
    assert result["flags"] == []


def test_flags_elevated_bearing_temperature():
    events = [_event(bearing_temp_c=82.0) for _ in range(5)]
    result = analyze_window(events)
    signals = [f["signal"] for f in result["flags"]]
    assert "elevated_bearing_temperature" in signals


def test_empty_window_has_no_flags_and_no_zero_division():
    result = analyze_window([])
    assert result == {"window_size": 0, "alarm_counts": {}, "flags": []}
