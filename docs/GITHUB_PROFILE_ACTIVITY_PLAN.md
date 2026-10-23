# Plano de execução e validação — Perfil GitHub

**Repositório:** `caiocezar-dev/caiocezar-dev`
**Objetivo:** substituir dashboard amostrado de outubro por dados pessoais oficiais dos
últimos 12 meses, com atualização automática e proteção dos projetos privados.

## Problema identificado

| Item | Implementação anterior | Implementação corrigida |
| --- | --- | --- |
| Fontes | Busca de até 100 commits por repositório | GraphQL `viewer.contributionsCollection` |
| Identidade | Poderia incluir colaboradores e bots | Apenas contribuições creditadas à conta autenticada |
| Escopo | Outubro/2026 (amostragem) | Calendário anual móvel do GitHub |
| Total | ≥377 commits encontrados | Total de contribuições e commits elegíveis, separados |
| Frequência | Snapshot manual ou rotina diária | GitHub Actions a cada 6 horas |
| Segurança | Sem dados dos repositórios, mas contagem ambígua | Token mínimo `read:user`, dados agregados e validação de identidade |
| Gráficos | Barras diárias de outubro | Calendário 12 meses + evolução mensal |
| Testes | Testes com calendário de uma semana | Casos com calendário anual e falhas de coleta |

O GitHub nativo mostrou 3.696 contribuições na captura de 23/10/2026.
Esse valor é observação histórica, nunca uma constante embutida no script.
É esperado que a cifra atual se altere continuamente.

## Etapas de implantação

| Fase | Critério de aceite | Estado |
| --- | --- | --- |
| 1. Analisar origem da divergência | Período e definição da métrica identificados | Concluído |
| 2. Reescrever coletor | GraphQL autenticado, `viewer.login`, schema validado | Implementado |
| 3. Refazer layout | KPIs, calendário anual, gráfico mensal, timestamp | Implementado |
| 4. Automação | Disparo a cada 6 horas e manual, publicação restrita ao SVG | Implementado |
| 5. Testes | Testes unitários em PR e na branch principal | Implementados; CI pendente de comprovação |
| 6. Habilitar credencial | `PROFILE_STATS_TOKEN` secret com `read:user` | Pendente de configuração do titular, se ainda não realizado |
| 7. Go-live | Workflow autenticado com SVG real e execução bem-sucedida | Pendente de verificação |
| 8. Operação | Falha segura, renovação do token e monitoramento de Actions | Procedimento documentado |

## Arquitetura de execução

```text
GitHub Actions (schedule / manual)
  ├── Checkout
  ├── Python py_compile + unittest
  ├── PROFILE_STATS_TOKEN (repository secret)
  │    └── GraphQL viewer.contributionsCollection
  │          ├── Confere viewer.login
  │          ├── Valida campos e calendário anual
  │          └── Deriva KPIs e séries
  └── Renderização SVG
         ├── Grava em arquivo temporário
         ├── Substitui assets/activity.svg atomically
         └── Commit apenas se houver diff
```

O `GITHUB_TOKEN` do Actions é usado somente para gravar o SVG na
branch `main`, e o PAT `read:user` somente para consultar o GitHub.

## Critérios de segurança

- Não ler nomes de repositórios privados.
- Não publicar commits, hashes, conteúdo de PRs, mensagens nem dados de terceiros.
- Não ecoar segredos nos logs, nem salvá-los no repositório.
- Não transformar erro de API em métricas inventadas.
- Falhar quando token pertence a outra conta.
- Preservar o SVG válido anterior em caso de problema.
- Marcar métricas brutas de amostragem como obsoletas.

## Aceite operacional final

Somente marcar como concluído após:
1. `PROFILE_STATS_TOKEN` existir no secret;
2. Primeira execução manual autenticada terminar sem erro;
3. O SVG mostrar números obtidos do GraphQL (não placeholders);
4. O README mostrar a atualização real e a data de sincronização;
5. Os testes e a rotina automática estarem funcionando.

[Procedimento de ativação](./PROFILE_STATS_SETUP.md)
