# SIEM Brute Force Detection Lab

**Projetei, construí e testei um laboratório de detecção de intrusão com Elastic Stack — do zero até atacar minha própria VM de verdade e detectar o ataque em tempo real.**

Feito como projeto prático depois de concluir o módulo *Security Monitoring & SIEM Fundamentals* (HTB Academy, SOC Analyst Path). O objetivo não era só terminar o módulo — era provar, com um sistema funcionando, que sei transformar eventos de log em detecção de verdade.

## O que este projeto prova

| Competência | Onde está no repositório |
|---|---|
| Arquitetar um ambiente de monitoramento (Elastic Stack via Docker) | `docker-compose.yml`, `lab.sh` |
| Escrever consultas e investigar com KQL | `queries/kql.md` |
| Construir regras de detecção (limiar, cardinalidade, sequência EQL) | `detections/build_rules.py` |
| Mapear detecções para MITRE ATT&CK | `docs/mitre-mapping.md` |
| Fazer tuning de um falso positivo com uma decisão documentada | `docs/tuning.md` |
| Montar um alvo real (VM com agente de coleta) e atacar de verdade | `docs/real-soc-lab-howto.md` |
| Testar detecção como se testa código | `tests/` — 44 testes |
| Documentar um incidente no formato que um SOC usa | `docs/incident-report.md` |

## O laboratório, em uma imagem

```
VM vítima (Linux, Filebeat)  <-- ataque real (Hydra / script Python multi-IP) --  Atacante
         |
         | logs reais de autenticação
         v
   Elasticsearch + Kibana (Docker Compose)
         |
   4 regras de detecção -> Security > Alerts
```

Também existe uma versão sintética (gerador de eventos determinístico) para validar a
lógica de detecção em segundos, sem depender de VM — útil para revisão de código e CI.
As duas coexistem no mesmo repositório.

## O que aconteceu quando rodei (evidência)

> _Prints reais do meu ambiente: Discover recebendo o ataque, o alerta de sequência
> disparando e o dashboard consolidado. Ver `docs/img/`._

Saída real do `./lab.sh verify` contra os dados do meu teste:
```
Limiar (>=5 falhas por IP+usuário, toda a janela do lab):
   203.0.113.45 -> administrator   40 falhas
      10.0.5.20 -> svc_backup      30 falhas
[OK]    brute force detectado (203.0.113.45 -> administrator)
[OK]    falso positivo visível SEM tuning (svc_backup)
[OK]    com tuning, só o ataque permanece
[OK]    password spraying detectado (198.51.100.77)
[OK]    sequência falha->sucesso detectada
Resultado: TUDO CERTO
```

## Decisões técnicas que tomei (e por quê)

- **A regra por conta não vê password spraying.** Um atacante testando poucas senhas
  contra muitas contas fica abaixo do limiar por conta. Resolvi com uma segunda regra,
  agrupada só por IP com cardinalidade mínima de usuários distintos.
- **Tuning do falso positivo (`svc_backup`) excluiu o par conta+IP, não a conta inteira.**
  Excluir só o nome da conta esconderia um ataque de verdade contra essa mesma conta vindo
  de outro IP. Mantive uma segunda regra idêntica, sem a exceção, desabilitada, só para
  comparação lado a lado (`docs/tuning.md`).
- **Testei a lógica de detecção como testo código.** 44 testes cobrem os casos de limite
  (4 falhas não alertam, 5 alertam) — não só o caminho feliz.
- **Fui do simulado para o real de propósito.** O gerador sintético prova a lógica em
  segundos; a VM real prova que o sistema inteiro funciona com dados que eu não controlo.

## Resultado técnico
4 regras de detecção (limiar, spraying, sequência EQL, e uma variante sem tuning para
comparação), mapeadas ao MITRE ATT&CK (T1110, T1110.001, T1110.003), validadas por
44 testes automatizados e por um ataque real contra uma VM própria.

| Regra | Tipo | Lógica | MITRE |
|---|---|---|---|
| Brute force por limiar (tunada) | Threshold | >=5 falhas por IP+conta, exceto `svc_backup`@`10.0.5.20` | T1110.001 |
| Brute force por limiar (sem tuning) | Threshold | idem, sem exceção (desabilitada, só para comparação) | T1110.001 |
| Password spraying | Threshold + cardinalidade | >=10 falhas do mesmo IP contra >=5 contas | T1110.003 |
| Falhas seguidas de sucesso | EQL sequence | 5+ falhas e depois sucesso, mesmo IP+conta, 10 min | T1110 |

## Rodar você mesmo (para conferir)
O projeto é reproduzível — não é só uma descrição do que eu fiz.
```bash
pip install -r requirements-dev.txt
./lab.sh test                                   # 44 testes, sem precisar de Docker
./lab.sh up && ./lab.sh wait && ./lab.sh demo    # sobe o Elastic Stack e roda o cenário completo
```
Abre em `http://localhost:5601` (usuário `elastic`, senha gerada em `.env`). A documentação
técnica de cada etapa — montar a VM vítima, atacar de verdade, multiplicar os IPs de
origem, construir o dashboard, gravar a demo — está em `docs/`, para quem quiser entender
o processo com esse nível de detalhe.

## Estrutura
```
generator/     gerador de eventos sintético (determinístico por seed)
detections/    lógica de detecção testável + regras do Kibana (sintéticas e para dados reais)
scripts/       ingestão, validação e o orquestrador de ataque multi-IP
attack-target/ alvo SSH containerizado (opção rápida, sem precisar de VM)
queries/       consultas KQL usadas na investigação
tests/         44 testes (pytest)
docs/          MITRE, tuning, relatório de incidente, setup da VM real, limitações
```

## Limitações e próximos passos
O cenário sintético valida lógica, não coleta real — por isso o lab também tem um caminho
com VM e tráfego de verdade (`docs/real-soc-lab-howto.md`). Detalhes completos em
`docs/limitations.md`. Próximo passo: telemetria Windows real com Sysmon, para cobrir o
cenário de Active Directory, além de ações automatizadas nas regras (alerta por e-mail/webhook).

## Licença
MIT. Autor: Paulo Douglas.
