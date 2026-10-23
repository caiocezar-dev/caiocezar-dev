# Perfil GitHub — Dashboard de contribuições automático

## Fonte de verdade

O calendário nativo do GitHub exibido em 23/10/2026 registra **3.696 contribuições nos últimos 12 meses**.
Esse número é a referência visual fornecida pelo titular naquele dia, **não é constante no código**.
A atualização automática consulta `viewer.contributionsCollection` na API GraphQL oficial,
atribuindo os dados ao próprio titular autenticado (`viewer.login == caiocezar-dev`).

A versão anterior do SVG mostrava **≥377 commits observados em outubro** e **≥143 desde 16/10**.
Esses valores eram uma **amostra de commits encontrados em repositórios**, com limite de
100 resultados por repositório. Podiam incluir automações, merges e outros autores.
Além disso, cobriam um **período diferente** e por isso não podiam ser comparados
às **3.696 contribuições** do calendário nativo.

### Métricas definitivas

| Indicador | Campo / cálculo | Limitações |
| --- | --- | --- |
| Contribuições (12 meses) | `contributionCalendar.totalContributions` | Abrange tipos diferentes de contribuição |
| Commits elegíveis | `totalCommitContributions` | Só commits atribuídos ao usuário e elegíveis no GitHub |
| Pull requests | `totalPullRequestContributions` | PRs abertas pelo titular |
| Issues | `totalIssueContributions` | Issues abertas pelo titular |
| Reviews | `totalPullRequestReviewContributions` | Reviews atribuídas ao titular |
| Repositórios com commits | `totalRepositoriesWithContributedCommits` | Contagem, sem revelar nomes |
| Dias de atividade | Dias com `contributionCount > 0` | Janela fornecida pela API |
| Pico diário | `max(contributionCount)` | Contribuições, não commits |
| Últimos 7 e 30 dias | Soma dos últimos 7/30 dias do calendário | Janela móvel baseada nas datas da API |
| Heatmap e barras mensais | Agregação por dia/mês do calendário | Primeiro e último meses podem ser parciais |

Os valores **não são simulados nem fixados no SVG**. A atualização utiliza a API
oficial e inclui contribuições privadas **somente quando a conta concede acesso**.

## Pré-requisitos de autenticação

1. Abra https://github.com/caiocezar-dev e selecione
   **Contribution settings → Private contributions** para mostrar contagens privadas anônimas.
2. Acesse https://github.com/settings/tokens e crie
   **Personal access token (classic)** com somente o escopo `read:user`.
3. No repositório de perfil, abra
   https://github.com/caiocezar-dev/caiocezar-dev/settings/secrets/actions
   e salve o token em um repository secret de nome **`PROFILE_STATS_TOKEN`**.
4. Selecione o workflow **Atualizar painel de atividade** em
   https://github.com/caiocezar-dev/caiocezar-dev/actions
   e clique em **Run workflow**, usando a branch `main`.

**Nunca cole tokens no chat, README, PR, commit, e-mail ou logs.**
O token de coleta **não precisa** de acesso `repo`, `workflow` ou escrita.
O `GITHUB_TOKEN` efêmero do Actions escreve apenas o SVG no
repositório público de perfil.

## Automação e integridade

- Agendamento a cada 6 horas, às 00:17, 06:17, 12:17 e 18:17 (horário de Recife).
- Testes em `pull_request`, `push` e execução periódica/manual.
- Falha na API, autenticação, schema, ordem de datas ou calendário incompleto
  **não substitui** o SVG anteriormente gerado.
- Escrita do SVG em arquivo temporário e substituição atômica.
- Publicação somente quando `assets/activity.svg` muda.
- Nenhum nome de repositório privado, hash, mensagem, caminho de código ou segredo
  aparece na consulta GraphQL nem no SVG.
- A data de sincronização vem do próprio momento da execução, em UTC.
- A versão estática de outubro não é usada como fonte de dados.
- O GitHub pode atrasar execuções agendadas e pode desativá-las
  em repositórios públicos sem atividade prolongada.

### Diagnóstico

| Sintoma | Verificação |
| --- | --- |
| O painel continua indicando configuração pendente | Verificar existência do secret e executar o workflow manual |
| Token recusado ou pertence a outro usuário | Emitir o PAT na conta `caiocezar-dev` com `read:user` |
| Coleta correta, números diferentes da captura | Conferir data da janela, commits elegíveis e configuração de privadas |
| Falha em publicação do SVG | Consultar o log de `git push`, branch protection e `contents:write` |
| Dashboard parece não atualizar | Revisar última sincronização no SVG e execução no Actions |
| GitHub não mostra alguns commits | Conferir e-mail do autor, branch padrão e elegibilidade de contribuição |
| Token expirado | Substituir apenas o valor do secret, sem commitar o token |

## Implementação

- Fonte: [scripts/build_activity_svg.py](../scripts/build_activity_svg.py)
- Testes: [tests/test_profile_activity.py](../tests/test_profile_activity.py)
- Rotina: [.github/workflows/activity.yml](../.github/workflows/activity.yml)
- SVG: [assets/activity.svg](../assets/activity.svg)

Documentação oficial:
- https://docs.github.com/en/graphql/reference/users#contributionscollection
- https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference
- https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule
