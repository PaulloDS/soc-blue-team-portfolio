# HTB Sherlock — Brutus | Investigação DFIR de comprometimento SSH

**Hack The Box · Sherlock (Retired) · DFIR · Linux Forensics / Incident Response**

> **Escopo e rastreabilidade:** o desafio foi concluído pelo autor deste portfólio. Este relatório foi estruturado a partir do cenário público do Brutus e de referências técnicas consultadas; os arquivos originais `auth.log` e `wtmp` e o registro da sessão pessoal de análise **não foram disponibilizados para esta redação**. As conclusões do cenário são apresentadas com referências; **a validação autoral por capturas ainda está pendente**. Não confundir resolução do desafio com experiência profissional em incidente real.

## Resumo executivo

O Brutus reproduz o comprometimento de um servidor Linux associado a um ambiente Confluence. O vetor é uma sequência de tentativas de autenticação SSH que culmina em acesso privilegiado. Em seguida, os registros permitem reconstruir o uso de uma sessão interativa, a criação de uma conta local com privilégio administrativo e atividades posteriores realizadas por essa conta.

O valor do caso está na **correlação entre duas fontes distintas**:

- **`auth.log`** — falhas/sucessos SSH, abertura e encerramento de sessões, criação de usuários, alterações de grupos e comandos registrados pelo `sudo`.
- **`wtmp`** — registros binários de sessões de login e logout; úteis para diferenciar sucesso de autenticação de início efetivo de sessão interativa.

### Principais capacidades demonstráveis após anexar evidências próprias

| Competência | Aplicação neste estudo |
| --- | --- |
| Linux Log Analysis | Identificação de falhas repetidas, sessões SSH e eventos `sudo` |
| Digital Forensics | Investigação conjunta de `auth.log` e `wtmp` |
| Incident Timeline | Construção de linha do tempo em UTC com fonte por evento |
| Incident Response | Avaliação de impacto, persistência e medidas de contenção |
| MITRE ATT&CK | Mapeamento da cadeia de ataque para técnicas documentadas |
| Investigative Reporting | Separação entre fato observado, inferência e lacuna de visibilidade |

## Visão da cadeia de ataque

```text
SSH acessível
   |
   v
Múltiplas tentativas de senha (T1110.001)
   |
   v
Autenticação bem-sucedida em root
   |
   v
Sessão interativa confirmada por auth.log + wtmp
   |
   v
Nova conta local com permissão sudo (T1136.001)
   |
   v
Autenticação pela conta criada
   |
   +--> Leitura de /etc/shadow com sudo (T1003.008)
   |
   +--> Requisição de script remoto com curl (execução não comprovada)
```

## Documentos

| Arquivo | Conteúdo |
| --- | --- |
| [investigation.md](investigation.md) | Relatório DFIR, metodologia, linha do tempo, achados, MITRE e resposta |
| [detection-and-response.md](detection-and-response.md) | Hipóteses de detecção, fontes de telemetria, tuning e playbook de triagem |
| [evidence/README.md](evidence/README.md) | Lista de capturas e nomes exatos para inserir suas provas |

## Evidências a anexar

As imagens já estão referenciadas na [documentação das evidências](evidence/README.md) pelos nomes esperados. Basta adicionar os arquivos de imagem à pasta `evidence/`, preservando os nomes sugeridos.

**Status:** `Documentação pronta` · `Capturas da investigação pessoal pendentes`

## Principais conclusões técnicas

1. **Um sucesso de autenticação não basta para provar uma sessão interativa.** É preciso correlacionar `sshd`, `systemd-logind` e `wtmp`.
2. **A cadeia de atividade importa mais do que um único alerta.** O acesso privilegiado, a conta recém-criada e o uso de `sudo` constituem sinais complementares.
3. **A criação de conta local privilegiada é uma forma de persistência.** Monitorar mudanças de usuários e grupos é tão importante quanto monitorar tentativas SSH.
4. **Os logs têm limites.** Um registro de `curl` não comprova que o script baixado foi executado ou que persistência adicional foi instalada.

## Relação com outros projetos

O [SIEM Brute Force Detection Lab](../../siem/siem-bruteforce-lab/) documenta a construção de detecções; o Brutus aplica o raciocínio defensivo à **reconstrução forense de um incidente apresentado pela HTB**. São entregas distintas e complementares.

## Fontes e política de publicação

- [Hack The Box — Diretrizes para publicações](https://help.hackthebox.com/en/articles/5188925-streaming-writeups-walkthrough-guidelines)
- [0xdf — HTB Sherlock: Brutus](https://0xdf.gitlab.io/2024/04/09/htb-sherlock-brutus.html) — referência pública com informação de aposentadoria (04/04/2024) e análise dos artefatos.
- [MITRE ATT&CK — T1110.001](https://attack.mitre.org/techniques/T1110/001/), [T1136.001](https://attack.mitre.org/techniques/T1136/001/) e [T1003.008](https://attack.mitre.org/techniques/T1003/008/).

**Observação:** não foram anexados os arquivos originais distribuídos pela HTB, senhas, flags nem uma suposta captura de sessão que não tenha sido fornecida. O material escrito é original e emprega a cronologia publicamente documentada como base para uma revisão posterior com evidências pessoais.
