# Engenharia de Detecção e Resposta: Brutus

**Escopo:** hipóteses defensivas derivadas do cenário do Sherlock Brutus. **Não são regras implantadas ou validadas em produção.** Esta página contém pseudoconsultas e procedimentos de análise que devem ser adaptados à telemetria e ao mapeamento de campos de cada ambiente.

## 1. Fontes de logs e pré-requisitos

- Autenticação Linux: `/var/log/auth.log` (Debian/Ubuntu) ou `/var/log/secure` (sistemas RHEL), se configurados.
- Sessões: `wtmp`, consultado por `last -f` em laboratório; não é equivalente a um feed normalizado de SIEM.
- Eventos administrativos: `sudo`, `useradd`, `usermod`, além de auditd/process telemetry quando disponíveis.
- Contexto: inventário de ativos, contas autorizadas, origens conhecidas, política de SSH e manutenção.

A coleta correta exige timestamps consistentes, resolução de hostname, identificação da origem e normalização de campos antes de criar regras.

## 2. Casos de uso propostos

| UC | Objetivo | Condição proposta | Atenção a falsos positivos |
| --- | --- | --- | --- |
| UC-01 | SSH password guessing | 10+ falhas para a mesma conta de uma mesma origem em 5 min | Usuário com senha esquecida, scanner autorizado |
| UC-02 | Falhas seguidas de sucesso | Falhas da mesma origem e conta próximas a um sucesso SSH | Credenciais digitadas incorretamente antes do sucesso legítimo |
| UC-03 | Conta local criada fora de janela | Evento `useradd` não esperado, especialmente após logon suspeito | Provisionamento, automação autorizada |
| UC-04 | Elevação via grupo privilegiado | `usermod` / `gpasswd` adicionando conta ao grupo sudo/wheel | Manutenção aprovada |
| UC-05 | Leitura suspeita de arquivo de credenciais | Processo/comando acessa `/etc/shadow`, principalmente por sessão recém-criada | Administração legítima, backup e agentes de segurança |

**Parâmetros iniciais ilustrativos**, não limites universais. Exigem testes de comportamento normal, sensibilidade, cobertura e supervisão de falsos positivos.

## 3. Exemplo didático de busca em arquivo local

```bash
# Pesquisa textual exploratória; não substitui agregação temporal de SIEM.
grep -E 'Failed password|Accepted password' auth.log

# Operações de conta e privilégio, dependendo do que foi registrado:
grep -E 'useradd|usermod|gpasswd|sudo:' auth.log

# Sessões:
last -F -f wtmp
```

Esses comandos **não foram executados por este documento**; são exemplos reproduzíveis para analisar os artefatos locais da HTB.

## 4. Lógica proposta para SIEM

**UC-01: agregação por 5 minutos**

```text
event.category = authentication
AND event.outcome = failure
AND network.protocol = ssh
GROUP BY source.ip, user.name, time_bucket(5m)
HAVING COUNT(*) >= 10
```

**UC-02: correlação com sucesso**

```text
Find repeated SSH failures for (source.ip, user.name)
followed by successful SSH authentication for the same pair
within a defined maxspan, e.g. 10 minutes.
Require corroborating session evidence for incident confirmation.
```

Esses blocos são **pseudocódigo independente de produto**, não consultas KQL/EQL prontas para executar. Na Elastic, KQL filtra eventos; correlação/limiares exigem recursos apropriados do motor de detecção e seus campos ECS.

## 5. Triagem operacional (SOC N1)

1. **Recepção:** registrar alerta, horário com fuso, regra, ativo, conta e origem.
2. **Verificação:** confirmar integridade da telemetria e ocorrências em janelas anteriores.
3. **Contexto:** verificar localização do servidor, acesso remoto autorizado, conta privilegiada e alterações planejadas.
4. **Corroboração:** procurar sucessos SSH, sessões no host, novos usuários, alterações `sudo`, conexões e processos posteriores.
5. **Escalonamento:** se há acesso privilegiado não autorizado ou persistência possível, elevar prioridade e preservar evidências.
6. **Registro:** informar dados observados, hipóteses, confiança e justificativa, evitando apresentar suposições como fatos.

### Exemplo de classificação

- **Somente falhas:** investigar; não concluir comprometimento.
- **Falhas + sucesso da mesma origem/conta:** alta prioridade investigativa, condicionada ao contexto.
- **Falhas + sucesso + conta privilegiada recém-criada:** cadeia de evidências mais forte; escalonamento imediato segundo playbook.

## 6. Risco de detecções frágeis

- NAT, VPN, bastion host e proxy podem concentrar autenticações legítimas em um IP.
- IPs dinâmicos e rotação de origem podem fragmentar contagens.
- Dependência de `auth.log` é insuficiente para detectar todos os comandos pós-login.
- Mudanças de horário, lacunas de ingestão e retenção curta prejudicam a timeline.
- Exceções para contas de serviço devem ser específicas, justificadas e periodicamente revisadas.

## 7. Melhorias propostas para um laboratório próprio

- Coletar logs de uma VM Linux de teste com Filebeat ou Elastic Agent.
- Criar um cenário de falhas e sucesso SSH **apenas em máquinas autorizadas**.
- Medir o tempo entre os eventos e a emissão do alerta, quando o motor de detecção estiver ativo.
- Implantar regras para criação de conta e inclusão no grupo sudo.
- Testar cenários de manutenção legítima, falso positivo e evasão por distribuição temporal.
- Publicar prints do dashboard e exportação sanitizada das regras, indicando se o resultado veio de dados sintéticos ou de telemetria real.

## 8. MITRE ATT&CK e referências

- [T1110.001: Password Guessing](https://attack.mitre.org/techniques/T1110/001/)
- [T1136.001: Create Account: Local Account](https://attack.mitre.org/techniques/T1136/001/)
- [T1003.008: /etc/passwd and /etc/shadow](https://attack.mitre.org/techniques/T1003/008/)
- [T1078: Valid Accounts](https://attack.mitre.org/techniques/T1078/)

**Nota de método:** essas sugestões complementam o relatório DFIR; não alegam que uma regra Sigma, Elastic, Splunk ou Wazuh foi de fato implementada para o Brutus.
