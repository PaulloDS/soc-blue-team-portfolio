# Relatório de incidente (cenário simulado)

> Dados sintéticos do laboratório. Substitua os horários e anexe seus prints reais em `docs/img/`.

| Campo | Valor |
|---|---|
| ID | LAB-2026-001 |
| Severidade | Crítica (conta privilegiada possivelmente comprometida) |
| Regras acionadas | Brute force por limiar, Falhas -> sucesso (EQL) |
| Origem | 203.0.113.45 (externa) |
| Conta alvo | administrator no host dc01 |

## Resumo
Um IP externo executou 40 tentativas de login em cerca de 2 minutos contra `administrator` e, em seguida, obteve um login com sucesso. O padrão (rajada, conta única, sucesso ao final) é compatível com brute force bem-sucedido (T1110.001).

## Linha do tempo (UTC)
1. `T-12:00` primeira falha 4625 de 203.0.113.45 contra administrator
2. `T-10:00` 40ª falha; a regra por limiar passa a disparar
3. `T-09:58` login 4624 com sucesso (sequência completa; regra EQL dispara)

## Evidências
- Discover: filtro `source.ip:"203.0.113.45"` (print em `docs/img/discover-bruteforce.png`)
- Alerta da regra de sequência (print em `docs/img/alert-sequence.png`)

## Eventos relacionados e descartes
- 198.51.100.77: password spraying (12 contas, 24 tentativas, sem sucesso). Origem diferente; tratar em ticket separado e bloquear.
- svc_backup / 10.0.5.20: falso positivo conhecido (ver `docs/tuning.md`).

## Conclusão
Brute force **confirmado** com acesso obtido: a hipótese inicial (falhas repetidas) foi sustentada por contexto (origem externa, conta única, janela curta, sucesso final).

## Recomendações
1. Resetar a senha de `administrator` e revogar sessões ativas
2. Bloquear 203.0.113.45 e 198.51.100.77 no perímetro
3. Investigar atividade pós-login de `administrator` em dc01
4. Exigir MFA e política de bloqueio de conta
5. Corrigir a credencial do `svc_backup`
