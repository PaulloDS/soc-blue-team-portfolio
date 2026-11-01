#!/usr/bin/env bash
# Sobe o alvo SSH de laboratório, ataca com Hydra, captura os logs REAIS
# e ingere no mesmo índice do lab (lab.scenario = "real_attack").
set -euo pipefail
cd "$(dirname "$0")/../.."
[ -f .env ] || cp .env.example .env
command -v hydra >/dev/null || { echo "Hydra não encontrado. No Kali já vem instalado; em Debian/Ubuntu: sudo apt install hydra"; exit 1; }
command -v docker >/dev/null || { echo "Docker não encontrado."; exit 1; }

echo "==> Subindo alvo SSH de laboratório (senha fraca de propósito)..."
docker compose --profile attack up -d --build attack-target

echo "==> Aguardando a porta 2222 responder..."
python3 - <<'PY'
import socket, time, sys
for _ in range(30):
    try:
        socket.create_connection(("localhost", 2222), 1).close()
        sys.exit(0)
    except OSError:
        time.sleep(1)
sys.exit("Porta 2222 não respondeu a tempo.")
PY

echo "==> Atacando com Hydra (pode levar 1-2 min)..."
hydra -L scripts/attack/userlist.txt -P scripts/attack/wordlist.txt -t 4 -f \
  -s 2222 ssh://127.0.0.1 || true
echo "(hydra pode terminar com 'quit' ao achar a credencial correta; isso é esperado)"

echo "==> Capturando os logs reais do alvo..."
mkdir -p data
docker compose logs attack-target --no-color --timestamps > data/real-ssh-attack.log

echo "==> Convertendo para ECS e ingerindo..."
python3 scripts/attack/parse_sshd_log.py --in data/real-ssh-attack.log --out data/real-ssh-attack.ndjson
python3 scripts/ingest.py --file data/real-ssh-attack.ndjson

echo
echo "Pronto. No Kibana Discover, filtre: lab.scenario:real_attack"
echo "Para encerrar o alvo: docker compose --profile attack down"
