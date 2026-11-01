#!/usr/bin/env python3
"""Gera detections/rules/bruteforce_rules.ndjson (importável no Kibana Security)."""
import json, pathlib

INDEX = ["lab-winlogs*"]
AUTH_FAIL = "event.category:authentication and event.outcome:failure"
TUNED_FAIL = AUTH_FAIL + ' and not (user.name:"svc_backup" and source.ip:"10.0.5.20")'


def threat(sub_id, sub_name, tech_id="T1110", tech_name="Brute Force"):
    tech = {"id": tech_id, "name": tech_name, "reference": f"https://attack.mitre.org/techniques/{tech_id}/"}
    if sub_id:
        tech["subtechnique"] = [{"id": sub_id, "name": sub_name,
                                 "reference": f"https://attack.mitre.org/techniques/{sub_id.replace('.', '/')}/"}]
    return [{"framework": "MITRE ATT&CK",
             "tactic": {"id": "TA0006", "name": "Credential Access",
                        "reference": "https://attack.mitre.org/tactics/TA0006/"},
             "technique": [tech]}]


COMMON = {"author": ["Paulo Douglas"], "license": "MIT", "index": INDEX, "interval": "5m",
          "from": "now-1h", "to": "now", "max_signals": 100, "version": 1, "references": [],
          "risk_score": 47, "severity": "medium"}
# from=now-1h: janela larga SÓ para o lab (dados gerados pouco antes). Em produção, use interval+overlap.

RULES = [
    {"rule_id": "lab-bf-threshold-v2-tuned", "name": "LAB - Brute force por limiar (tunada)",
     "description": "5 ou mais falhas de login do mesmo IP contra a mesma conta. Versão com exclusão da conta de serviço conhecida (svc_backup em 10.0.5.20).",
     "type": "threshold", "language": "kuery", "query": TUNED_FAIL,
     "threshold": {"field": ["source.ip", "user.name"], "value": 5},
     "threat": threat("T1110.001", "Password Guessing"), "enabled": True,
     "tags": ["LAB", "Brute Force", "T1110", "Tuned"],
     "false_positives": ["Usuário esquecendo a senha", "Serviço com credencial desatualizada (filtrar caso a caso)"]},
    {"rule_id": "lab-bf-threshold-v1-untuned", "name": "LAB - Brute force por limiar (SEM tuning)",
     "description": "Mesma regra sem exclusões. Mantida DESABILITADA para demonstrar o falso positivo do svc_backup. Habilite para comparar.",
     "type": "threshold", "language": "kuery", "query": AUTH_FAIL,
     "threshold": {"field": ["source.ip", "user.name"], "value": 5},
     "threat": threat("T1110.001", "Password Guessing"), "enabled": False,
     "tags": ["LAB", "Brute Force", "T1110", "Untuned"], "false_positives": ["Contas de serviço com credencial antiga"]},
    {"rule_id": "lab-spray-threshold-v1", "name": "LAB - Password spraying (muitas contas, mesmo IP)",
     "description": "10 ou mais falhas vindas do mesmo IP contra pelo menos 5 contas distintas. Pega o que a regra por conta não vê.",
     "type": "threshold", "language": "kuery", "query": AUTH_FAIL,
     "threshold": {"field": ["source.ip"], "value": 10, "cardinality": [{"field": "user.name", "value": 5}]},
     "threat": threat("T1110.003", "Password Spraying"), "enabled": True,
     "tags": ["LAB", "Password Spraying", "T1110.003"], "false_positives": ["NAT corporativo com muitos usuários errando senha"],
     "risk_score": 73, "severity": "high"},
    {"rule_id": "lab-bf-sequence-v1", "name": "LAB - Falhas repetidas seguidas de login com sucesso",
     "description": "Sequência EQL: 5+ falhas e depois sucesso para o mesmo IP e conta em até 10 minutos. Indica possível comprometimento.",
     "type": "eql", "language": "eql",
     "query": 'sequence by source.ip, user.name with maxspan=10m\n  [authentication where event.outcome == "failure"] with runs=5\n  [authentication where event.outcome == "success"]',
     "threat": threat(None, None),
     "enabled": True, "tags": ["LAB", "Brute Force", "T1110", "Sequence"],
     "false_positives": ["Usuário que erra a senha várias vezes e acerta em seguida"],
     "risk_score": 99, "severity": "critical"},
]


def main():
    out = pathlib.Path(__file__).parent / "rules" / "bruteforce_rules.ndjson"
    with out.open("w", encoding="utf-8") as f:
        for r in RULES:
            f.write(json.dumps({**COMMON, **r}, ensure_ascii=False) + "\n")
    print(f"{len(RULES)} regras em {out}")


if __name__ == "__main__":
    main()
