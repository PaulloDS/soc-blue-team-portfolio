# Modelo de triagem de alerta — SOC N1

> **TEMPLATE, NÃO UM CASO REAL.**

## 1. Identificação

| Campo | Preenchimento |
| --- | --- |
| ID da investigação | `[CASE-ID]` |
| Título do alerta | `[título descritivo]` |
| Data/hora do alerta (fuso) | `[AAAA-MM-DD HH:MM UTC±HH]` |
| Início/fim da janela analisada | `[intervalo]` |
| Fonte do alerta / regra | `[sistema, regra, versão]` |
| Ativo / usuário afetado | `[identificador anonimizado]` |
| Analista responsável | `[nome ou identificação]` |
| Estado inicial | `[novo / em triagem / escalado]` |

## 2. Descrição inicial

**O que foi sinalizado:**  
`[resumo objetivo do alerta, sem assumir causa ou intenção]`

**Por que requer investigação:**  
`[condição que disparou a análise e criticidade do ambiente]`

## 3. Observações verificáveis

| Horário com fuso | Fonte | Observação | Referência à evidência |
| --- | --- | --- | --- |
| `[horário]` | `[log/ferramenta]` | `[fato observado]` | `[caminho/ID/linha]` |

> Separe fatos observados de interpretações. Registre o fuso e mantenha referências verificáveis das evidências.

## 4. Hipóteses e correlação

**Hipótese principal:** `[explicação candidata]`  
**Hipóteses alternativas:** `[inclua possibilidade de atividade legítima]`

**Evidências a favor:**
- `[evidência e referência]`

**Evidências contrárias ou ausentes:**
- `[evidência ou lacuna]`

**Critério de correlação utilizado:** `[tempo, ativo, conta, processo, comunicação etc.]`

## 5. Observáveis e enriquecimento

| Tipo | Valor anonimizado | Fonte consultada | Resultado e ressalvas |
| --- | --- | --- | --- |
| `[IP/domínio/hash/etc.]` | `[valor]` | `[fonte permitida]` | `[resultado; confiabilidade]` |

**Proteção dos dados:** antes de consultar serviços externos, verifique se há autorização para compartilhar o observável.

## 6. Avaliação e decisão

**Criticidade do ativo:** `[baixa / média / alta / crítica + justificativa]`  
**Impacto observado ou potencial:** `[descrever]`  
**Grau de confiança da análise:** `[baixo / médio / alto + justificativa]`  
**Classificação provisória:** `[falso positivo / benigno esperado / suspeito inconclusivo / incidente confirmado / requer escalonamento]`  
**Prioridade de atendimento:** `[conforme política local]`

**Justificativa da classificação:**  
`[texto que conecta evidências, limitações e decisão]`

## 7. Ações e escalonamento

| Horário com fuso | Ação autorizada | Responsável | Resultado |
| --- | --- | --- | --- |
| `[horário]` | `[ação]` | `[pessoa/equipe]` | `[resultado]` |

**Escalonamento necessário?** `[sim / não; para quem e por quê]`  
**Ações pendentes:** `[o que ainda precisa ser verificado]`

## 8. Encerramento e lições aprendidas

**Conclusão fundamentada:** `[o que foi confirmado, descartado ou permaneceu inconclusivo]`

**Limitações da investigação:** `[logs ausentes, baixa retenção, ausência de telemetria etc.]`

**Recomendações:** `[melhoria de detecção, prevenção, processo ou comunicação]`

**Estado final:** `[encerrado / em acompanhamento / escalado]`  
**Data/hora de fechamento:** `[horário + fuso]`

---

**Uso previsto neste portfólio:** investigações **independentes** futuras, com dados de laboratório, sintéticos ou expressamente autorizados. Não representa uma investigação corporativa já executada.
