# Windows Event Logs & Finding Evil

**HTB Academy | SOC Analyst Path | Módulo 03 concluído**

Este registro reúne meus estudos sobre investigação de eventos do Windows, Sysmon, Event Tracing for Windows (ETW) e análise com PowerShell. A intenção é consolidar um método de investigação, não decorar comandos ou reproduzir respostas de exercícios.

A principal ideia do módulo é simples: um Event ID indica o tipo de evento, mas a investigação depende de correlacionar **origem, usuário, processo, contexto, horário e comportamento**.

> **Escopo:** documentação técnica autoral de conceitos gerais. Este material não contém respostas, arquivos, flags nem capturas do Skills Assessment da HTB. O script deste repositório é um recurso de estudo reutilizável; não foi apresentado como ferramenta implantada em SOC corporativo.

## 1. Onde estão os eventos relevantes

| Canal / origem | O que investigar | Observação |
| --- | --- | --- |
| Windows Security | Autenticações, contas, privilégios e criação de processos, quando auditados | Depende da política de auditoria configurada |
| Windows System | Serviços, drivers e acontecimentos do sistema | Eventos devem ser interpretados com o contexto do provedor |
| Application | Falhas e atividade registrada por aplicações | A cobertura depende de cada aplicação |
| Microsoft-Windows-Sysmon/Operational | Telemetria de processos, conexões, módulos e DNS, conforme configuração | Sysmon precisa estar instalado e configurado |
| Microsoft-Windows-PowerShell/Operational | Telemetria operacional do PowerShell quando disponível | Registro avançado pode exigir políticas específicas |

## 2. Event IDs de referência

Os IDs abaixo não são uma lista universal de indicadores de comprometimento. Eles ajudam a direcionar a triagem e precisam ser considerados junto com o **canal e o provedor**.

| Fonte | ID | Significado | Pergunta investigativa |
| --- | --- | --- | --- |
| Security | 4624 | Autenticação bem-sucedida | O tipo de logon e a origem são esperados? |
| Security | 4625 | Falha de autenticação | Há volume, repetição ou distribuição anormal? |
| Security | 4672 | Privilégios especiais atribuídos ao logon | A identidade tem justificativa para privilégios elevados? |
| Security | 4688 | Novo processo criado | Quem iniciou o processo e qual era o comando? |
| Security | 1102 | Log de auditoria limpo | Houve ação administrativa legítima ou tentativa de apagar rastros? |
| Sysmon | 1 | Criação de processo | A relação entre processo pai, filho e argumentos é coerente? |
| Sysmon | 3 | Conexão de rede | O processo iniciou uma conexão inesperada? |
| Sysmon | 7 | Imagem ou DLL carregada | O caminho, assinatura e comportamento merecem investigação? |
| Sysmon | 11 | Arquivo criado | O processo gravou algo inesperado no disco? |
| Sysmon | 22 | Consulta DNS | Qual processo consultou o domínio e em qual contexto? |

**Atenção:** Sysmon ID 3 e ID 7 não devem ser tratados como disponíveis em todas as instalações; a coleta depende das regras/configuração, com possível impacto de volume. No evento 4688, o campo de linha de comando também depende de configuração de auditoria.

## 3. Processo de investigação que pretendo aplicar

1. Delimitar uma janela temporal e verificar se os horários estão no mesmo fuso.
2. Identificar o canal, o provedor e os IDs relevantes.
3. Consultar os eventos com filtros aplicados na origem, evitando carregar todo o log sem necessidade.
4. Ler o XML para acessar campos nomeados e entender o significado de cada registro.
5. Correlacionar identidade, processo, processo pai, host e demais observáveis.
6. Testar uma hipótese alternativa legítima antes de classificar uma anomalia como suspeita.
7. Registrar evidências, nível de confiança, lacunas e encaminhamento.

## 4. PowerShell para uma triagem inicial

Uma consulta eficiente combina filtro por log, ID e período:

