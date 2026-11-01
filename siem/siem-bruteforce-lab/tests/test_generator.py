import json
from datetime import datetime, timezone
from generator.generate_events import generate

NOW = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)


def test_deterministic_with_same_seed():
    assert generate(7, NOW) == generate(7, NOW)


def test_different_seed_changes_output():
    assert generate(1, NOW) != generate(2, NOW)


def test_schema_fields_present():
    for e in generate(42, NOW):
        assert e["@timestamp"].endswith("Z")
        assert e["event"]["category"] == ["authentication"]
        assert e["event"]["outcome"] in ("success", "failure")
        assert e["event"]["code"] == ("4624" if e["event"]["outcome"] == "success" else "4625")
        assert e["user"]["name"] and e["source"]["ip"] and e["lab"]["scenario"]
        json.dumps(e)


def test_scenarios_and_counts():
    ev = generate(42, NOW)
    sc = {}
    for e in ev:
        sc.setdefault(e["lab"]["scenario"], []).append(e)
    assert set(sc) == {"baseline", "false_positive", "bruteforce", "spray"}
    assert len(sc["false_positive"]) == 30
    assert sum(e["event"]["outcome"] == "failure" for e in sc["bruteforce"]) == 40
    assert sum(e["event"]["outcome"] == "success" for e in sc["bruteforce"]) == 1
    assert len(sc["spray"]) == 24


def test_sorted_and_not_in_future():
    ts = [e["@timestamp"] for e in generate(42, NOW)]
    assert ts == sorted(ts)
    assert ts[-1] <= "2026-10-28T12:00:00.000Z"
