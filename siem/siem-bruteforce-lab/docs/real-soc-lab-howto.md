# Laboratório SOC real: sua própria VM atacada e monitorada ao vivo

Isso é diferente de tudo que vimos até aqui. Aqui não tem gerador de eventos nem
container fazendo o papel de vítima: você sobe uma **VM de verdade**, instala um
**agente de coleta de logs de verdade** (Filebeat ou Winlogbeat), ataca essa VM com
**Hydra/NetExec de verdade**, e os alertas aparecem no Kibana porque o SO da vítima
realmente registrou a tentativa de login. É o mais próximo de um SOC real que dá
para montar em um notebook.

> **Estado da validação:** este documento é um roteiro de implantação para um ambiente independente com VM. O repositório apresenta código e testes de lógica, mas não contém logs brutos de execução da VM nem capturas locais versionadas que demonstrem o disparo de alertas. Não confunda instruções de execução com resultados já verificados.

## Topologia
```
[VM Vítima]  <--- ataque real (SSH/RDP/SMB) ---  [VM/host Atacante: Kali ou seu Linux]
     |
     | Filebeat / Winlogbeat envia os logs reais
     v
[Elastic Stack]  <-- já está pronto: docker compose up (deste repositório)
  Elasticsearch + Kibana
```
As 3 pontas podem ser: (a) 3 VMs separadas, (b) a Vítima em VM e o Atacante no seu
host, ou (c) tudo em VMs e o Elastic Stack rodando no seu host (mais simples, porque
você já tem o `docker-compose.yml` deste projeto).

**Rede: use sempre rede isolada (Host-only / Internal Network) da sua ferramenta de
virtualização (VirtualBox: "Host-only Adapter"; VMware: "Host-only"). Nunca ataque uma
máquina na sua rede real, nunca exponha a VM vítima à internet.**

## Requisitos
- VirtualBox ou VMware (gratuitos)
- Uma VM "vítima": Linux (Ubuntu Server, leve) **ou** Windows (10/11/Server, mais pesado — precisa de 4 GB de RAM só para ela)
- Kali Linux (VM ou o seu host, se já tiver `hydra`/`netexec` instalados) como atacante
- O Elastic Stack deste repositório rodando no seu host (`./lab.sh up && ./lab.sh wait`)
- RAM livre: ~4 GB para o Elastic Stack + 2-4 GB por VM

---

## Caminho A — Vítima Linux + Filebeat (mais rápido, recomendado para começar)

### A.1 Preparar a VM vítima
Ubuntu Server (ou qualquer distro) em rede Host-only. Anote o IP dela (`ip a`).
Crie um usuário fraco só para o lab:
```bash
sudo useradd -m labuser && sudo passwd labuser   # defina "123456" de propósito
```

### A.2 Deixar o Elastic Stack acessível pela rede do lab
No seu host, descubra o IP da interface Host-only (ex.: `192.168.56.1`):
```bash
ip a   # Linux          |   ipconfig   # Windows
```
Teste de dentro da VM vítima:
```bash
curl -u elastic:SUASENHA http://192.168.56.1:9200
```
Por segurança, o `docker-compose.yml` publica a porta 9200 **somente em 127.0.0.1 por padrão**. Para acesso da VM, configure no `.env` o IP **exato** da interface Host-only do host, por exemplo `ES_BIND_IP=192.168.56.1`, e reinicie a stack com `docker compose up -d`. Se precisar usar Kibana diretamente pela VM, configure também `KIBANA_BIND_IP=192.168.56.1`. Mantenha firewall limitado à rede do laboratório; não use `0.0.0.0`, Bridged nem IP público. A VM deve conseguir acessar a interface Host-only.

### A.3 Instalar e configurar o Filebeat na vítima
```bash
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.15.3-amd64.deb
sudo dpkg -i filebeat-8.15.3-amd64.deb   # use a MESMA versão do STACK_VERSION do .env
sudo filebeat modules enable system
```
Edite `/etc/filebeat/filebeat.yml`:
```yaml
output.elasticsearch:
  hosts: ["http://192.168.56.1:9200"]   # IP do seu host (Host-only)
  username: "elastic"
  password: "SUASENHA"                   # a do seu .env
  ssl.verification_mode: "none"          # TLS está desabilitado no docker-compose deste lab
setup.kibana:
  host: "http://192.168.56.1:5601"
```
Carrega os templates, pipelines e dashboards padrão do Elastic e inicia:
```bash
sudo filebeat setup -e
sudo systemctl enable --now filebeat
```
Confirme que o SSH está logando de verdade: `sudo tail -f /var/log/auth.log` enquanto
você tenta um login errado de outro terminal.

---

## Caminho B — Vítima Windows + Winlogbeat (mais próximo de ambiente corporativo)

### B.1 VM Windows em rede Host-only
Crie um usuário local fraco (Painel de Controle > Contas, senha simples de propósito).
Habilite RDP (Configurações > Sistema > Área de Trabalho Remota) **ou** deixe o
compartilhamento de arquivos (SMB) padrão ligado — qualquer um serve como vetor.

