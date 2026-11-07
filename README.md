# SOC & Blue Team — Portfólio de Estudos

**Formação contínua em operações de segurança, análise de alertas e resposta a incidentes.**

Este repositório reúne **anotações técnicas autorais**, modelos de trabalho e, futuramente, **laboratórios independentes** desenvolvidos durante minha evolução em segurança defensiva.

Sou graduado em **Engenharia de Software** e concluí o **Web Penetration Tester Job Role Path** da HTB Academy. Agora amplio minha formação com o **SOC Analyst Job Role Path**, conectando a compreensão de técnicas ofensivas à investigação e à detecção de atividades suspeitas.

> **Escopo e transparência:** materiais de estudo não representam experiência profissional em um SOC. Os laboratórios futuros serão identificados como simulações independentes. Este repositório **não contém soluções, respostas ou spoilers** de avaliações ativas da Hack The Box.

## Trilha SOC Analyst — acompanhamento

| Etapa | Módulo | Situação | Registro público |
| --- | --- | --- | --- |
| 01 | Incident Handling Process | **Concluído — Skills Assessment realizado** | [Fundamentos de Incident Handling](case-studies/01-incident-handling-process) |
| 02 | Security Monitoring & SIEM Fundamentals | **Concluído** | [SIEM Brute Force Detection Lab](siem/siem-bruteforce-lab/) |

Os demais módulos serão incorporados conforme o avanço da formação. Nem todo módulo dará origem a uma publicação: **a prioridade é o valor técnico e a qualidade da documentação**, não a quantidade de arquivos.

## Conteúdo disponível

- **[Incident Handling Process — fundamentos](case-studies/01-incident-handling-process/fundamentos.md):** eventos, alertas, incidentes, etapas da resposta, triagem, correlação, enriquecimento e diferenças entre modelos do NIST.
- **[Template de triagem de alertas](case-studies/01-incident-handling-process/template.md):** estrutura autoral para registrar hipóteses, evidências, severidade, ações e encaminhamentos em investigações futuras.
- **[SIEM Brute Force Detection Lab](siem/siem-bruteforce-lab/):** Elastic Stack com Docker, geração de eventos sintéticos, regras de detecção, consultas KQL, testes e fluxo opcional de ataque SSH em laboratório controlado. [Limitações e evidências](siem/siem-bruteforce-lab/docs/limitations.md).
- **[HTB Sherlock — Brutus | Investigação DFIR](dfir/sherlock-brutus/):** reconstrução do comprometimento Linux por SSH com `auth.log` e `wtmp`, hipóteses de detecção, MITRE ATT&CK e guia para anexar evidências pessoais. Estudo de caso de Sherlock aposentado; capturas da resolução pessoal pendentes.

## Competências em desenvolvimento

`Incident Response` · `Alert Triage` · `Case Management` · `TheHive` · `Network Security` · `Log Analysis` · `Elastic Stack (laboratório)` · `KQL` · `Detection Engineering (laboratório)` · `Linux Forensics (Sherlock)`

A ferramenta **TheHive** foi utilizada em ambiente de avaliação da HTB no módulo *Incident Handling Process*. A documentação aqui publicada descreve princípios gerais e referências públicas; **não reproduz o cenário nem o passo a passo do assessment**.

## Como leio uma investigação

Um alerta é um ponto de partida, não uma conclusão. Antes de classificá-lo, procuro distinguir:

1. **Observações:** o que as fontes de dados efetivamente registraram;
2. **Hipóteses:** quais interpretações podem explicar os eventos;
3. **Corroboração:** que evidências adicionais sustentam ou refutam cada hipótese;
4. **Decisão:** quais ações são justificadas pelo contexto, impacto e grau de confiança.

## Próximas entregas propostas

- Ampliar a coleta de telemetria real com Windows Event Logs / Sysmon;
- Versionar evidências locais do Kibana, distinguindo testes Python e alertas do mecanismo de detecção;
- Investigar novos cenários e produzir relatórios baseados em logs próprios de laboratório.

Essas entregas estão **planejadas, não realizadas**; serão publicadas somente após execução e revisão técnica.

## Contato

- [LinkedIn](https://www.linkedin.com/in/paulo-douglas/)
- [Perfil no GitHub](https://github.com/PaulloDS)

---

**Nota de integridade:** as referências à HTB Academy identificam a origem da formação. Nenhum conteúdo deste repositório deve ser interpretado como resposta de exercícios, walkthrough de avaliação, ou certificação profissional obtida por exame.
