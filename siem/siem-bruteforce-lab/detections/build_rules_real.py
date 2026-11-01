#!/usr/bin/env python3
"""Gera detections/rules/real_lab_rules.ndjson: as MESMAS 4 regras, mas apontadas
para os índices que o Filebeat (módulo 'system') e o Winlogbeat (módulo 'security')
criam de verdade, com o setup oficial deles (ECS nativo, sem script de ingestão custom).

Use este arquivo quando estiver monitorando uma VM real (docs/real-soc-lab-howto.md).
Para o lab sintético/Docker, continue usando bruteforce_rules.ndjson.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build_rules import RULES, COMMON  # reusa as 4 regras já definidas

REAL_INDEX = ["filebeat-*", "winlogbeat-*"]


def main():
    out = pathlib.Path(__file__).parent / "rules" / "real_lab_rules.ndjson"
    with out.open("w", encoding="utf-8") as f:
        for r in RULES:
            r2 = {**COMMON, **r}
            r2["index"] = REAL_INDEX
            r2["rule_id"] = r2["rule_id"].replace("lab-", "real-")
            r2["name"] = r2["name"].replace("LAB -", "REAL -")
            f.write(json.dumps(r2, ensure_ascii=False) + "\n")
    print(f"{len(RULES)} regras (índices reais) em {out}")


if __name__ == "__main__":
    main()
