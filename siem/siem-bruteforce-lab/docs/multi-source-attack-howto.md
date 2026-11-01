# Deixar o dashboard mais alimentado: vários IPs e vários tipos de alerta

Isto estende o `docs/real-soc-lab-howto.md`. É para depois que você já validou o
ataque simples (passo 7 do roteiro) e quer um dashboard com mais variedade: vários
IPs de origem, um ataque de brute force, um de spraying e o "ruído" de falso
positivo rodando ao mesmo tempo.

## Como funciona
Em vez de várias VMs, o próprio atacante (Kali ou seu host Linux) ganha **IPs
secundários de verdade** na mesma interface de rede. Cada "perfil" de ataque sai
por um IP diferente, dentro da mesma rede Host-only — tráfego real, capturado de
verdade pelo Filebeat/Winlogbeat na vítima.

## 1. Adicionar os IPs de origem (no atacante)
```bash
ip a                                             # confira o nome da sua interface (ex.: eth0)
sudo ./scripts/attack/add_ips.sh eth0 192.168.56.200 3
```
Isso cria `192.168.56.200`, `.201` e `.202` na sua máquina atacante.

## 2. Instalar o paramiko (só no atacante)
```bash
pip install paramiko --break-system-packages
```

## 3. Editar a campanha
Copie `scripts/attack/campaign.example.json` e ajuste os IPs para os que você
criou e o usuário/senha reais do seu `labuser`:
```bash
cp scripts/attack/campaign.example.json scripts/attack/campaign.json
nano scripts/attack/campaign.json
```
Três perfis prontos, cada um exercitando uma regra diferente:

| Perfil | O que faz | Regra que deveria disparar |
|---|---|---|
| `bruteforce` | várias senhas contra 1 conta, termina com a senha certa | Limiar + Sequência |
| `spray` | poucas tentativas contra várias contas, 1 IP | Spraying |
| `noise` | 1 falha a cada ~45s, indefinidamente, numa conta tipo `svc_backup` | Dispara na regra SEM tuning; é o análogo real do falso positivo |

## 4. Ver o plano antes de atacar de verdade
```bash
python3 scripts/attack/multi_attack.py --target 192.168.56.101 --config scripts/attack/campaign.json --dry-run
```
Confira os IPs e as contas antes de mandar de verdade.

## 5. Atacar de verdade
```bash
python3 scripts/attack/multi_attack.py --target 192.168.56.101 --config scripts/attack/campaign.json
```
O perfil `noise` fica rodando por `count × interval` segundos (no exemplo, 15 × 45s
≈ 11 min) — deixe em um terminal separado enquanto você explora o Kibana.

## 6. Repetir com mais variedade
Rode de novo mudando `campaign.json`: mais perfis `bruteforce` contra outras
contas, outros IPs (`add_ips.sh eth0 192.168.56.210 3` para mais 3), horários
diferentes. Cada rodada nova alimenta mais o dashboard com dados reais.

## 7. Ver no Kibana
No Discover (`filebeat-*` ou `winlogbeat-*`), agora `source.ip` tem 3+ valores
distintos. No gráfico de barras de `docs/kibana-dashboard-howto.md`, você já
deve ver as barras separadas por origem. Em **Security > Alerts**, espere
aparecer os 3 tipos: limiar, sequência e spraying — e, se importar a regra
"SEM tuning" (desabilitada por padrão), o ruído do perfil `noise` também.

## Limpeza
```bash
sudo ip addr del 192.168.56.200/24 dev eth0   # repita para cada IP criado
```
(o `add_ips.sh` já imprime os comandos exatos de remoção ao final)

## O que eu não validei
A execução real (`run_attempt`, que usa `paramiko` e `socket.bind` no IP de
origem) depende de uma vítima SSH de verdade na rede — não tenho isso neste
sandbox. O que testei e está garantido: a lógica do plano de ataque (quantas
tentativas, de que IP, em que ordem) em `tests/test_multi_attack.py`.
