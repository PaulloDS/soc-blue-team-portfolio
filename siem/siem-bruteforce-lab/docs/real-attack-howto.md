# Ataque de verdade contra o lab (opcional, mas é o que mais impressiona no vídeo)

Até aqui os dados vêm de um gerador (`generator/`). Esta parte é diferente: sobe um
**SSH real** com senha fraca de propósito, ataca de verdade com **Hydra** e ingere os
**logs reais** que o SSH gerou — não é simulação de simulação.

**Isolamento:** o alvo só existe dentro da rede do Docker Compose, não é exposto fora do
seu host, e só sobe com `--profile attack` (nunca com `./lab.sh up` normal). É só para
o seu laboratório local.

## Pré-requisito
Hydra instalado. No Kali já vem. Em Ubuntu/Debian: `sudo apt install hydra`.

## Passo a passo
```bash
./lab.sh up && ./lab.sh wait && ./lab.sh demo   # se ainda não tiver feito
./scripts/attack/run_attack.sh
```
O script:
1. builda e sobe o container `attack-target` (Ubuntu + OpenSSH, usuário `labuser`, senha `123456` — proposital e documentada)
2. roda `hydra -L userlist.txt -P wordlist.txt -t 4 -f -s 2222 ssh://127.0.0.1`
3. captura `docker compose logs attack-target --timestamps` (o log real do sshd)
4. converte para o mesmo formato ECS do lab (`scripts/attack/parse_sshd_log.py`)
5. ingere no mesmo índice `lab-winlogs`, marcado com `lab.scenario:real_attack`

O resultado do Hydra pode variar (ele usa múltiplas threads, a ordem das tentativas não é
100% determinística). O que importa para o lab: **várias falhas reais seguidas de um
possível sucesso**, exatamente o padrão que a regra de sequência foi feita para pegar.

## Ver no Kibana
- Discover: `lab.scenario:real_attack` — IPs, portas de origem e usuários são os que o Hydra realmente usou
- Security > Alerts: se a wordlist acertou a senha, a regra de sequência deve disparar
- Compare com `source.ip:"203.0.113.45"` (ataque sintético) — mesma lógica, origem diferente

## Encerrar o alvo
```bash
docker compose --profile attack down
```
Suba de novo (`run_attack.sh` builda sozinho) sempre que quiser gerar um ataque novo — a
senha e a wordlist podem ser trocadas em `scripts/attack/wordlist.txt`.

## Por que isso é melhor que só mostrar o gerador
Quem avalia o projeto consegue ver, no seu vídeo, o Hydra rodando em um terminal e o
alerta aparecendo no Kibana segundos depois. É a prova de que a detecção reage a tráfego
real, não só a dados fabricados.
