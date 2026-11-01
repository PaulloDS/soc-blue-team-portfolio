# Consultas KQL (Kibana > Discover > data view `lab-winlogs`)

Ajuste o intervalo de tempo para "Last 1 hour".

| Objetivo | KQL |
|---|---|
| Todas as falhas de login | `event.category:authentication and event.outcome:failure` |
| Falhas contra uma conta | `event.outcome:failure and user.name:"administrator"` |
| Falhas de uma origem | `event.outcome:failure and source.ip:"203.0.113.45"` |
| Sucesso de logon após ataque (alvo da sequência) | `event.outcome:success and source.ip:"203.0.113.45"` |
| Origens externas (exclui rede interna) | `event.outcome:failure and not source.ip:"10.0.0.0/8"` |
| Contas de serviço | `user.name:svc_*` |
| Falso positivo conhecido | `user.name:"svc_backup" and source.ip:"10.0.5.20"` |
| Remover o falso positivo | `event.outcome:failure and not (user.name:"svc_backup" and source.ip:"10.0.5.20")` |

## Roteiro de investigação (o que fazer no Discover)
1. Rode a consulta de falhas e adicione as colunas `source.ip`, `user.name`, `host.name`.
2. Clique em `source.ip` > "Top 5 values": dois IPs externos dominam.
3. Filtre por `203.0.113.45`: um usuário só (`administrator`), ~40 falhas em ~2 min, e **um sucesso no final**.
4. Filtre por `198.51.100.77`: 12 usuários, 2 tentativas cada, sem sucesso = spraying.
5. Filtre por `10.0.5.20`: falhas regulares, 1 por minuto, conta `svc_backup`, logon type `Service` = padrão de serviço, não de ataque.
