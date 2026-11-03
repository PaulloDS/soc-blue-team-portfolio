# SIEM Brute Force Detection Lab

<img src="https://i.imgur.com/pMgPbSE.png"/>

**Laboratório autoral de monitoramento e detecção de tentativas de autenticação com Elastic Stack, Docker, Python e regras para Kibana Security.** A implementação inclui cenários sintéticos reproduzíveis, testes de lógica e fluxos opcionais para capturar logs reais de SSH em ambiente isolado. As evidências publicadas devem ser interpretadas conforme o nível de validação descrito abaixo.

Feito como projeto prático depois de concluir o módulo *Security Monitoring & SIEM Fundamentals* (HTB Academy, SOC Analyst Path). O objetivo não era só terminar o módulo, era provar com um sistema funcionando, que sei transformar eventos de log em detecção de verdade.

## O que este projeto prova

| Competência | Onde está no repositório |
|---|---|
| Arquitetar um ambiente de monitoramento (Elastic Stack via Docker) | `docker-compose.yml`, `lab.sh` |
| Escrever consultas e investigar com KQL | `queries/kql.md` |
| Construir regras de detecção (limiar, cardinalidade, sequência EQL) | `detections/build_rules.py` |
| Mapear detecções para MITRE ATT&CK | `docs/mitre-mapping.md` |
| Fazer tuning de um falso positivo com uma decisão documentada | `docs/tuning.md` |
| Documentar um roteiro de VM com agente de coleta | `docs/real-soc-lab-howto.md` — instruções, sem logs/capturas da VM versionados |
| Testar lógica de detecção como código | `tests/` — suíte de testes automatizados; o README anteriormente informava 44 testes (confirme a contagem no seu ambiente com `./lab.sh test`) |
| Documentar um incidente no formato que um SOC usa | `docs/incident-report.md` |

## O laboratório, em um diagrama

```
VM vítima (Linux, Filebeat)  <-- ataque real (Hydra / script Python multi-IP) --  Atacante
         |
         | logs reais de autenticação (etapa opcional; exigir evidência)
         v
   Elasticsearch + Kibana (Docker Compose)
         |
   4 definições de regras -> Security > Alerts (validar disparos no Kibana)
```

Também existe uma versão sintética (gerador de eventos determinístico) para validar a
lógica de detecção em segundos, sem depender de VM, sendo útil para revisão de código e CI.
As duas coexistem no mesmo repositório.

## Resultados documentados e níveis de evidência

> <img src="https://i.imgur.com/JKCFuhC.png"/>
> <img src="https://i.imgur.com/5y0DFvK.png"/>

O trecho abaixo é uma **saída ilustrativa/documentada do verificador** para o cenário sintético. O script consulta agregações do Elasticsearch e compara com a lógica Python; **não valida sozinho** os alertas emitidos pelo motor de regras do Kibana:
```
Limiar (>=5 falhas por IP+usuário, toda a janela do lab):

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
  (4 falhas não alertam, 5 alertam), não só o caminho feliz.
- **Fui do simulado para o real de propósito.** O gerador sintético prova a lógica em
  segundos; a VM real prova que o sistema inteiro funciona com dados que eu não controlo.

## Resultado técnico
Quatro definições de regras (limiar, spraying, sequência EQL e variante desabilitada sem tuning) estão disponíveis e mapeadas ao MITRE ATT&CK (T1110, T1110.001 e T1110.003). A lógica de detecção Python dispõe de testes automatizados; a integração no Elasticsearch é verificável com `./lab.sh verify`. Execução de ataque real e geração de alertas nativos do Kibana exigem evidências específicas, distintas dos dados gerados sinteticamente.

| Regra | Tipo | Lógica | MITRE |
|---|---|---|---|
| Brute force por limiar (tunada) | Threshold | >=5 falhas por IP+conta, exceto `svc_backup`@`10.0.5.20` | T1110.001 |
| Brute force por limiar (sem tuning) | Threshold | idem, sem exceção (desabilitada, só para comparação) | T1110.001 |
| Password spraying | Threshold + cardinalidade | >=10 falhas do mesmo IP contra >=5 contas | T1110.003 |
| Falhas seguidas de sucesso | EQL sequence | 5+ falhas e depois sucesso, mesmo IP+conta, 10 min | T1110 |

## Rodar você mesmo (para conferir)
O projeto é reproduzível, não é só uma descrição do que eu fiz.
```bash
pip install -r requirements-dev.txt
./lab.sh test                                   # 44 testes, sem precisar de Docker
./lab.sh up && ./lab.sh wait && ./lab.sh demo    # sobe o Elastic Stack e roda o cenário completo
```
A interface local fica em `http://localhost:5601` (usuário `elastic`, senha definida em `.env`; o arquivo é copiado de `.env.example`, portanto altere a senha de exemplo antes de executar). As portas do host ficam vinculadas a `127.0.0.1` por padrão. Para acesso por uma VM isolada, configure explicitamente o IP da interface Host-only no `.env`, conforme `docs/real-soc-lab-howto.md`. A documentação
técnica de cada etapa: montar a VM vítima, atacar de verdade, multiplicar os IPs de
origem, construir o dashboard, gravar a demo, está em `docs/`, para quem quiser entender
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

## Integridade das evidências, limitações e próximos passos
O cenário sintético valida lógica, não coleta real e por isso o lab também tem um caminho
com VM e tráfego de verdade (`docs/real-soc-lab-howto.md`). Detalhes em [limitações](docs/limitations.md) e no [relatório sintético](docs/incident-report.md). A pasta `docs/img/` ainda não contém as capturas citadas no relatório antigo; imagens externas incorporadas acima não substituem logs, IDs de alertas e capturas locais verificáveis. Próximos passos: coleta Windows/Sysmon, evidência de execução das regras no Kibana e integração opcional de notificações (e-mail/webhook).

## Licença
MIT. Autor: Paulo Douglas.
