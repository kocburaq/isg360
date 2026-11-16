from datetime import timedelta

import pytest
from fcs_contracts import ViolationEvent, ViolationType

from fcs_vision.simulator.scenario import Scenario
from tests.conftest import CAMERAS, NOW


def run(scenario: Scenario, ticks: int) -> list[ViolationEvent]:
    events = []
    for i in range(ticks):
        events += scenario.tick(CAMERAS, NOW + timedelta(seconds=10 * i))
    return events


def test_same_seed_produces_same_events() -> None:
    a = run(Scenario(seed=7, event_probability=0.5), 30)
    b = run(Scenario(seed=7, event_probability=0.5), 30)
    assert a and [e.model_dump() for e in a] == [e.model_dump() for e in b]
    assert run(Scenario(seed=8, event_probability=0.5), 30) != a


def test_events_respect_contract_and_camera_config() -> None:
    events = run(Scenario(seed=1, event_probability=1.0), 50)
    kinds = {e.violation_type for e in events}
    assert kinds == set(ViolationType)  # tüm türler üretilir
    classes = {c.id: set(c.ppe_classes) for c in CAMERAS}
    for e in events:
        # Sözleşme doğrulamasından geçer (JSON gidiş-dönüş)
        assert ViolationEvent.model_validate_json(e.model_dump_json()) == e
        assert e.source == "simulation"
        if e.violation_type == ViolationType.MISSING_PPE:
            assert set(e.missing_ppe) <= classes[e.camera_id]
        else:
            assert e.missing_ppe == []


def test_ongoing_violations_end_with_same_event_id() -> None:
    scenario = Scenario(seed=3, event_probability=1.0, min_duration_s=5, max_duration_s=5)
    first = scenario.tick(CAMERAS, NOW)
    assert len(first) == 2 and all(e.ended_at is None for e in first)

    later = scenario.tick([], NOW + timedelta(seconds=6))
    assert {e.event_id for e in later} == {e.event_id for e in first}
    assert all(e.ended_at == NOW + timedelta(seconds=5) for e in later)
    assert scenario.ongoing == []


def test_offline_cameras_produce_no_events_and_report_offline() -> None:
    scenario = Scenario(seed=1, event_probability=1.0, offline_cameras=frozenset({"cam-02"}))
    events = scenario.tick(CAMERAS, NOW)
    assert {e.camera_id for e in events} == {"cam-01"}
    beats = {b.camera_id: b for b in scenario.camera_heartbeats(CAMERAS, NOW)}
    assert beats["cam-02"].status == "offline"
    assert beats["cam-01"].status == "online" and beats["cam-01"].last_frame_at == NOW


def test_invalid_probability() -> None:
    with pytest.raises(ValueError):
        Scenario(event_probability=1.5)