### B.2 Instalar e configurar o Winlogbeat
Baixe o Winlogbeat **na mesma versão do `.env`** (`STACK_VERSION`) em
`https://www.elastic.co/downloads/beats/winlogbeat`, extraia e, via PowerShell
(administrador):
```powershell
cd 'C:\Program Files\Winlogbeat'
.\install-service-winlogbeat.ps1
```
Edite `winlogbeat.yml`:
```yaml
winlogbeat.event_logs:
  - name: Security
output.elasticsearch:
  hosts: ["http://192.168.56.1:9200"]
  username: "elastic"
  password: "SUASENHA"
  ssl.verification_mode: "none"
setup.kibana:
  host: "http://192.168.56.1:5601"
```
```powershell
.\winlogbeat.exe setup -e
Start-Service winlogbeat
```

---

## Atacar de verdade

Rode isso do Kali (ou do seu host com as ferramentas instaladas), apontando para o
**IP da VM vítima** (não para o Elastic!):

**SSH (vítima Linux):**
```bash
hydra -l labuser -P /usr/share/wordlists/rockyou.txt -t 4 ssh://<IP-DA-VITIMA>
```

**RDP (vítima Windows):**
```bash
hydra -l labuser -P /usr/share/wordlists/rockyou.txt rdp://<IP-DA-VITIMA>
```

**SMB (vítima Windows, alternativa mais estável que RDP via Hydra):**
```bash
# ferramenta moderna (sucessora do crackmapexec)
nxc smb <IP-DA-VITIMA> -u labuser -p /usr/share/wordlists/rockyou.txt
```
Use uma wordlist curta e coloque a senha certa perto do meio, para ter várias falhas
antes do sucesso (é o padrão que a regra de sequência foi feita para detectar). Crie
a sua: `head -50 /usr/share/wordlists/rockyou.txt > senhas-lab.txt` e injete a senha
real do `labuser` na linha ~10.

## Confirmar no Kibana
1. **Discover**: crie/selecione a data view `filebeat-*` (Linux) ou `winlogbeat-*`
   (Windows). Filtro: `event.category:authentication and event.outcome:failure`
2. Deve aparecer o IP real do seu Kali/atacante e o usuário `labuser`, em tempo real
3. Se os campos vierem diferentes do esperado (nome de campo varia um pouco entre
   versões), ajuste a query antes de importar as regras — é rápido de conferir no Discover

## Apontar as regras de detecção para os dados reais
```bash
python3 detections/build_rules_real.py     # gera detections/rules/real_lab_rules.ndjson
```
Importe no Kibana: **Security > Rules > Import** (ou `curl` como no `lab.sh rules`, trocando
o arquivo para `real_lab_rules.ndjson`). As 4 regras são as mesmas de antes (limiar, spraying,
sequência, tunada x sem tuning), só que lendo `filebeat-*`/`winlogbeat-*` em vez do índice
sintético.

## Dashboard, validação e alertas
Siga `docs/kibana-dashboard-howto.md` utilizando a data view de telemetria real (`filebeat-*` ou `winlogbeat-*`). **Security > Alerts** só deverá mostrar um alerta se a regra estiver corretamente importada, habilitada, licenciada quando necessário, compatível com o esquema ECS real e executada durante a janela dos eventos.

Ao executar, registre: logs originais, mapeamento ECS, horário/fuso, ID e resultado de execução da regra, evidência do alerta (ou da ausência dele), e limitações. Anexe capturas locais sanitizadas em `docs/img/` e identifique a origem dos dados. Não descreva como comprovado algo que ainda não esteja documentado.

## Isolamento e segurança (não pule isso)
- Rede **Host-only/Internal** nas VMs — nunca Bridged, nunca exponha à internet
- Senha fraca só na conta de lab (`labuser`), nunca na sua conta real
- Desligue a VM vítima quando terminar de gravar a demo
- Isso é um laboratório seu, contra sua própria infraestrutura. Nunca aponte essas
  mesmas ferramentas para qualquer sistema que não seja seu ou que você não tenha
  autorização explícita para testar.

## Troubleshooting
| Sintoma | Causa provável |
|---|---|
| Filebeat/Winlogbeat não conecta no 9200 | firewall do host, ou a VM não está na mesma rede Host-only |
| `setup -e` falha com erro de template | versão do Beat diferente da versão do Elastic no `.env` |
| Discover sem nenhum dado | confira `systemctl status filebeat` / `Get-Service winlogbeat`; veja os logs em `/var/log/filebeat/` ou `C:\ProgramData\winlogbeat\Logs` |
| Hydra/nxc não encontra a senha | a senha real não está na wordlist, ou o RDP tem bloqueio de tentativas (normal no Windows); troque para SMB |
| Regras não disparam | confirme os nomes reais dos campos no Discover e ajuste `detections/build_rules_real.py` se necessário |
