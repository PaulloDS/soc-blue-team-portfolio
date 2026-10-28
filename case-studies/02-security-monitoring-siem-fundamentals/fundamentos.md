# 02 — Security Monitoring & SIEM Fundamentals

**Trilha:** HTB Academy — SOC Analyst Job Role Path  
**Status:** concluído  

## 1. Objetivo e principal aprendizado

Compreender como equipes SOC utilizam telemetria para monitorar ambientes, identificar sinais de ameaça, investigar alertas e apoiar resposta a incidentes. **Um SIEM centraliza dados, mas coletar logs não significa detectar ataques automaticamente:** detecção depende de qualidade de dados, lógica, contexto, validação e processo operacional.

## 2. Fluxo de monitoramento

```text
Fontes de telemetria → coleta → parsing/normalização → indexação/pesquisa
        → consulta ou regra → alerta → triagem → investigação → decisão
```

- **Fontes:** endpoints, autenticação, servidores, aplicações e infraestrutura de rede.
- **Coleta e ingestão:** os dados precisam chegar íntegros, com horários confiáveis.
- **Normalização:** campos coerentes facilitam pesquisas e correlações.
- **Regras e visualizações:** materializam hipóteses e permitem monitorar condições de risco.
- **Tratamento:** um alerta só é útil quando possui contexto e encaminhamento definido.

Ausência de eventos no dashboard pode representar **ausência de atividade ou falha na coleta**.

## 3. Elastic Stack na análise de segurança

| Componente | Papel usual |
| --- | --- |
| Elastic Agent / Beats (conforme a instalação) | Coleta e encaminhamento de eventos. |
| Elasticsearch | Indexação e pesquisa de documentos. |
| Kibana | Exploração no Discover e visualização de dados. |
| Elastic Security (se habilitado) | Regras e fluxos de detecção. |

O esquema dos campos depende da fonte e do pipeline; uma consulta só faz sentido depois de verificar os dados disponíveis.

## 4. KQL: filtrar não é correlacionar

Kibana Query Language (KQL) filtra registros por campos, valores, intervalos e operadores lógicos. KQL **não agrega, conta por grupos ou sequencia eventos por si só**. Exemplo conceitual (exige campos presentes e normalizados):

```kql
event.category: authentication AND event.outcome: failure
```

A consulta recupera eventos categorizados como falhas de autenticação, mas não comprova força bruta. Uma detecção por frequência necessita de uma **regra de limiar (threshold)**; detecção por sequência pode exigir lógica de correlação apropriada, como EQL.

Mais exemplos: [consultas-kql.md](consultas-kql.md).

## 5. Casos de uso de detecção

Uma detecção de qualidade começa por uma hipótese observável e pergunta:

1. Qual risco ou comportamento queremos monitorar?
2. Quais fontes de telemetria capturam esse comportamento?
3. Quais campos identificam usuário, ativo, origem, resultado e tempo?
4. O que é normal nesse ambiente? Onde podem surgir falsos positivos?
5. Como testar a detecção e definir triagem/escalonamento?

**Exemplo hipotético:** múltiplas falhas de autenticação oriundas de uma mesma origem. Isso pode ser compatível com [MITRE ATT&CK T1110 — Brute Force](https://attack.mitre.org/techniques/T1110/), mas não confirma um ataque sem análise contextual.

O modelo de caso de uso permanecerá em planejamento privado até que exista laboratório próprio, resultados verificáveis e documentação das limitações.

## 6. Dashboards e visibilidade

Uma visualização útil responde a uma pergunta operacional: quais fontes pararam de enviar eventos? Onde se concentram falhas de autenticação? Quais alertas recorrentes acabam classificados como benignos? Métricas precisam de contexto, janelas temporais e verificação de qualidade dos dados.

## 7. Continuidade com Incident Handling Process

O módulo anterior abordou o processo de investigação e resposta. Este aprofundou **como os eventos chegam ao analista e como são pesquisados e transformados em sinais de atenção**.

`telemetria → detecção → alerta → triagem → investigação → decisão documentada`

Conhecimento ofensivo ajuda a formular hipóteses, mas **hipótese não substitui evidência**.

## 8. Próximo experimento autoral

Planejo ingerir logs de autenticação gerados em laboratório controlado no Elastic, validar consultas KQL, criar uma regra adequada e registrar resultados e falsos positivos. **Esse experimento ainda não foi realizado nem validado neste repositório.**

## Referências

- [HTB — Security Monitoring & SIEM Fundamentals](https://academy.hackthebox.com/course/preview/security-monitoring--siem-fundamentals)
- [Elastic — KQL overview](https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql)
- [Elastic — KQL syntax](https://www.elastic.co/docs/reference/query-languages/kql)
- [Elastic — Custom query rules](https://www.elastic.co/docs/solutions/security/detect-and-alert/custom-query)
- [MITRE ATT&CK — T1110](https://attack.mitre.org/techniques/T1110/)

*Documento autoral; não contém respostas, flags, capturas ou resolução do assessment da HTB.*
