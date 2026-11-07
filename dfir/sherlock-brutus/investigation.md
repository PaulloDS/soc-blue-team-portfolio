# Relatório DFIR — Sherlock Brutus

**Tipo:** estudo de caso técnico de cenário fictício e aposentado da Hack The Box  
**Origem:** Sherlock Brutus (Linux / SSH)  
**Estado da análise:** documentação baseada no cenário e em fontes públicas; capturas da resolução pessoal pendentes de inclusão  
**Classificação:** exercício educacional, não incidente em ambiente corporativo

> **Integridade da evidência:** sem acesso aos `auth.log`, `wtmp` e histórico de comandos empregados pelo autor, este documento **não atribui horários, IPs, contas específicas ou saídas de terminal à investigação pessoal**. Os achados abaixo descrevem a cadeia do cenário publicada em referências externas; os campos de evidência devem ser conferidos contra os artefatos da HTB antes da inclusão de prints.

## 1. Objetivo e hipóteses

Investigar um possível comprometimento de servidor Linux por tentativa de adivinhação de senha SSH, verificar acesso não autorizado, identificar ações pós-comprometimento e propor resposta adequada.

**Hipóteses de trabalho**

- H1 — uma origem efetuou diversas falhas SSH em curta janela, seguidas por autenticação bem-sucedida;
- H2 — o acesso resultou em sessão interativa no servidor;
- H3 — o agente criou outra identidade local com privilégios elevados;
- H4 — houve tentativa de acessar material de autenticação e de buscar conteúdo externo.

Essas hipóteses precisam de confirmação por linhas dos logs, não apenas por associação com técnicas MITRE.

## 2. Fontes e confiabilidade

| Fonte | O que permite observar | Limite |
| --- | --- | --- |
| `auth.log` | Eventos `sshd`, falhas, sucesso, `pam_unix`, `sudo`, `useradd` e mudanças de grupos quando registrados | Nem todo comando de shell aparece; dependerá da configuração de auditoria |
| `wtmp` | Abertura/encerramento de sessões e identificação de terminal/origem, quando disponível | Formato binário; relógio e integridade da máquina podem afetar a leitura |
| Metadados do exercício | Contextualização do ambiente e objetivos do Sherlock | Não substituem evidência diretamente extraída dos logs |

Comandos de análise **sugeridos** (não apresentados como o histórico real da resolução):

```bash
# Inspecionar falhas e sucessos SSH, mantendo o texto original
grep -En 'Failed password|Accepted password|Accepted publickey' auth.log

# Investigar abertura de sessões e ações administrativas
grep -En 'session opened|session closed|useradd|usermod|sudo:' auth.log

# Consultar histórico de sessões no arquivo wtmp distribuído
last -F -f wtmp

# Se precisar validar tipo e integridade dos artefatos
file auth.log wtmp
sha256sum auth.log wtmp
```

**Boas práticas:** trabalhar com cópias dos arquivos, preservar o fuso horário de origem, conferir hashes e evitar alterar os artefatos. Não publique hashes como se os tivesse coletado sem executar os comandos.

## 3. Método de correlação

1. **Estabelecer a janela do incidente:** localizar a primeira concentração relevante de erros SSH e definir período anterior e posterior para contexto.
2. **Agrupar tentativas:** correlacionar origem, usuário pretendido, intervalo e volume de falhas.
3. **Identificar sucesso:** procurar eventos `Accepted ...` e conferir se correspondem à mesma campanha.
4. **Corroborar sessão:** comparar o sucesso com registros do `wtmp`, terminal e eventos de abertura de sessão.
5. **Analisar pós-acesso:** procurar criação de conta, inclusão em grupo privilegiado, uso de `sudo`, acesso a arquivos sensíveis e comandos de rede.
6. **Avaliar persistência e impacto:** distinguir o que foi registrado do que é mera possibilidade.
7. **Documentar:** preservar referências às linhas e capturas, classificar grau de confiança e registrar lacunas.

## 4. Linha do tempo investigativa

A ordem abaixo corresponde ao **encadeamento público do cenário**. Não é uma reconstrução original a partir de arquivos fornecidos neste chat. Substitua os campos marcados por horários exatos **somente após verificar os seus artefatos**.

| Ordem | Marco | Fonte esperada | Horário UTC / evidência pessoal |
| --- | --- | --- | --- |
| 1 | Série de falhas de autenticação SSH | `auth.log` / `sshd` | **A conferir** — [E01](evidence/README.md) |
| 2 | Autenticação bem-sucedida em conta privilegiada | `auth.log` / `sshd` | **A conferir** — [E02](evidence/README.md) |
| 3 | Abertura e encerramento de sessão interativa | `wtmp` e mensagens de sessão | **A conferir** — [E03](evidence/README.md) |
| 4 | Criação de usuário local e concessão de privilégios | `auth.log` / auditoria disponível | **A conferir** — [E04](evidence/README.md) |
| 5 | Atividade autenticada como a identidade recém-criada | `auth.log` + `wtmp` | **A conferir** — [E05](evidence/README.md) |
| 6 | Leitura de `/etc/shadow` e comando envolvendo recurso remoto | Registros `sudo`, caso presentes | **A conferir** — [E06](evidence/README.md) |

