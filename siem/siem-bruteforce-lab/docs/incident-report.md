# Relatório de incidente (cenário simulado)

> **Estudo de caso sintético**, construído com os eventos do gerador `generator/generate_events.py`. Não representa um incidente corporativo real. As capturas locais de Kibana referidas anteriormente não estão versionadas neste repositório; somente adicione imagens em `docs/img/` depois de obtê-las e revisá-las.

| Campo | Valor |
|---|---|
| ID | LAB-2026-001 |
| Severidade | Crítica (conta privilegiada possivelmente comprometida) |
| Lógicas contempladas | Brute force por limiar e falhas seguidas de sucesso; regras de Kibana definidas no código, mas disparo efetivo de alertas não comprovado por captura versionada |
| Origem | 203.0.113.45 (externa) |
| Conta alvo | administrator no host dc01 |

## Resumo
Um IP externo executou 40 tentativas de login em cerca de 2 minutos contra `administrator` e, em seguida, obteve um login com sucesso. O padrão (rajada, conta única, sucesso ao final) é compatível com brute force bem-sucedido (T1110.001).

## Linha do tempo relativa (cenário gerado)
1. Aproximadamente T-12 min: início das falhas simuladas (código 4625).
2. Nos minutos seguintes: sequência de 40 falhas simuladas de autenticação.
3. Após as falhas: um evento de autenticação bem-sucedida (código 4624), gerado intencionalmente.

**Observação:** horários exatos variam a cada geração. O roteiro acima descreve a sequência nos dados sintéticos e **não** atesta disparo de alertas no motor do Kibana.

## Evidências disponíveis e pendências
- **Fonte reproduzível:** `generator/generate_events.py` cria os eventos marcados com `lab.scenario: bruteforce`.
- **Lógica auditável:** `detections/detector.py`, `detections/build_rules.py` e `tests/`.
- **Verificação da agregação e lógica Python:** `scripts/verify.py`; isso **não equivale** a confirmar alertas emitidos pela interface de detecção do Kibana.
- **Capturas ainda não anexadas:** imagens do Discover e do painel Security > Alerts. A pasta `docs/img/` contém apenas `.gitkeep`. Capturas externas incorporadas no README não substituem evidências locais versionadas.

Para comprovar execução do motor de regras, exportar evidência verificável de alerta com ID da regra, horário, índice, origem e dados de suporte, sem segredos ou dados sensíveis.

## Eventos relacionados e descartes
- 198.51.100.77: password spraying (12 contas, 24 tentativas, sem sucesso). Origem diferente; tratar em ticket separado e bloquear.
- svc_backup / 10.0.5.20: falso positivo conhecido (ver `docs/tuning.md`).

## Conclusão
**No cenário sintético**, a sequência gerada representa um brute force com evento de autenticação bem-sucedida. Isso é confirmado pela definição do gerador e pode ser identificado pela lógica de análise; não comprova, por si só, comprometimento real nem funcionamento ponta a ponta da execução agendada de regras do Kibana.

A classificação "crítica" neste documento é uma severidade **hipotética do exercício**, não uma medição de risco em ambiente corporativo.

## Recomendações
1. Em um incidente real equivalente, verificar a legitimidade do acesso e preservar evidências antes de decidir o tratamento.
2. Se houver comprometimento confirmado, aplicar contenção aprovada, revogar sessões e redefinir credenciais.
3. Investigar a atividade pós-autenticação e avaliar medidas preventivas, como MFA e bloqueios adequados.
4. Avaliar regras e tuning para falsos positivos sem introduzir pontos cegos.
5. Tratar o erro recorrente da conta de serviço `svc_backup` na origem.

Os IPs `203.0.113.45` e `198.51.100.77` pertencem a faixas reservadas para documentação; são identificadores de exemplo, não destinos para bloqueio em produção.
