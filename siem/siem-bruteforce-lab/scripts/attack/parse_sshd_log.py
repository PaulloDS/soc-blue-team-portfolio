#!/usr/bin/env python3
"""Converte 'docker compose logs attack-target --timestamps' em eventos ECS reais.

Reconhece as linhas do OpenSSH em modo foreground:
  Failed password for [invalid user] <user> from <ip> port <port> ssh2
  Accepted password for <user> from <ip> port <port> ssh2
"""
import argparse, json, re

FAIL_RE = re.compile(r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+) port (?P<port>\d+)")
OK_RE = re.compile(r"Accepted password for (?P<user>\S+) from (?P<ip>\S+) port (?P<port>\d+)")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T")


def parse_lines(lines, host="attack-target"):
    events = []
    for raw in lines:
        raw = raw.strip()
        if not raw or " " not in raw:
            continue
        ts, rest = raw.split(" ", 1)
        if not TS_RE.match(ts):
            continue
        m = FAIL_RE.search(rest)
        ok = False
        if not m:
            m = OK_RE.search(rest)
            ok = bool(m)
        if not m:
            continue
        events.append({
            "@timestamp": ts if ts.endswith("Z") else ts + "Z",
            "event": {"category": ["authentication"], "outcome": "success" if ok else "failure",
                      "action": "ssh_login" if ok else "ssh_login_failed"},
            "user": {"name": m.group("user")},
            "source": {"ip": m.group("ip"), "port": int(m.group("port"))},
            "host": {"name": host},
            "observer": {"product": "OpenSSH"},
            "lab": {"scenario": "real_attack"},
        })
    return events


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lines = open(a.inp, encoding="utf-8", errors="replace").read().splitlines()
    events = parse_lines(lines)
    with open(a.out, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"{len(events)} eventos reais extraídos para {a.out}")
    if not events:
        print("Nenhum evento reconhecido. Confira se o docker logs usou --timestamps "
              "e se o container 'attack-target' chegou a rodar.")


if __name__ == "__main__":
    main()
