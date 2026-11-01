#!/usr/bin/env bash
# Uso: ./lab.sh {up|wait|data|ingest|kibana|rules|verify|demo|test|down}
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a
KB="${KIBANA_URL:-http://localhost:5601}"
case "${1:-help}" in
  up)     docker compose up -d ;;
  wait)   echo "Aguardando Kibana (pode levar 1-3 min)..."
          until curl -s -u "elastic:$ELASTIC_PASSWORD" "$KB/api/status" | grep -q '"level":"available"'; do sleep 5; done
          echo "Kibana disponível em $KB" ;;
  data)   python3 generator/generate_events.py --out data/events.ndjson ;;
  ingest) python3 scripts/ingest.py --reset ;;
  kibana) curl -s -u "elastic:$ELASTIC_PASSWORD" -X POST "$KB/api/data_views/data_view" \
            -H "kbn-xsrf: true" -H "Content-Type: application/json" \
            -d '{"data_view":{"title":"lab-winlogs*","name":"lab-winlogs","timeFieldName":"@timestamp"}}' >/dev/null \
            && echo "Data view lab-winlogs criada (ou já existia)" ;;
  rules)  curl -s -u "elastic:$ELASTIC_PASSWORD" -X POST "$KB/api/detection_engine/rules/_import?overwrite=true" \
            -H "kbn-xsrf: true" --form file=@detections/rules/bruteforce_rules.ndjson | python3 -m json.tool ;;
  verify) python3 scripts/verify.py ;;
  demo)   "$0" data; "$0" ingest; "$0" kibana; "$0" rules; "$0" verify ;;
  attack) ./scripts/attack/run_attack.sh ;;
  test)   python3 -m pytest -q ;;
  down)   docker compose --profile attack down -v ;;
  *)      sed -n '2p' "$0" ;;
esac
