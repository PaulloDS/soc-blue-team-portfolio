# Gravar a demo para o LinkedIn

Objetivo: 30-60s, sem áudio (ou com narração curta), mostrando o lab reagindo a um
ataque de verdade. Ferramentas: OBS Studio (Linux/Win/Mac) ou Peek/ScreenToGif para GIF.

## Roteiro sugerido (corte seco entre as cenas, sem precisar editar muito)
1. **(5s)** Terminal: `./scripts/attack/run_attack.sh` rodando, Hydra tentando senhas
2. **(5s)** Kibana > Discover, filtro `lab.scenario:real_attack`, dados chegando
3. **(10s)** Kibana > Security > Alerts, o alerta de sequência aparecendo
4. **(10s)** Dashboard com o gráfico de barras (falhas por origem) e a tabela de contas
5. **(5s)** Terminal: `./lab.sh verify` terminando em "TUDO CERTO"
6. **(5s)** README do GitHub, rolando até a seção de regras

## Prints mínimos para o GitHub (`docs/img/`)
- `discover-real-attack.png` — Discover filtrado por `lab.scenario:real_attack`
- `alert-sequence.png` — alerta da regra de sequência disparado
- `dashboard.png` — o dashboard com os dois gráficos
- `verify-output.png` — terminal com `./lab.sh verify` em "TUDO CERTO"
- `rules-list.png` — Security > Rules mostrando as 4 regras (uma desabilitada)

## Dicas práticas
- F11 antes de gravar/printar para esconder barra de favoritos e abas
- Gere dados de novo (`./lab.sh demo` + `run_attack.sh`) se o intervalo de tempo "envelhecer"
- Um GIF de 15-20s costuma rodar melhor no feed do LinkedIn que vídeo com áudio
