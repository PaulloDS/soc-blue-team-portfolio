<#
.SYNOPSIS
    Consulta eventos Windows em um canal local ou arquivo EVTX.
.DESCRIPTION
    Exemplo de estudo para revisão de logs de autenticação e criação de processo.
    Emite objetos com campos básicos e EventData nomeado, sem fazer classificações de ataque.
    Requer Windows PowerShell 5.1+ ou PowerShell em Windows com Get-WinEvent.
.EXAMPLE
    .\triage-windows-events.ps1 -LogName Security -Ids 4624,4625,4688 -Hours 24 -MaxEvents 100
.EXAMPLE
    .\triage-windows-events.ps1 -EvtxPath 'C:\Labs\security.evtx' -Ids 4688 -MaxEvents 50 |
        Export-Csv .\eventos.csv -NoTypeInformation -Encoding UTF8
#>

[CmdletBinding(DefaultParameterSetName = 'Channel')]
param(
    [Parameter(Mandatory = $false, ParameterSetName = 'Channel')]
    [ValidateNotNullOrEmpty()]
    [string]$LogName = 'Security',

    [Parameter(Mandatory = $true, ParameterSetName = 'File')]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string]$EvtxPath,

    [Parameter(Mandatory = $false)]
    [ValidateCount(1, 50)]
    [int[]]$Ids = @(4624, 4625, 4688),

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 168)]
    [int]$Hours = 24,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 10000)]
    [int]$MaxEvents = 200
)

$filter = @{ Id = $Ids }
if ($PSCmdlet.ParameterSetName -eq 'File') {
    $filter.Path = (Resolve-Path -LiteralPath $EvtxPath).ProviderPath
}
else {
    $filter.LogName = $LogName
    $filter.StartTime = (Get-Date).AddHours(-$Hours)
}

try {
    $events = @(Get-WinEvent -FilterHashtable $filter -MaxEvents $MaxEvents -ErrorAction Stop)
}
catch {
    Write-Error "Nao foi possivel consultar os eventos. Verifique permissao, canal/arquivo e filtros. Detalhe: $($_.Exception.Message)"
    return
}

foreach ($event in $events) {
    $eventData = @{}
    try {
        [xml]$eventXml = $event.ToXml()
        $dataNodes = @($eventXml.Event.EventData.Data)
        foreach ($node in $dataNodes) {
            if ($null -ne $node -and -not [string]::IsNullOrWhiteSpace($node.Name)) {
                $eventData[$node.Name] = $node.InnerText
            }
        }
    }
    catch {
        Write-Verbose "Nao foi possivel analisar XML do registro $($event.RecordId): $($_.Exception.Message)"
    }

    $eventDataJson = if ($eventData.Count -gt 0) {
        $eventData | ConvertTo-Json -Compress -Depth 4
    } else {
        '{}'
    }

    [pscustomobject]@{
        TimeCreated  = $event.TimeCreated
        EventId      = $event.Id
        ProviderName = $event.ProviderName
        MachineName  = $event.MachineName
        RecordId     = $event.RecordId
        ProcessName  = $eventData['NewProcessName']
        ParentName   = $eventData['ParentProcessName']
        TargetUser   = $eventData['TargetUserName']
        IpAddress    = $eventData['IpAddress']
        LogonType    = $eventData['LogonType']
        EventData    = $eventDataJson
    }
}