## 5. Achados e avaliação

### F01 — Tentativas de força bruta por SSH

Uma sequência de falhas de senha, concentrada em origem e conta, é compatível com **password guessing**, técnica **MITRE ATT&CK T1110.001**. O limiar isolado não determina comprometimento; depende de evento de sucesso e contexto adicional.

- **Evidência a anexar:** E01 (falhas agregadas) e E02 (sucesso).
- **Confiança nesta redação:** achado do cenário documentado externamente; confirmação autoral pendente.

### F02 — Acesso e sessão

O evento de autenticação bem-sucedida e registros de sessão em `wtmp` são fontes complementares. A análise deve conferir se os respectivos horários, conta, IP/host e TTY são coerentes.

- **Evidência a anexar:** E02 e E03.
- **Cuidado analítico:** `Accepted password` não prova, sozinho, cada ação posterior.

### F03 — Identidade adicional privilegiada

Os relatos públicos do Brutus descrevem criação de conta local com privilégios elevados. A criação da conta se relaciona a **T1136.001 — Create Account: Local Account**. A alteração de privilégios deve ser descrita separadamente, com os eventos que a sustentam.

- **Evidência a anexar:** E04 e E05.
- **Significado:** possível mecanismo para manter acesso mesmo se a senha original for alterada.
- **Cuidado:** confirmar nome, horário e grupo apenas com os seus logs.

### F04 — Tentativa de acesso a credenciais e artefato remoto

A leitura de `/etc/shadow`, quando demonstrada, relaciona-se a **T1003.008 — OS Credential Dumping: /etc/passwd and /etc/shadow**. O registro de `curl` para recurso remoto demonstra uma **requisição/comando**, mas não comprova execução do conteúdo ou implantação de malware.

- **Evidência a anexar:** E06.
- **Limitação:** ausência de telemetria de processos e rede impede conclusões sobre execução posterior, exfiltração ou persistência adicional.

## 6. Síntese e impacto potencial

A cadeia documentada no cenário é compatível com comprometimento de autenticação SSH seguido de ampliação da superfície de persistência via conta privilegiada. Em um ambiente real, esse padrão justificaria escalonamento e investigação urgente de atividades pós-login.

**O que não é possível afirmar com base na documentação atual:** a integridade do sistema restaurada, execução do conteúdo remoto, exfiltração de dados, todas as ações do invasor ou o horário exato de cada evento da sua resolução.

## 7. Resposta recomendada para cenário equivalente

1. Preservar logs e contexto volátil conforme procedimento de coleta forense.
2. Restringir o acesso de origem suspeita e avaliar isolamento do host, considerando risco operacional.
3. Revogar sessões e credenciais comprometidas, rotacionando segredos relevantes.
4. Desabilitar a conta criada sem autorização, após coleta e decisão de resposta.
5. Revisar `sudoers`, grupos privilegiados, chaves SSH, cron, serviços e indicadores de persistência.
6. Analisar possível comprometimento de outros sistemas e escopo lateral.
7. Corrigir exposição SSH, habilitar MFA quando suportado, restringir contas privilegiadas e configurar monitoramento contínuo.
8. Registrar lições aprendidas, lacunas de logging e melhorias de regras.

## 8. Mapeamento MITRE ATT&CK

| Evidência ou comportamento | Técnica | Precisão |
| --- | --- | --- |
| Muitas tentativas de senha SSH | [T1110.001 — Password Guessing](https://attack.mitre.org/techniques/T1110/001/) | Compatível com registros de falhas |
| Conta local adicional criada | [T1136.001 — Create Account: Local Account](https://attack.mitre.org/techniques/T1136/001/) | Requer evidência de criação |
| Leitura de `/etc/shadow` | [T1003.008 — /etc/passwd and /etc/shadow](https://attack.mitre.org/techniques/T1003/008/) | Requer evidência do comando/acesso |
| Uso de conta legítima após comprometimento | [T1078 — Valid Accounts](https://attack.mitre.org/techniques/T1078/) | Anotar se os eventos sustentarem o uso |

## 9. Evidências pendentes

Veja [evidence/README.md](evidence/README.md). A documentação permite integrar prints **sem reescrever o relatório**: cada evidência possui ID e destino previsto.

## Referências

- [0xdf — HTB Sherlock: Brutus (09/04/2024)](https://0xdf.gitlab.io/2024/04/09/htb-sherlock-brutus.html) — referência externa para o encadeamento do cenário, não apresentada como trabalho original do autor.
- [Hack The Box — Streaming, Writeups and Walkthrough Guidelines](https://help.hackthebox.com/en/articles/5188925-streaming-writeups-walkthrough-guidelines).
- [MITRE ATT&CK](https://attack.mitre.org/).

**Autoria do texto:** organização e análise explicativa autorais, elaboradas a partir de cenário e referências públicas. **Análise pessoal dos arquivos originais:** o usuário informou a conclusão do Sherlock; os dados brutos e capturas não foram fornecidos para auditoria deste documento.
