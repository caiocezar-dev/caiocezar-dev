# Plano de implantação — atividade de commits no perfil GitHub

**Titular:** `caiocezar-dev`
**Repositório de apresentação:** `caiocezar-dev/caiocezar-dev`
**Objetivo:** publicar indicadores confiáveis da atividade pessoal no GitHub,
com contribuições privadas elegíveis e sem divulgação de informações dos projetos.

## Critérios de aceite

- O README permanece público, legível, com identidade visual da Arcis.
- O painel mostra commits pessoais elegíveis, contribuições agregadas, PRs
  e quantidade de repositórios com commits nos últimos 12 meses.
- O calendário utiliza dados diários provenientes da API oficial do GitHub.
- Nenhum nome de repositório privado, mensagem de commit, arquivo, e-mail ou
  token é gravado em arquivos públicos, SVG ou logs intencionalmente.
- Qualquer ausência de credencial ou erro de coleta preserva a versão anterior.
- A rotina diária e a execução manual usam o mesmo script.
- O README distingue o retrato inicial (amostrado) do painel definitivo
  (contribuições efetivamente creditadas ao usuário).

## Execução por fase

| Fase | Entrega / evidência | Status |
| --- | --- | --- |
| 0. Auditoria | README, SVG, gerador, workflow e documentação inspecionados | Concluído |
| 1. Fontes | Métricas GraphQL oficiais; escopo mínimo `read:user` | Concluído |
| 2. Proteção | Validação de `viewer.login`, métricas, datas e preservação do SVG | Implementado |
| 3. Qualidade | Testes automáticos sem rede e validação em GitHub Actions | Testes implementados; resultado de CI ainda não aferido |
| 4. Entrega | Script, workflow, documentação e README versionados em `main` | Implementado |
| 5. Autorização | Mostrar contribuições privadas e cadastrar o token em secret | Pendente de ação autenticada do titular |
| 6. Go-live | Executar workflow manual, conferir logs e conferir SVG publicado | Pendente da fase 5 |
| 7. Operação | Atualização agendada diariamente, sujeita à plataforma | Configurada; aguarda ativação |

## Dependências que não podem ser automatizadas pelo conector disponível

1. Em https://github.com/caiocezar-dev, marcar
   **Contribution settings → Private contributions**.
2. Em https://github.com/settings/tokens, criar PAT (classic)
   da conta titular com somente `read:user`.
3. Em
   https://github.com/caiocezar-dev/caiocezar-dev/settings/secrets/actions,
   cadastrar o PAT como `PROFILE_STATS_TOKEN`.
4. Em https://github.com/caiocezar-dev/caiocezar-dev/actions,
   selecionar o workflow e executar **Run workflow** na `main`.

**Regra de segurança:** nunca enviar a credencial por chat, issues,
commits ou qualquer outro canal externo; usar somente o formulário
seguro de secrets do GitHub.

## Operação e manutenção

- Rotina: GitHub Actions `activity.yml` com agendamento diário às 09:15 UTC.
- Fonte de dados: `contributionsCollection` via GitHub GraphQL.
- Publicação: `assets/activity.svg`, sem consultas no navegador do visitante.
- Falha operacional: manter o último painel válido e sinalizar erro no Actions.
- Renovação: quando o token expirar, atualizar somente o secret.
- Critério de divulgação: números públicos agregados, nunca detalhes privados.

## Auditoria de números iniciais

O SVG anterior foi produzido de uma **amostra** de até 100 commits recentes
por repositório e inclui potencialmente coautores e automações. Por isso seus
totais não podem ser tratados como commits pessoais definitivos nem
comparados diretamente com o campo `totalCommitContributions`.

A única certificação de que o novo painel está ativo é uma execução
bem-sucedida do workflow **com token configurado**, seguida da inspeção
do SVG atualizado e dos resultados de testes.

[Procedimento operacional completo](./PROFILE_STATS_SETUP.md)
