# Evidências da investigação — lugar reservado para seus prints

A estrutura já está vinculada aos documentos do [Sherlock Brutus](../README.md). **A única ação necessária é adicionar as imagens correspondentes a esta pasta e manter os nomes indicados.** Os arquivos abaixo ainda não estão presentes; não se trata de falha de renderização.

## Posições planejadas

| ID | Nome exato do arquivo | O que registrar |
| --- | --- | --- |
| E01 | `01-ssh-failed-logins.png` | Recorte de `auth.log` com repetição de falhas, usuário, horário e origem |
| E02 | `02-ssh-success.png` | Evento de sucesso correspondente, com contexto temporal |
| E03 | `03-wtmp-sessions.png` | Saída de `last -F -f wtmp`, mostrando a sessão relacionada |
| E04 | `04-account-creation.png` | Eventos de criação de conta local e concessão de privilégios |
| E05 | `05-new-account-session.png` | Sessão aberta com a conta criada, se constar dos artefatos |
| E06 | `06-post-exploitation.png` | Registro de `sudo`, acesso a `/etc/shadow` e/ou comando de requisição remota |
| E07 | `07-timeline.png` | Timeline montada por você, baseada nos eventos analisados |
| E08 | `08-htb-completion.png` | Comprovante da conclusão do Sherlock, sem flags ou informação privada |

## Requisitos para uma boa captura

- Mostrar o comando/filtro e a linha de log que apoia a conclusão; quando possível, preservar horário e fuso.
- Evitar imagens que cortem justamente o campo `source.ip`, `user.name`, data/hora ou mensagem.
- Não publicar tokens de acesso, senhas, dados pessoais, flags ou material de outros usuários.
- Distinguir captura obtida na sua investigação de imagem ilustrativa ou retirada de terceiros.
- Se as evidências revelarem uma conclusão diferente, **corrigir a linha do tempo e o relatório**; a prova tem prioridade sobre a narrativa.

## Como adicionar

1. Acesse esta pasta no GitHub e selecione **Add file → Upload files**.
2. Renomeie as capturas conforme a tabela (E01–E08).
3. Confirme o commit e consulte [investigation.md](../investigation.md) para alinhar os horários exatos.
4. Se não possuir um print específico, mantenha-o pendente em vez de criar uma prova artificial.

## Galeria — habilitar após envio

Para evitar imagens quebradas antes de você enviar os arquivos, as referências estão comentadas. Quando fizer o upload, remova os marcadores de comentário (`<!--` e `-->`) somente nos blocos correspondentes:

<!--
### E01 — Falhas de autenticação SSH
![E01 — Falhas de autenticação SSH](01-ssh-failed-logins.png)

### E02 — Autenticação bem-sucedida
![E02 — Autenticação SSH bem-sucedida](02-ssh-success.png)

### E03 — Sessões do wtmp
![E03 — Sessões registradas no wtmp](03-wtmp-sessions.png)

### E04 — Criação de conta e privilégios
![E04 — Criação de conta local e privilégios](04-account-creation.png)

### E05 — Nova sessão
![E05 — Sessão da conta criada](05-new-account-session.png)

### E06 — Atividades pós-acesso
![E06 — Atividades pós-comprometimento](06-post-exploitation.png)

### E07 — Timeline autoral
![E07 — Linha do tempo de investigação](07-timeline.png)

### E08 — Conclusão HTB
![E08 — Comprovante de conclusão](08-htb-completion.png)
-->

**Estado atual:** nenhuma dessas capturas foi recebida nesta conversa ou validada pelo assistente. Este guia documenta apenas os arquivos esperados.
