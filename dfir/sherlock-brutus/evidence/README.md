# Evidências da investigação: lugar reservado para seus prints

As imagens são exibidas diretamente no [README do Sherlock Brutus](../README.md) assim que forem enviadas com os nomes abaixo. **A única ação necessária é adicionar as imagens correspondentes a esta pasta e manter os nomes indicados.** Os caminhos das imagens já estão incorporados no README. Antes do upload, o GitHub pode apresentar espaços de imagem indisponível.

## Posições planejadas

| ID | Nome exato do arquivo | O que registrar |
| --- | --- | --- |
| E01 | [01-ssh-failed-logins.png](01-ssh-failed-logins.png) | Recorte de `auth.log` com repetição de falhas, usuário, horário e origem |
| E02 | [02-ssh-success.png](02-ssh-success.png) | Evento de sucesso correspondente, com contexto temporal |
| E03 | [03-wtmp-sessions.png](03-wtmp-sessions.png) | Saída de `last -F -f wtmp`, mostrando a sessão relacionada |
| E04 | [04-account-creation.png](04-account-creation.png) | Eventos de criação de conta local e concessão de privilégios |
| E05 | [05-new-account-session.png](05-new-account-session.png) | Sessão aberta com a conta criada, se constar dos artefatos |
| E06 | [06-post-exploitation.png](06-post-exploitation.png) | Registro de `sudo`, acesso a `/etc/shadow` e/ou comando de requisição remota |
| E07 | [07-timeline.png](07-timeline.png) | Timeline montada por você, baseada nos eventos analisados |
| E08 | [08-htb-completion.png](08-htb-completion.png) | Comprovante da conclusão do Sherlock, sem flags ou informação privada |

## Requisitos para uma boa captura

- Mostrar o comando/filtro e a linha de log que apoia a conclusão; quando possível, preservar horário e fuso.
- Evitar imagens que cortem justamente o campo `source.ip`, `user.name`, data/hora ou mensagem.
- Não publicar tokens de acesso, senhas, dados pessoais, flags ou material de outros usuários.
- Distinguir captura obtida na sua investigação de imagem ilustrativa ou retirada de terceiros.
- Se as evidências revelarem uma conclusão diferente, **corrigir a linha do tempo e o relatório**; a prova tem prioridade sobre a narrativa.

## Como adicionar

1. Acesse esta pasta no GitHub e selecione **Add file → Upload files**.
2. Renomeie as capturas conforme a tabela (E01aE08).
3. Confirme o commit. As imagens aparecerão diretamente no README principal sem alterar o Markdown. Os campos de horário do [relatório](../investigation.md) continuarão como pendentes até serem revisados à luz das provas.
4. Se não possuir um print específico, mantenha-o pendente em vez de criar uma prova artificial.

## Apresentação das provas

As imagens já estão incorporadas no README principal do Brutus. **Não é necessário editar o Markdown**; basta enviar cada print com seu nome correspondente. Depois do upload, as imagens aparecerão diretamente na seção de evidências.

**Estado atual:** nenhuma dessas capturas foi recebida nesta conversa ou validada pelo assistente. Este guia documenta apenas os arquivos esperados.
