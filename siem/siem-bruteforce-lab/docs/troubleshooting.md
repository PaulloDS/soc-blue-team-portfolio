# Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Elasticsearch sai com `max virtual memory areas` (Linux) | `sudo sysctl -w vm.max_map_count=262144` |
| Containers reiniciando / OOM | Dê pelo menos 4 GB de RAM ao Docker |
| `./lab.sh wait` não termina | `docker compose logs kibana`; Kibana leva 1-3 min na primeira vez |
| Importação de regras retorna erro de schema | Veja a mensagem em `./lab.sh rules`; a versão do Kibana pode ter campo diferente. A stack está fixada em 8.15.3 (`.env`) |
| Erro dizendo que API keys exigem TLS | Habilite TLS no ES ou use `./lab.sh verify` + Discover, que não dependem do motor de detecção |
| Regra EQL com `runs=5` rejeitada | Substitua pela sequência explícita com 5 blocos de falha antes do sucesso, ou use apenas as regras de limiar |
| Sem alertas no Kibana Security | Rode `./lab.sh demo` de novo (dados envelhecem) e veja Security > Rules > Last response |
