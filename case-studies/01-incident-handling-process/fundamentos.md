# 01 — Incident Handling Process

**Área:** SOC / Incident Response  
**Formação associada:** HTB Academy — SOC Analyst Job Role Path  
**Situação:** módulo concluído; Skills Assessment realizado em ambiente TheHive  
**Tipo de publicação:** síntese técnica autoral, **não** um write-up de assessment

## 1. Objetivo do estudo

Compreender como um time de segurança organiza a resposta a eventos potencialmente maliciosos: identificar sinais, estabelecer contexto, analisar evidências, priorizar decisões, encaminhar ações e aprender com a ocorrência.

**Aprendizado central:** detectar uma anomalia não equivale a confirmar um incidente. A qualidade da investigação depende do contexto disponível, da confiabilidade das fontes e da distinção entre fatos, hipóteses e conclusões.

## 2. Evento, alerta e incidente: não são sinônimos

| Termo | Interpretação operacional | Exemplo genérico |
| --- | --- | --- |
| **Evento** | Ocorrência observável registrada por um sistema ou serviço. | Uma tentativa de autenticação falha registrada em log. |
| **Alerta** | Sinal produzido por regra, ferramenta ou analista de que algo merece avaliação. | Múltiplas falhas de login em curto intervalo acionam uma regra de monitoramento. |
| **Incidente de segurança** | Ocorrência que compromete ou coloca em risco sistemas, dados ou operações conforme critérios da organização. | Evidências correlacionadas confirmam uso não autorizado de uma conta. |

Uma mesma regra pode produzir falsos positivos; também é possível que um incidente não seja imediatamente detectado por regras existentes.

## 3. O ciclo clássico de tratamento de incidentes

Uma forma tradicional de estudar *incident handling* é organizar o processo nas seguintes etapas:

### 3.1 Preparação

- Definir responsabilidades, contatos de escalonamento, critérios de severidade e procedimentos.
- Disponibilizar fontes de logs, monitoramento, inventário e meios de preservar evidências.
- Exercitar a comunicação e a coordenação entre segurança, infraestrutura, gestores e outros responsáveis.

**Pergunta orientadora:** quem faz o quê quando um alerta importante chega?

### 3.2 Detecção e análise

- Identificar o sinal inicial e registrar quando foi observado.
- Verificar a origem, a integridade e as limitações das evidências.
- Correlacionar entidades, horários, ativos, contas e eventos relacionados.
- Registrar hipóteses, nível de confiança e lacunas de visibilidade.
- Diferenciar um falso positivo, uma ocorrência suspeita inconclusiva e um incidente confirmado.

**Pergunta orientadora:** quais dados corroboram ou contradizem a hipótese inicial?

### 3.3 Contenção

Medidas para reduzir a exposição ou o impacto, considerando a urgência, a continuidade do negócio e o risco de perder evidências. Exemplos possíveis, sujeitos a autorização e procedimento interno: isolar endpoint, revogar sessões ou bloquear comunicação suspeita.

**Pergunta orientadora:** qual medida reduz o risco sem criar dano operacional desnecessário?

### 3.4 Erradicação

Tratar a causa identificada: remover persistência maliciosa, corrigir configurações, atualizar sistemas, redefinir credenciais comprometidas e verificar se ainda existem sinais do vetor original.

**Pergunta orientadora:** eliminamos apenas um sintoma ou a causa comprovada?

### 3.5 Recuperação

Restaurar serviços com validações de integridade, monitoramento reforçado e critérios definidos para retorno à operação normal.

**Pergunta orientadora:** que evidência demonstra que a recuperação foi bem-sucedida?

### 3.6 Atividades pós-incidente

Produzir relatório, consolidar linha do tempo, registrar decisões e dificuldades, identificar falhas de processo ou visibilidade e definir melhorias verificáveis.

**Pergunta orientadora:** o que mudará para evitar ou detectar mais cedo uma situação semelhante?

