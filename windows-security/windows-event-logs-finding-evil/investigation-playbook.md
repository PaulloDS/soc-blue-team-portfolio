# Playbook de triagem: eventos de segurança do Windows

**Uso:** roteiro de estudo e laboratório. Não substitui os procedimentos e níveis de escalonamento de uma organização.

## 1. Escopo e preparação

Antes de investigar, identificar o hostname, o usuário relacionado ao alerta, a janela temporal e as fontes disponíveis. Anotar timezone, possíveis diferenças de relógio, política de auditoria e configuração do Sysmon.

Se os dados vierem de um arquivo EVTX, preservar o original, utilizar cópia e registrar origem, tamanho e hash quando houver processo de preservação de evidências.

## 2. Autenticação anômala

**Hipótese:** tentativas de adivinhação de credenciais ou uso indevido de uma identidade.

Fontes de interesse:

- Security 4625: falha de logon.
- Security 4624: sucesso de logon.
- Security 4672: privilégios especiais atribuídos ao novo logon, quando aplicável.

Procedimento:

1. Agrupar eventos de falha por usuário, IP e intervalo de tempo.
2. Diferenciar logon local, remoto, de rede e por serviço usando o campo LogonType.
3. Identificar sucesso relacionado, tendo cuidado com NAT, contas compartilhadas e saltos temporais.
4. Avaliar criticidade do host, identidade e origem.
5. Verificar eventos posteriores que possam confirmar ou enfraquecer a hipótese.

**Não concluir:** cinco falhas e um sucesso não comprovam comprometimento sem outras evidências.

## 3. Execução suspeita de processos

**Hipótese:** uma aplicação iniciou um processo que não corresponde ao comportamento esperado.

Fontes de interesse:

- Security 4688: criação de processo, quando a auditoria estiver habilitada.
- Sysmon 1: criação de processo, com ProcessGuid, ParentProcessGuid e CommandLine quando configurados.
- Sysmon 7: carregamento de imagem/DLL, dependendo das opções de coleta.
- Sysmon 3 e 22: rede e DNS, se disponíveis.

Procedimento:

1. Identificar o processo, pai, usuário, caminho e linha de comando.
2. Verificar se o processo foi iniciado legitimamente por instalação, atualização, script administrativo ou software autorizado.
3. Correlacionar conexões, arquivos escritos, DNS e processos descendentes.
4. Conferir diferenças entre nome, caminho e assinatura do binário. Um nome conhecido sozinho não garante benignidade.
5. Documentar hipótese, evidências, lacunas e justificativa para triagem ou escalonamento.

**Atenção:** PIDs são reutilizados. Prefira ProcessGuid e ParentProcessGuid quando Sysmon estiver disponível.

## 4. Exemplo de consulta com PowerShell

~~~powershell
$start = (Get-Date).AddHours(-12)
$filter = @{
    LogName = 'Security'
    Id = @(4624, 4625, 4688)
    StartTime = $start
}
Get-WinEvent -FilterHashtable $filter -MaxEvents 200 |
    Select-Object TimeCreated, Id, ProviderName, Message
~~~

Para explorar a estrutura XML sem depender de posições fixas:

~~~powershell
$event = Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    Id = 4688
} -MaxEvents 1

[xml]$xml = $event.ToXml()
foreach ($data in $xml.Event.EventData.Data) {
    '{0}: {1}' -f $data.Name, $data.InnerText
}
~~~

## 5. Registro da análise

| Campo | Conteúdo esperado |
| --- | --- |
| Identificador | Código interno do laboratório ou ticket |
| Período | Início e fim com timezone |
| Origem | Host, log, provider e arquivo de evidência |
| Hipótese | Atividade investigada, sem conclusão antecipada |
| Evidências | EventRecordID, EventID, hora, campos relevantes e capturas |
| Corroboração | Dados adicionais que sustentam ou contradizem a hipótese |
| Impacto | Ativos, contas e possíveis efeitos |
| Conclusão | Benigno, suspeito, confirmado ou inconclusivo, com justificativa |
| Encaminhamento | Monitorar, ajustar detecção, escalar ou resposta autorizada |

## 6. Quando escalar

O escalonamento pode ser necessário quando existem sinais corroborados de acesso não autorizado, execução com privilégios, persistência, acesso indevido a credenciais ou evidências de movimentação lateral.

Os procedimentos de contenção e coleta dependem da política da organização. Uma ação precipitada pode prejudicar uma investigação ou interromper serviços.

## 7. Melhorias para um laboratório independente

- Coletar eventos Security e Sysmon em uma VM Windows própria e isolada.
- Registrar o cenário e os comandos legítimos executados, sem alterar artificialmente os logs.
- Produzir buscas por Event ID, processo, identidade e intervalo.
- Construir linha do tempo e identificar os indicadores que ajudam a separar hipótese e conclusão.
- Exportar capturas dos resultados, omitindo qualquer dado sensível.
- Registrar limitações de coleta e causas de possíveis falsos positivos.

**Estado:** este playbook descreve uma metodologia proposta, não a conclusão de uma investigação independente já executada.
