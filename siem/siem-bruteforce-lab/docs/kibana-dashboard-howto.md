# Construir uma visualização no Kibana (passo a passo manual)

Feito manualmente de propósito — monte do zero no seu Kibana e tire os prints enquanto
constrói; isso também é "mostrar que sabe usar o Kibana", não só o produto final.

Pré-requisito: `./lab.sh demo` já rodado (ou `run_attack.sh` para dados reais).

## 1. Gráfico de barras: falhas de login por origem ao longo do tempo
1. Menu ☰ > **Visualize Library** > **Create visualization** > **Lens**
2. Em **Data view**, selecione `lab-winlogs`
3. Arraste `@timestamp` para o eixo horizontal (ele vira automático um histograma de tempo)
4. Em **Break down by**, adicione `source.ip` (Top 5 values)
5. No filtro de busca no topo, digite: `event.category:authentication and event.outcome:failure`
6. Troque o tipo do gráfico para **Bar vertical stacked** (menu de sugestões à direita)
7. Título: "Falhas de autenticação por origem" > **Save**

## 2. Tabela: top contas atacadas
1. Novo Lens > Data view `lab-winlogs`
2. Tipo: **Data table**
3. Linhas: `user.name` (Top 10 values) — métrica: **Count**
4. Filtro: `event.outcome:failure`
5. Ordene por Count decrescente
6. Salvar como "Top contas com falha de login"

## 3. Métrica: total de alertas por regra (se o motor de detecção estiver ativo)
1. Menu ☰ > **Security > Alerts**
2. Use os filtros de `kibana.alert.rule.name` para comparar a regra tunada x sem tuning
3. Print dessa tela já serve como evidência "antes/depois do tuning"

## 4. Montar o Dashboard
1. Menu ☰ > **Dashboard** > **Create dashboard**
2. **Add from library** > adicione os dois Lens salvos acima
3. Redimensione lado a lado, ajuste o intervalo de tempo para a janela do seu teste
4. Salve como "SIEM Lab - Brute Force & Spraying"
5. **Share > Export** ou apenas print da tela cheia (F11 para modo tela cheia antes do print)

## Exportar o dashboard para o repositório (opcional, mas profissional)
1. Menu ☰ > **Stack Management > Saved Objects**
2. Marque o dashboard e os dois Lens > **Export**
3. Salve o `.ndjson` em `kibana/dashboard-export.ndjson` no repositório
4. Documente no README como importar: Saved Objects > Import
