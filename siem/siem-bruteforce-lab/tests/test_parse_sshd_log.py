from scripts.attack.parse_sshd_log import parse_lines
from detections import detector as d

SAMPLE = [
    "2026-10-28T15:10:01.100000000Z attack-target sshd[61]: Failed password for invalid user administrator from 172.20.0.3 port 51000 ssh2",
    "2026-10-28T15:10:02.200000000Z attack-target sshd[61]: Failed password for invalid user administrator from 172.20.0.3 port 51001 ssh2",
    "2026-10-28T15:10:03.300000000Z attack-target sshd[61]: Failed password for invalid user administrator from 172.20.0.3 port 51002 ssh2",
    "2026-10-28T15:10:04.400000000Z attack-target sshd[61]: Failed password for invalid user administrator from 172.20.0.3 port 51003 ssh2",
    "2026-10-28T15:10:05.500000000Z attack-target sshd[61]: Failed password for invalid user administrator from 172.20.0.3 port 51004 ssh2",
    "2026-10-28T15:10:06.600000000Z attack-target sshd[61]: Accepted password for labuser from 172.20.0.3 port 51005 ssh2",
    "2026-10-28T15:10:07.000000000Z attack-target sshd[61]: Server listening on 0.0.0.0 port 22.",  # linha irrelevante
]


def test_parses_only_auth_lines():
    events = parse_lines(SAMPLE)
    assert len(events) == 6  # 5 falhas + 1 sucesso; a linha "Server listening" é ignorada


def test_fields_match_lab_schema():
    for e in parse_lines(SAMPLE):
        assert e["event"]["category"] == ["authentication"]
        assert e["event"]["outcome"] in ("success", "failure")
        assert e["source"]["ip"] == "172.20.0.3"
        assert e["lab"]["scenario"] == "real_attack"
        assert e["@timestamp"].endswith("Z")


def test_invalid_user_prefix_is_stripped():
    events = parse_lines(SAMPLE)
    assert events[0]["user"]["name"] == "administrator"  # "invalid user" não vira parte do nome


def test_accepted_login_parsed_as_success():
    events = parse_lines(SAMPLE)
    assert events[-1]["event"]["outcome"] == "success"
    assert events[-1]["user"]["name"] == "labuser"


def test_detector_flags_real_attack_log():
    events = parse_lines(SAMPLE)
    thr = d.threshold_alerts(events)
    assert len(thr) == 1 and thr[0]["source.ip"] == "172.20.0.3" and thr[0]["user.name"] == "administrator"


def test_ignores_lines_without_valid_timestamp_prefix():
    bad = ["not-a-timestamp Failed password for root from 1.2.3.4 port 22 ssh2"] + SAMPLE
    assert len(parse_lines(bad)) == 6


def test_empty_input_returns_empty_list():
    assert parse_lines([]) == []
