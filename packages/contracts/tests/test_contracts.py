from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from fcs_contracts import (
    EventBatch,
    Heartbeat,
    ViolationEvent,
    ViolationType,
)

NOW = datetime(2026, 11, 15, 10, 0, tzinfo=UTC)


def event(**overrides):  # type: ignore[no-untyped-def]
    data = {
        "eventId": str(uuid4()),
        "cameraId": "cam-01",
        "violationType": "missing_ppe",
        "missingPpe": ["helmet"],
        "startedAt": NOW.isoformat(),
        "confidence": 0.9,
        "severity": "high",
        "source": "simulation",
    }
    data.update(overrides)
    return data


def test_event_round_trips_as_camel_case_json() -> None:
    parsed = ViolationEvent.model_validate(event(trackId="t-1"))
    dumped = parsed.model_dump(mode="json")
    assert dumped["cameraId"] == "cam-01"
    assert dumped["missingPpe"] == ["helmet"]
    assert dumped["trackId"] == "t-1"
    assert ViolationEvent.model_validate(dumped) == parsed


@pytest.mark.parametrize(
    "overrides",
    [
        {"missingPpe": []},  # missing_ppe türü KKD listesi ister
        {"violationType": "restricted_area"},  # restricted_area KKD listesi almaz
        {"missingPpe": ["helmet", "helmet"]},  # tekrar
        {"missingPpe": ["cape"]},  # bilinmeyen KKD
        {"startedAt": "2026-11-15T10:00:00"},  # zaman dilimi yok
        {"endedAt": (NOW - timedelta(seconds=1)).isoformat()},  # bitiş < başlangıç
        {"confidence": 1.5},
        {"source": "model"},  # model bilgisi gerekli
        {"cameraId": "cam 01; DROP"},  # geçersiz karakter
        {"unknownField": 1},  # bilinmeyen alan
    ],
)
def test_event_validation_rejects_invalid_input(overrides: dict) -> None:
    with pytest.raises(ValidationError):
        ViolationEvent.model_validate(event(**overrides))


def test_non_ppe_violation_types_are_valid_without_ppe_list() -> None:
    for vtype in (ViolationType.RESTRICTED_AREA, ViolationType.MISSING_HARNESS):
        parsed = ViolationEvent.model_validate(event(violationType=vtype, missingPpe=[]))
        assert parsed.missing_ppe == []


def test_model_source_requires_model_ref() -> None:
    parsed = ViolationEvent.model_validate(
        event(source="model", model={"id": "ppe-detector", "version": "1.0.0"})
    )
    assert parsed.model is not None


def test_batch_limits_and_duplicate_ids() -> None:
    same_id = str(uuid4())
    with pytest.raises(ValidationError):
        EventBatch.model_validate({"events": [event(eventId=same_id), event(eventId=same_id)]})
    with pytest.raises(ValidationError):
        EventBatch.model_validate({"events": []})
    with pytest.raises(ValidationError):
        EventBatch.model_validate({"events": [event() for _ in range(101)]})


def test_heartbeat() -> None:
    hb = Heartbeat.model_validate(
        {
            "sentAt": NOW.isoformat(),
            "softwareVersion": "0.1.0",
            "simulated": True,
            "cameras": [{"cameraId": "cam-01", "status": "online", "fps": 5}],
        }
    )
    assert hb.cameras[0].status == "online"
    with pytest.raises(ValidationError):
        Heartbeat.model_validate({"sentAt": NOW.isoformat(), "softwareVersion": "x"})
