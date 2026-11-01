# Tuning: o falso positivo do `svc_backup`

**Problema.** A conta de serviço `svc_backup` (host `fs01`, IP `10.0.5.20`) falha 1 vez por minuto, porque a credencial salva no job está desatualizada. A regra por limiar (5 falhas em 5 min) dispara continuamente.

**Evidências de que não é ataque**
- origem interna e fixa; a mesma desde o início
- cadência perfeitamente regular (1/min), sem rajada
- logon type `Service`, não `Network`
- nunca há sucesso depois
- a conta tem nome de serviço e um único host de origem

**Decisão.** Excluir a combinação exata (`user.name` + `source.ip`) na query da regra, e abrir chamado para corrigir a credencial na origem. Excluir só o nome da conta deixaria um ataque contra `svc_backup` de outro IP invisível, por isso a exceção é o par.

```
event.category:authentication and event.outcome:failure
and not (user.name:"svc_backup" and source.ip:"10.0.5.20")
```

**Risco residual.** Se o atacante conseguir executar a partir de `10.0.5.20`, a exceção o esconde. Mitigação: a regra de sequência (falha -> sucesso) não tem exceção e continua cobrindo esse caso.

**Como ver na prática:** habilite `LAB - Brute force por limiar (SEM tuning)` no Kibana, compare os alertas das duas versões e desabilite de novo. Os testes (`tests/test_detector.py`) provam a mesma diferença offline.
