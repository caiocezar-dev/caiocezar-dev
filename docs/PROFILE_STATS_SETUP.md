# Ativação do painel de contribuições privadas — GitHub

## Estado atual

O README público já apresenta um **retrato de atividade observada até 23/10/2026**.
Esse retrato identifica commits presentes em repositórios associados à conta;
ele não garante que todos tenham sido criados pelo titular e não representa
uma contagem completa (limite de 100 commits por repositório na consulta inicial).

A implementação definitiva usa a API GraphQL do GitHub para mostrar
**contribuições elegíveis creditadas ao titular do perfil** em uma janela
móvel dos últimos 12 meses, inclusive privadas quando autorizadas.

**A ativação precisa de duas autorizações feitas pelo titular no GitHub:**
marcar a opção de contribuições privadas e criar o secret de leitura.
A integração GitHub usada para editar os arquivos não dispõe de permissões
para essas duas alterações nas configurações da conta.

## A. Habilitar contribuição privada no perfil nativo

1. Abra https://github.com/caiocezar-dev
2. Acima do calendário, clique em **Contribution settings**.
3. Selecione **Private contributions**.

Essa escolha mostra contagens anônimas. Nomes de repositórios privados,
mensagens, hashes e código-fonte continuam ocultos.

Referência:
https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements

## B. Criar uma credencial com privilégio mínimo

1. Acesse https://github.com/settings/tokens
2. Escolha **Generate new token (classic)**.
3. Defina uma expiração apropriada (ex.: 90 dias) e selecione **somente**
   o escopo `read:user`.
4. Não selecione `repo`, `workflow` nem permissões de escrita.
5. Copie o token diretamente para o secret abaixo e descarte qualquer
   cópia em arquivos, prints ou mensagens.

A documentação GraphQL informa que contribuições privadas são incluídas
com o escopo opcional `read:user`:
https://docs.github.com/en/graphql/reference/users#contributionscollection

**Atenção:** ao expirar, o token terá que ser renovado. Um token criado
por outra conta não será aceito: o coletor valida `viewer.login`.

## C. Cadastrar o token como secret

1. Abra https://github.com/caiocezar-dev/caiocezar-dev/settings/secrets/actions
2. Clique em **New repository secret**.
3. Preencha:
   - **Name:** `PROFILE_STATS_TOKEN`
   - **Secret:** token gerado no passo B.
4. Salve. O valor não deve ser incluído em nenhum arquivo versionado.

O workflow `.github/workflows/activity.yml` lê o secret somente para
identificar a disponibilidade da credencial e executar a consulta autenticada.
O SVG contém **apenas contagens e frequência de contribuição**.

## D. Executar e validar

1. Acesse https://github.com/caiocezar-dev/caiocezar-dev/actions
2. Selecione **Atualizar painel de atividade** e clique em **Run workflow**
   na branch `main`.
3. Confirme no log as etapas:
   - Validar gerador e segurança
   - Verificar credencial configurada
   - Gerar estatísticas pessoais autorizadas
   - Publicar somente o painel atualizado
4. Visualize o README: https://github.com/caiocezar-dev

Depois da primeira execução bem-sucedida, o SVG é atualizado diariamente
às **09:15 UTC (06:15 BRT)**, sujeito à disponibilidade e política
do GitHub Actions.

**Falha segura:** se faltar token, houver erro de autenticação, incompatibilidade
de titular ou dados inválidos, o arquivo anterior é preservado. Uma execução
manual sem secret encerra com erro explícito; execuções agendadas sem o secret
apenas registram um aviso e não publicam dados fictícios.

## Como interpretar os números

| Indicador | Fonte | Significado |
| --- | --- | --- |
| Commits / 12 meses | `totalCommitContributions` | Commits elegíveis atribuídos ao titular |
| Contribuições | `contributionCalendar.totalContributions` | Atividades elegíveis de diferentes tipos, não apenas commits |
| Repos com commits | `totalRepositoriesWithContributedCommits` | Quantidade de repositórios com commits elegíveis, sem nomes |
| Pull requests | `totalPullRequestContributions` | Pull requests abertas pelo titular |
| Calendário | `contributionDays` | Atividades atribuídas em cada dia |

Contribuições de forks, branch não padrão ou commits com e-mail não
vinculado à conta podem ficar fora do calendário, conforme as regras
do GitHub:
https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference

## Diagnóstico e governança

| Cenário | Procedimento |
| --- | --- |
| O SVG ainda mostra “atividade observada” | Executar workflow manual após configurar o token |
| `PROFILE_STATS_TOKEN` ausente | Criar o secret conforme C |
| Token pertence a outro usuário | Emitir token na conta `caiocezar-dev` |
| Falha de autenticação | Renovar token e confirmar escopo `read:user` |
| Workflow executa, mas o push falha | Revisar proteção de branch e permissão `contents: write` |
| Contagens diferem da consulta anterior | É esperado: consulta antiga amostrava commits de repositórios; nova conta contribuições pessoais elegíveis |
| Dados de dias anteriores ausentes | Conferir e-mail do autor, branch padrão, critérios de elegibilidade e UTC |

**Privacidade:** o dashboard público revela apenas volume/frequência agregados.
Se não quiser essa exposição, desabilite o workflow e remova o SVG do README.

Código-fonte: [gerador](../scripts/build_activity_svg.py),
[workflow](../.github/workflows/activity.yml) e
[testes](../tests/test_profile_activity.py).
