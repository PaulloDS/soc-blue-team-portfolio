#!/usr/bin/env python3
"""Gerador de eventos de autenticação (formato ECS, estilo Windows 4624/4625).

Cenários (campo lab.scenario = gabarito, NÃO usado pelas regras):
  baseline        uso normal + erros de digitação isolados
  false_positive  conta de serviço com credencial antiga (svc_backup)
  bruteforce      ataque contra 'administrator' seguido de login válido
  spray           1 senha testada contra vários usuários
Todos os IPs externos usam faixas de documentação (RFC 5737).
"""
import argparse, json, random
from datetime import datetime, timedelta, timezone

BASE_USERS = ["ana.silva", "bruno.costa", "carla.souza", "diego.lima",
              "elisa.rocha", "fabio.nunes", "gabriela.melo", "henrique.alves"]
SPRAY_USERS = BASE_USERS + ["administrator", "backup.admin", "helpdesk", "svc_sql"]
ATTACKER_BF = "203.0.113.45"
ATTACKER_SPRAY = "198.51.100.77"
SERVICE_IP = "10.0.5.20"


def _ev(ts, user, ip, ok, scenario, host="dc01", logon_type="Network"):
    return {
        "@timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z",
        "event": {
            "category": ["authentication"],
            "action": "logon-success" if ok else "logon-failed",
            "outcome": "success" if ok else "failure",
            "code": "4624" if ok else "4625",
        },
        "user": {"name": user},
        "source": {"ip": ip},
        "host": {"name": host},
        "winlog": {"logon": {"type": logon_type}},
        "lab": {"scenario": scenario},
    }


def generate(seed=42, now=None):
    rng = random.Random(seed)
    now = now or datetime.now(timezone.utc).replace(microsecond=0)
    ev = []

    # baseline: 160 logins válidos + erros isolados (cada usuário tem seu IP)
    ip_of = {u: f"10.0.1.{10 + i}" for i, u in enumerate(BASE_USERS)}
    for _ in range(160):
        u = rng.choice(BASE_USERS)
        t = now - timedelta(seconds=rng.randint(60, 3600))
        ev.append(_ev(t, u, ip_of[u], True, "baseline", host=rng.choice(["dc01", "fs01", "ws-" + u[:3]])))
    for u in rng.sample(BASE_USERS, 8):
        for _ in range(rng.randint(1, 2)):
            t = now - timedelta(seconds=rng.randint(60, 3600))
            ev.append(_ev(t, u, ip_of[u], False, "baseline"))

    # falso positivo: svc_backup falha 1x/min por 30 min
    start = now - timedelta(minutes=35)
    for i in range(30):
        ev.append(_ev(start + timedelta(minutes=i), "svc_backup", SERVICE_IP, False,
                      "false_positive", host="fs01", logon_type="Service"))

    # brute force: 40 falhas em ~2 min + sucesso
    t = now - timedelta(minutes=12)
    for _ in range(40):
        t += timedelta(seconds=rng.uniform(2, 4))
        ev.append(_ev(t, "administrator", ATTACKER_BF, False, "bruteforce"))
    ev.append(_ev(t + timedelta(seconds=2), "administrator", ATTACKER_BF, True, "bruteforce"))

    # password spraying: 12 usuários x 2 tentativas
    t = now - timedelta(minutes=20)
    for _ in range(2):
        for u in SPRAY_USERS:
            t += timedelta(seconds=rng.uniform(6, 10))
            ev.append(_ev(t, u, ATTACKER_SPRAY, False, "spray"))

    return sorted(ev, key=lambda e: e["@timestamp"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/events.ndjson")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    events = generate(a.seed)
    with open(a.out, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"{len(events)} eventos gravados em {a.out}")


if __name__ == "__main__":
    main()