~~~powershell
$filter = @{
    LogName   = 'Security'
    Id        = @(4624, 4625, 4688)
    StartTime = (Get-Date).AddHours(-24)
}

Get-WinEvent -FilterHashtable $filter -MaxEvents 100 |
    Select-Object TimeCreated, Id, ProviderName, MachineName, Message |
    Format-Table -Wrap
~~~

Para arquivos exportados:

~~~powershell
Get-WinEvent -FilterHashtable @{
    Path = 'C:\Laboratorio\security-sample.evtx'
    Id   = @(4624, 4625, 4688)
} | Select-Object TimeCreated, Id, Message
~~~

Os exemplos são genéricos. O arquivo EVTX deve existir, e os eventos só estarão disponíveis se forem gerados e coletados no ambiente. Executar como administrador pode ser necessário para ler canais protegidos.

### Como examinar campos do XML

~~~powershell
$event = Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    Id = 4688
} -MaxEvents 1

[xml]$xml = $event.ToXml()
$xml.Event.EventData.Data |
    Select-Object Name, '#text'
~~~

A análise por campos nomeados é mais robusta que procurar qualquer texto na propriedade \`Message\` ou depender de posições fixas no array de propriedades.

## 5. Anomalias entre processo pai e filho

Uma relação pai e filho atípica pode ser um sinal de execução indevida, mas não é evidência suficiente para confirmar um ataque.

Exemplo hipotético: um editor de documentos inicia um interpretador de comandos com argumentos incomuns. A análise exige verificar a linha de comando, o caminho do executável, a assinatura, o usuário, o horário, a frequência, a origem do arquivo e a presença de eventos correlatos.

No Sysmon, a identificação de processos por \`ProcessGuid\` e \`ParentProcessGuid\` facilita uma correlação mais estável do que usar apenas PID. Mesmo assim, retenção, regras de coleta e mudanças de processo podem limitar a investigação.

## 6. Sysmon e ETW não são a mesma coisa

O **ETW** é uma infraestrutura de instrumentação e emissão de eventos do Windows, que conecta produtores, sessões e consumidores de telemetria.

O **Sysmon** fornece eventos específicos sobre atividade do sistema, registra parte desses dados em seu canal próprio e oferece recursos de configuração de coleta. Event Viewer e \`Get-WinEvent\` são meios de consultar eventos já registrados; nenhum deles substitui, por si só, a configuração da telemetria.

## 7. Materiais do portfólio

| Arquivo | Finalidade |
| --- | --- |
| [triage-windows-events.ps1](triage-windows-events.ps1) | Script de apoio para ler eventos de um canal ou arquivo EVTX e extrair campos relevantes |
| [investigation-playbook.md](investigation-playbook.md) | Playbook de análise de autenticações, criação de processos e módulos carregados |

O script é um **exemplo autoral de estudo**, não uma ferramenta cuja execução foi validada nesta conversa. Testes e capturas de um laboratório Windows independente serão adicionados somente após a execução.

## 8. Relação com os projetos anteriores

No [SIEM Brute Force Detection Lab](../../siem/siem-bruteforce-lab/), explorei regras e lógica de detecção em Elastic Stack. O conteúdo de Windows Event Logs complementa esse trabalho com compreensão das fontes de dados, das limitações de auditoria e da correlação de processos em endpoints.

O objetivo do próximo laboratório é coletar eventos reais de uma VM Windows autorizada, validar uma hipótese de detecção e documentar capturas no próprio README, com o contexto necessário.

## Referências

- [HTB Academy: Windows Event Logs & Finding Evil](https://academy.hackthebox.com/course/preview/windows-event-logs--finding-evil)
- [Microsoft Learn: Get-WinEvent](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent)
- [Microsoft Learn: Sysmon Events](https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/sysmon-events)
- [Microsoft Learn: Windows Security Event 4688](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4688)
- [HTB: diretrizes de publicação](https://help.hackthebox.com/en/articles/5188925-streaming-writeups-walkthrough-guidelines)
