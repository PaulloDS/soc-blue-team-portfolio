from scripts.attack.multi_attack import build_campaign, plan_bruteforce, plan_spray, plan_noise

CFG = {"profiles": [
    {"type": "bruteforce", "name": "bf", "source_ip": "10.0.0.1", "user": "administrator",
     "wordlist": ["a", "b", "c"], "correct": "d"},
    {"type": "spray", "name": "sp", "source_ip": "10.0.0.2", "users": ["u1", "u2", "u3"], "passwords_per_user": 2},
    {"type": "noise", "name": "no", "source_ip": "10.0.0.3", "user": "svc_backup", "count": 5, "interval": 30},
]}


def test_bruteforce_plan_includes_correct_password_last():
    attempts = plan_bruteforce("10.0.0.1", "administrator", ["a", "b", "c"], correct="d")
    assert len(attempts) == 4
    assert attempts[-1]["password"] == "d"
    assert all(a["source_ip"] == "10.0.0.1" and a["user"] == "administrator" for a in attempts)


def test_bruteforce_without_correct_password():
    attempts = plan_bruteforce("10.0.0.1", "administrator", ["a", "b"])
    assert len(attempts) == 2


def test_spray_plan_covers_every_user_each_round():
    attempts = plan_spray("10.0.0.2", ["u1", "u2", "u3"], passwords_per_user=2)
    assert len(attempts) == 6
    assert {a["user"] for a in attempts} == {"u1", "u2", "u3"}
    assert all(a["source_ip"] == "10.0.0.2" for a in attempts)


def test_noise_plan_is_steady():
    attempts = plan_noise("10.0.0.3", "svc_backup", count=5, interval=30)
    assert len(attempts) == 5
    assert all(a["delay"] == 30 and a["user"] == "svc_backup" for a in attempts)


def test_build_campaign_three_profiles_distinct_ips():
    campaign = build_campaign(CFG)
    assert [name for name, _ in campaign] == ["bf", "sp", "no"]
    ips = {attempts[0]["source_ip"] for _, attempts in campaign}
    assert ips == {"10.0.0.1", "10.0.0.2", "10.0.0.3"}


def test_build_campaign_total_attempts():
    campaign = build_campaign(CFG)
    total = sum(len(a) for _, a in campaign)
    assert total == 4 + 6 + 5


def test_unknown_profile_type_raises():
    import pytest
    with pytest.raises(ValueError):
        build_campaign({"profiles": [{"type": "nope"}]})


def test_example_config_file_is_valid():
    import json, pathlib
    cfg = json.loads(pathlib.Path(__file__).parent.parent.joinpath(
        "scripts/attack/campaign.example.json").read_text())
    campaign = build_campaign(cfg)
    assert len(campaign) == 3
    assert len({attempts[0]["source_ip"] for _, attempts in campaign}) == 3
