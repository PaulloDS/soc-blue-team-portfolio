# KQL para triagem — exemplos comentados

**Natureza:** referência didática. As consultas abaixo **não são evidências de execução em um laboratório próprio**. Confira sempre os campos e o mapping do índice no Kibana.

KQL (*Kibana Query Language*) **filtra documentos**. Para contagem por grupo, sequências ou geração de alertas, a plataforma necessita de funcionalidades adicionais adequadas.

## 1. Todos os eventos de autenticação

```kql
event.category: authentication
```

Útil quando a integração preenche o campo `event.category` corretamente.

## 2. Somente falhas de autenticação

```kql
event.category: authentication AND event.outcome: failure
```

Uma falha isolada não representa necessariamente atividade maliciosa.

## 3. Identificar evento Windows 4625

```kql
event.code: "4625"
```

No Windows Security, o evento 4625 indica falha de logon. O campo `event.code` precisa estar presente e normalizado; verifique o evento bruto e a origem dos dados.

## 4. Eventos com endereço de origem e usuário

```kql
source.ip: * AND user.name: *
```

Mostra documentos em que os dois campos existem. Alguns eventos locais não terão um IP de origem individual.

## 5. Falhas recentes

```kql
@timestamp >= now-24h AND event.category: authentication AND event.outcome: failure
```

Confira o fuso e o seletor de tempo do Kibana: eles também afetam a janela analisada.

## 6. Investigar um ativo de laboratório

```kql
host.name: "workstation-lab" AND event.category: authentication
```

Substitua por um host do seu **ambiente autorizado**. `host.name` depende da fonte de eventos.

## 7. Evitar uma conclusão incorreta

```kql
event.category: authentication AND NOT event.outcome: success
```

Este filtro também pode incluir eventos com `event.outcome` ausente. Para selecionar explicitamente falhas, prefira `event.outcome: failure`.

## 8. Preparar um caso de uso por limiar

```kql
event.category: authentication AND event.outcome: failure AND source.ip: *
```

O filtro seleciona eventos candidatos. Ele **não conta tentativas**. Para alertar quando uma origem ultrapassar determinado número de falhas em uma janela temporal, é necessário configurar e validar uma regra por **threshold** ou lógica equivalente.

## Checklist de consulta confiável

- [ x ] Conferi o intervalo de tempo, o fuso e o data view.
- [ x ] Verifiquei os campos e tipos realmente presentes.
- [ x ] Analisei exemplos de registros brutos.
- [ x ] Avaliei se NAT, VPN, proxies ou lacunas de coleta afetam a interpretação.
- [ x ] Separei resultados observados de hipóteses.

## Referências

- [Elastic — KQL syntax reference](https://www.elastic.co/docs/reference/query-languages/kql)
- [Elastic — KQL overview](https://www.elastic.co/docs/explore-analyze/query-filter/languages/kql)
- [Elastic — Custom query rules](https://www.elastic.co/docs/solutions/security/detect-and-alert/custom-query)
