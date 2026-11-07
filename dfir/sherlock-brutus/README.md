# Sherlock Brutus | Investigação forense de um ataque SSH

**Hack The Box | Sherlock aposentado | Linux | DFIR | Incident Response**

Concluí o Sherlock Brutus e organizei este estudo para documentar o raciocínio de uma investigação de comprometimento Linux. O foco está na análise de autenticações SSH, na correlação de sessões e no reconhecimento de ações executadas após o acesso inicial.

**Sobre as evidências:** o cenário e a sequência de eventos descritos aqui foram conferidos em referências públicas do Sherlock. Os arquivos `auth.log`, `wtmp` e as capturas da minha resolução não foram disponibilizados para a elaboração deste texto. Por isso, os horários exatos e as evidências pessoais permanecem pendentes. Este é um estudo educacional, não um relato de incidente corporativo.

## Cenário

O Brutus apresenta sinais de comprometimento de um servidor Linux associado a um ambiente Confluence. O acesso inicial ocorre após tentativas de adivinhação de senha por SSH. O cenário também apresenta ações posteriores ao login, incluindo a criação de uma conta local privilegiada.

Para reconstruir os acontecimentos, duas fontes são particularmente relevantes:

| Fonte | Utilidade na investigação |
| --- | --- |
| `auth.log` | Identificar falhas e sucessos de autenticação, eventos de sessão, ações administrativas e comandos registrados pelo `sudo` |
| `wtmp` | Correlacionar registros de login e logout e verificar informações de sessões interativas |

Um evento `Accepted password` é um indício importante, mas não explica sozinho o que aconteceu depois. O objetivo é relacioná-lo a outros registros e construir uma linha do tempo sustentada por evidências.

## Como organizei a análise

1. Localizar as falhas de autenticação SSH e identificar conta, origem e intervalo de tempo.
2. Procurar o sucesso de autenticação relacionado à mesma campanha.
3. Confrontar os eventos do `sshd` com os registros de sessão do `wtmp`.
4. Verificar criação de usuários, mudanças de privilégios e uso de `sudo`.
5. Identificar atividades posteriores ao login, registrando o que os logs realmente permitem concluir.
6. Elaborar uma linha do tempo e mapear as técnicas observadas para o MITRE ATT&CK.

O procedimento detalhado, com comandos sugeridos e limites da análise, está em [investigation.md](investigation.md).

## Sequência investigada

```text
Tentativas de autenticação SSH
          |
          v
Sucesso de autenticação
          |
          v
Abertura de sessão no servidor
          |
          v
Criação de conta local com privilégios
          |
          v
Nova atividade autenticada
          |
          +--> Acesso a arquivo sensível de credenciais
          |
          +--> Comando para solicitar conteúdo remoto
```

A sequência acima resume o cenário conhecido. A execução de um script remoto, eventual exfiltração e outros efeitos não podem ser afirmados apenas porque existe um comando de requisição registrado.

## Evidências da investigação

Os espaços abaixo estão prontos para receber minhas capturas. **Cada imagem será exibida diretamente neste README assim que o arquivo correspondente for enviado à pasta [evidence](evidence/).** Enquanto não houver upload, o GitHub poderá exibir uma imagem indisponível. Não foram criadas imagens ilustrativas para substituir provas.

### E01. Falhas de autenticação SSH

Identificar a repetição de tentativas, os horários, a conta e o endereço de origem.

![E01: falhas de autenticação SSH no auth.log](evidence/01-ssh-failed-logins.png)

### E02. Autenticação bem-sucedida

Registrar o evento de sucesso e verificar se está relacionado às falhas anteriores.

![E02: autenticação SSH bem-sucedida](evidence/02-ssh-success.png)

### E03. Sessões registradas no wtmp

Conferir a saída de `last -F -f wtmp` e correlacionar conta, sessão e período.

![E03: sessões no wtmp](evidence/03-wtmp-sessions.png)

### E04. Criação de conta e alteração de privilégios

Documentar os registros que sustentam a criação da conta e sua inclusão em grupos privilegiados.

![E04: criação de conta e alteração de privilégios](evidence/04-account-creation.png)

### E05. Atividade da conta criada

Confirmar o início de sessão ou outra atividade associada à nova conta, quando houver registro correspondente.

![E05: sessão da conta criada](evidence/05-new-account-session.png)

### E06. Atividade posterior ao comprometimento

Apresentar os registros relacionados a `sudo`, acesso ao `/etc/shadow` ou solicitação de conteúdo externo. A captura deve evidenciar o comportamento descrito, sem extrapolar o que o log demonstra.

![E06: atividade posterior ao acesso](evidence/06-post-exploitation.png)

### E07. Linha do tempo

Inserir uma timeline produzida a partir dos horários conferidos nos artefatos.

![E07: linha do tempo da investigação](evidence/07-timeline.png)

### E08. Conclusão do Sherlock

Comprovante de conclusão no HTB, sem expor flags, credenciais ou informações sensíveis.

![E08: conclusão do Sherlock Brutus](evidence/08-htb-completion.png)

Os nomes exatos dos arquivos estão reunidos em [evidence/README.md](evidence/README.md). **Basta enviar os prints; não é necessário editar este README para fazer as imagens aparecerem.** Os horários e os achados específicos do relatório deverão ser conferidos com as imagens.

## Principais aprendizados

**Autenticação não é a investigação inteira.** Além de localizar um login bem-sucedido, é preciso verificar abertura de sessão, alteração de contas, privilégios e atividades posteriores.

**Persistência exige contexto.** Uma conta administrativa inesperada pode indicar manutenção indevida de acesso. A conclusão depende de registros de criação, mudanças de grupos e uso da identidade.

**O alcance dos logs precisa ser respeitado.** Um comando de download não comprova execução de código. Sem telemetria adicional, certas etapas permanecem inconclusivas.

**A detecção e a investigação se complementam.** No [SIEM Brute Force Detection Lab](../../siem/siem-bruteforce-lab/), trabalhei em regras para localizar padrões de autenticação suspeitos. No Brutus, o objetivo é reconstruir o que ocorreu após um acesso potencialmente malicioso.

## Documentação complementar

| Documento | Conteúdo |
| --- | --- |
| [Relatório de investigação](investigation.md) | Metodologia, fontes, linha do tempo, hipóteses e recomendações |
| [Detecção e resposta](detection-and-response.md) | Casos de uso, limitações e fluxo de triagem para SOC |
| [Guia dos prints](evidence/README.md) | Arquivos esperados e instruções de upload |

## Referências

- [HTB: diretrizes de publicação de write-ups](https://help.hackthebox.com/en/articles/5188925-streaming-writeups-walkthrough-guidelines)
- [0xdf: análise pública do Sherlock Brutus](https://0xdf.gitlab.io/2024/04/09/htb-sherlock-brutus.html). Referência externa utilizada para contextualizar o cenário, não apresentada como uma análise original minha.
- [MITRE ATT&CK: T1110.001](https://attack.mitre.org/techniques/T1110/001/), [T1136.001](https://attack.mitre.org/techniques/T1136/001/) e [T1003.008](https://attack.mitre.org/techniques/T1003/008/).

**Nota:** os comandos, procedimentos e recomendações não devem ser interpretados como prova de execução pessoal quando faltarem capturas ou registros correspondentes.
