# Configuração segura do painel de atividade

O README do perfil publica **somente estatísticas agregadas**. O código-fonte,
nomes de repositórios privados, títulos de issues, mensagens de commits,
endereços de e-mail e hashes não são enviados ao SVG.

## 1. Exibir contribuições privadas no perfil nativo

1. Acesse [seu perfil](https://github.com/caiocezar-dev).
2. No calendário de contribuições, abra **Contribution settings**.
3. Ative **Private contributions**.

Essa opção mostra contagens anônimas por dia, não o nome dos repositórios.

## 2. Gerar token de leitura

1. Acesse [Personal access tokens (classic)](https://github.com/settings/tokens).
2. Crie um token com expiração e **somente o escopo `read:user`**.
3. Não conceda o escopo `repo`: o gerador local consulta apenas
   `contributionsCollection` da API GraphQL e não lê repositórios.
4. Não cole o token no README, em commits, issues ou mensagens de chat.

**Nota:** a [documentação GraphQL do GitHub](https://docs.github.com/en/graphql/reference/users#contributionscollection)
identifica `read:user` como o escopo para contabilizar contribuições privadas e internas.

## 3. Salvar o secret no repositório público de perfil

1. Abra [Settings → Secrets and variables → Actions](https://github.com/caiocezar-dev/caiocezar-dev/settings/secrets/actions).
2. Clique em **New repository secret**.
3. Nome: `PROFILE_STATS_TOKEN`.
4. Valor: o token criado anteriormente.

Os GitHub Actions usam esse secret somente durante a execução e não o gravam
nos artefatos de publicação.

## 4. Gerar o dashboard

1. Abra [Actions](https://github.com/caiocezar-dev/caiocezar-dev/actions).
2. Selecione **Atualizar painel de atividade**.
3. Use **Run workflow** na branch principal (`main`).
4. Confira se o workflow terminou com sucesso.
5. Verifique o arquivo [assets/activity.svg](../assets/activity.svg).

Depois da primeira execução, o workflow tenta atualizar automaticamente o
cartão uma vez ao dia. Se a configuração estiver incompleta, ele preserva
o SVG anterior e não inventa números.

## Interpretação das métricas

- **Commits / 12 meses:** `totalCommitContributions` da API GraphQL.
- **Contribuições:** `contributionCalendar.totalContributions`, que reúne
  diferentes atividades; não é sinônimo de número de commits.
- **Pull requests / Issues:** contagens elegíveis segundo as regras do GitHub.
- **Calendário:** número de contribuições por dia, sem detalhes do repositório.

Commits podem não ser contados caso o e-mail do autor não esteja associado
ao GitHub ou o commit não esteja na branch principal/`gh-pages`, conforme
[critérios oficiais](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference).

### Diagnóstico

| Sintoma | O que verificar |
| --- | --- |
| O SVG continua com mensagem de configuração | Se o secret `PROFILE_STATS_TOKEN` foi salvo e o workflow foi executado |
| O workflow não consegue consultar a API | Expiração do token e escopo `read:user` |
| Repositórios privados não aparecem na contagem | `Contribution settings → Private contributions` e autor dos commits |
| O workflow gera o SVG, mas não faz push | Permissão `contents: write`, proteção de branch e política de Actions |
| Dados parecem incompletos | Regras de elegibilidade, data dos commits e janela dos últimos 12 meses |

**Privacidade:** um contador público pode revelar volume e frequência de
trabalho, embora não revele o conteúdo dos projetos. Desative a automação
e/ou a opção de contribuições privadas se não desejar expor esses totais.