> **Nota sobre o NIST:** a sequência acima é uma apresentação didática do ciclo clássico, associada à abordagem anterior da NIST SP 800-61 Rev. 2. A **SP 800-61 Rev. 3 (2025)** substituiu a revisão anterior e enfatiza resposta integrada à gestão de riscos e às funções do **NIST CSF 2.0**. No modelo atual, a preparação envolve *Govern, Identify e Protect*; a resposta abrange *Detect, Respond e Recover*, com melhoria contínua. Não se deve apresentar as seis etapas acima como se fossem a estrutura oficial da Rev. 3. [Fonte: NIST](https://csrc.nist.gov/projects/incident-response).

## 4. Triage: um método de raciocínio

Um fluxo de triagem aplicável a diversos tipos de alerta pode ser organizado assim:

1. **Registrar:** origem do alerta, data/hora com fuso, regra responsável, descrição e ativo afetado.
2. **Verificar qualidade:** há campos ausentes? O evento se repetiu? A fonte de log é confiável?
3. **Contextualizar:** qual a importância do ativo e da conta? Existe mudança autorizada que explique o comportamento?
4. **Correlacionar:** existem alertas relacionados, eventos anteriores/posteriores, outras máquinas ou identidades envolvidas?
5. **Enriquecer:** analisar observáveis (como IP, domínio, hash e usuário) em fontes permitidas pela política de dados.
6. **Classificar:** registrar hipóteses, nível de confiança, severidade/impacto e justificativa da decisão.
7. **Encaminhar:** documentar conclusão, escalonamento ou necessidade de investigação complementar.

**Severidade e prioridade não são idênticas.** A severidade representa o impacto potencial/confirmado segundo critérios definidos; a prioridade de atendimento pode depender também de urgência, criticidade do ativo e requisitos operacionais.

### Perguntas práticas que ajudam a evitar conclusões prematuras

- O evento é realmente anômalo para esse usuário, sistema e horário?
- O endereço de origem representa um host individual, um proxy, VPN ou infraestrutura compartilhada?
- Qual é a janela de tempo analisada? Estamos comparando horários com o mesmo fuso?
- Existem sinais adicionais além de uma única regra disparada?
- Há elementos suficientes para escalar como possível incidente? Quais são as incertezas?

## 5. Case Management e TheHive

Ferramentas de gerenciamento de incidentes, como **TheHive**, ajudam a organizar o trabalho investigativo. Na documentação oficial do TheHive, alertas podem conter observáveis (IPs, domínios, hashes etc.), TTPs, anexos e comentários, e podem ser associados a casos quando a investigação exige continuidade.

**Conceitos operacionais:**

- **Alert:** item de monitoramento que precisa de triagem;
- **Observable:** dado associado à investigação; não é automaticamente um indicador confirmado de comprometimento;
- **Case:** investigação organizada que pode reunir alertas relacionados, tarefas, observáveis e resultados;
- **Enrichment:** adição de contexto útil sobre um observável, respeitando a confidencialidade;
- **Correlation:** relacionamento fundamentado entre eventos ou alertas que compartilham contexto relevante.

Uma correlação temporal isolada não comprova causalidade. A documentação deve indicar **por que** dois eventos foram relacionados.

### Aprendizado prático do assessment

No módulo, utilizei o **TheHive em um Skills Assessment**, com atividades de triagem e organização de alertas. O aprendizado que registro publicamente é **o processo de raciocínio e documentação** — não os artefatos, respostas, caminhos ou dados do cenário de avaliação.

## 6. Registro de investigação: exemplo de estrutura, não de resultado

Para um alerta futuro, a anotação deve permitir que outro analista compreenda as decisões sem repetir toda a investigação:

| Campo | O que registrar |
| --- | --- |
| Contexto | Fonte, ativo, conta, horário e regra de detecção |
| Observações | Evidências objetivas extraídas das fontes disponíveis |
| Hipóteses | Possíveis explicações, incluindo alternativas benignas |
| Correlação | Eventos relacionados e critério usado para associá-los |
| Avaliação | Impacto, criticidade, confiança e limitações |
| Decisão | Falso positivo, inconclusivo, incidente ou escalonamento, conforme critérios locais |
| Ações | Responsável, horário, justificativa e resultado |
| Próximos passos | Evidências ainda necessárias, acompanhamento ou encerramento |

**Recurso reutilizável:** [modelo de triagem de alertas](../triagem-de-alerta.md).

## 7. Relação entre segurança ofensiva e defensiva

A formação ofensiva ajuda a compreender ações que um invasor pode executar; a investigação defensiva exige identificar **quais vestígios essas ações deixam nas fontes realmente disponíveis**.

Uma técnica conhecida não garante um sinal inequívoco nos logs. Cobertura de telemetria, configurações, retenção, contexto e comportamento legítimo dos usuários influenciam a capacidade de detectar um ataque.

Esta é uma mudança de perspectiva: de **“como uma falha pode ser explorada?”** para **“que evidências permitiriam suspeitar, confirmar, dimensionar e responder a um possível comprometimento?”**

## 8. Limitações e próximos passos

- Este arquivo contém **conceitos e reflexão**, não um relatório de incidente real.
- O Skills Assessment foi realizado, mas **a solução não é reproduzida**.
- Ainda não há aqui coleta independente de logs nem execução de um estudo de caso próprio.
- Próximo objetivo: aprofundar SIEM, consultas e investigação de eventos em um ambiente controlado com dados autorais.
