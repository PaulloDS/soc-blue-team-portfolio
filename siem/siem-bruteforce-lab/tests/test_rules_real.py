import json, pathlib
RULES = [json.loads(l) for l in pathlib.Path(__file__).parent.parent.joinpath(
    "detections/rules/real_lab_rules.ndjson").read_text().splitlines()]


def test_four_rules_pointed_at_real_indices():
    assert len(RULES) == 4
    for r in RULES:
        assert r["index"] == ["filebeat-*", "winlogbeat-*"]
        assert r["rule_id"].startswith("real-")
        assert "LAB -" not in r["name"]


def test_tuned_vs_untuned_preserved():
    by = {r["rule_id"]: r for r in RULES}
    assert by["real-bf-threshold-v2-tuned"]["enabled"] is True
    assert by["real-bf-threshold-v1-untuned"]["enabled"] is False
