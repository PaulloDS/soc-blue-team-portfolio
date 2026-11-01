from datetime import datetime, timedelta, timezone
from detections import detector as d
from generator.generate_events import generate, ATTACKER_BF, ATTACKER_SPRAY, SERVICE_IP

NOW = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)


def ev(offset_s, user="u1", ip="1.1.1.1", ok=False):
    t = NOW + timedelta(seconds=offset_s)
    return {"@timestamp": t.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "event": {"category": ["authentication"], "outcome": "success" if ok else "failure"},
            "user": {"name": user}, "source": {"ip": ip}}


# ---- cenário completo ----
def test_threshold_finds_attack_and_untuned_false_positive():
    keys = {(a["source.ip"], a["user.name"]) for a in d.threshold_alerts(generate(42, NOW))}
    assert keys == {(ATTACKER_BF, "administrator"), (SERVICE_IP, "svc_backup")}


def test_tuning_removes_false_positive_but_keeps_attack():
    keys = {(a["source.ip"], a["user.name"]) for a in d.threshold_alerts(generate(42, NOW), allowlist=d.TUNED_ALLOWLIST)}
    assert keys == {(ATTACKER_BF, "administrator")}


def test_spray_detects_only_the_sprayer():
    assert [a["source.ip"] for a in d.spray_alerts(generate(42, NOW))] == [ATTACKER_SPRAY]


def test_sequence_detects_compromise():
    a = d.sequence_alerts(generate(42, NOW))
    assert [(x["source.ip"], x["user.name"]) for x in a] == [(ATTACKER_BF, "administrator")]
    assert a[0]["failures_before_success"] == 40


def test_baseline_alone_is_quiet():
    base = [e for e in generate(42, NOW) if e["lab"]["scenario"] == "baseline"]
    assert d.threshold_alerts(base) == d.spray_alerts(base) == d.sequence_alerts(base) == []


def test_many_seeds_stable():
    for seed in range(20):
        e = generate(seed, NOW)
        assert {(a["source.ip"], a["user.name"]) for a in d.threshold_alerts(e, allowlist=d.TUNED_ALLOWLIST)} == {(ATTACKER_BF, "administrator")}
        assert [a["source.ip"] for a in d.spray_alerts(e)] == [ATTACKER_SPRAY]


# ---- limites (boundary tests) ----
def test_threshold_boundary_4_vs_5():
    assert d.threshold_alerts([ev(i * 10) for i in range(4)]) == []
    assert len(d.threshold_alerts([ev(i * 10) for i in range(5)])) == 1


def test_threshold_respects_window():
    spread = [ev(i * 120) for i in range(5)]       # 5 falhas em 8 min (> janela de 5)
    assert d.threshold_alerts(spread) == []
    assert len(d.threshold_alerts(spread, window=timedelta(minutes=10))) == 1


def test_threshold_groups_by_ip_and_user():
    mixed = [ev(i, ip=f"1.1.1.{i}") for i in range(5)] + [ev(i, user=f"u{i}") for i in range(5)]
    assert d.threshold_alerts(mixed) == []


def test_success_events_do_not_count_as_failures():
    assert d.threshold_alerts([ev(i, ok=True) for i in range(10)]) == []


def test_sequence_needs_enough_failures():
    assert d.sequence_alerts([ev(i) for i in range(4)] + [ev(10, ok=True)]) == []
    assert len(d.sequence_alerts([ev(i) for i in range(5)] + [ev(10, ok=True)])) == 1


def test_sequence_success_without_failures_is_ignored():
    assert d.sequence_alerts([ev(0, ok=True)]) == []


def test_sequence_success_before_failures_is_ignored():
    assert d.sequence_alerts([ev(0, ok=True)] + [ev(10 + i) for i in range(6)]) == []


def test_sequence_other_ip_success_does_not_match():
    e = [ev(i) for i in range(6)] + [ev(20, ip="9.9.9.9", ok=True)]
    assert d.sequence_alerts(e) == []


def test_sequence_respects_maxspan():
    e = [ev(i) for i in range(6)] + [ev(3600, ok=True)]
    assert d.sequence_alerts(e) == []


def test_spray_needs_distinct_users():
    same_user = [ev(i, user="admin", ip="2.2.2.2") for i in range(20)]
    assert d.spray_alerts(same_user) == []
    many = [ev(i, user=f"u{i % 6}", ip="2.2.2.2") for i in range(12)]
    assert len(d.spray_alerts(many)) == 1
