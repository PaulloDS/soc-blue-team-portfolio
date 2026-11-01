import json, pathlib
RULES = [json.loads(l) for l in pathlib.Path(__file__).parent.parent.joinpath(
    "detections/rules/bruteforce_rules.ndjson").read_text().splitlines()]
REQUIRED = {"rule_id", "name", "description", "type", "query", "language", "index", "interval",
            "from", "risk_score", "severity", "threat", "enabled"}


def test_four_rules_with_unique_ids():
    assert len(RULES) == 4 and len({r["rule_id"] for r in RULES}) == 4


def test_required_fields_and_mitre_mapping():
    for r in RULES:
        assert REQUIRED <= set(r), r["rule_id"]
        assert r["threat"][0]["framework"] == "MITRE ATT&CK"
        assert r["threat"][0]["technique"][0]["id"].startswith("T1")


def test_threshold_rules_have_thresholds():
    for r in RULES:
        if r["type"] == "threshold":
            assert r["threshold"]["value"] >= 5 and r["threshold"]["field"]


def test_tuned_vs_untuned():
    by = {r["rule_id"]: r for r in RULES}
    assert by["lab-bf-threshold-v2-tuned"]["enabled"] is True
    assert by["lab-bf-threshold-v1-untuned"]["enabled"] is False
    assert "svc_backup" in by["lab-bf-threshold-v2-tuned"]["query"]
    assert "svc_backup" not in by["lab-bf-threshold-v1-untuned"]["query"]


def test_spray_uses_cardinality_and_eql_is_sequence():
    by = {r["rule_id"]: r for r in RULES}
    assert by["lab-spray-threshold-v1"]["threshold"]["cardinality"][0]["field"] == "user.name"
    assert by["lab-bf-sequence-v1"]["query"].lstrip().startswith("sequence by source.ip, user.name")


def test_ndjson_matches_builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location("b", pathlib.Path(__file__).parent.parent / "detections/build_rules.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    assert [r["rule_id"] for r in m.RULES] == [r["rule_id"] for r in RULES]
