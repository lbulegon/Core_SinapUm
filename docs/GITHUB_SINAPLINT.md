# SinapLint no GitHub Actions

## O que faz

O workflow [`.github/workflows/sinaplint.yml`](../.github/workflows/sinaplint.yml) corre em **push** e **pull request** para `main`, `master` e `develop`:

1. Checkout do repositório com **histórico completo** (`fetch-depth: 0`) para permitir `git worktree` na branch base.
2. Python 3.12.
3. `python3 -m app_sinaplint check --json -o sinaplint-report.json --fail-under 80`
4. Em **pull requests**, o mesmo comando inclui **`--delta-base <github.base_ref>`** (ex.: `main`): compara o HEAD do PR com o estado analisado da branch base e acrescenta ao JSON os campos **`delta`**, **`delta_summary`** (evolução de score, novos SCC, acoplamento, tendência).
5. **Sumário** no separador *Summary* do workflow (inclui `delta_summary` quando existir).
6. **Artefacto** `sinaplint-report` com o JSON completo (grafo, insights, `clean_architecture`, `delta`, etc.).
7. Em **pull requests**: geração de `sinaplint-pr.md` com `python3 -m app_sinaplint pr-comment -i sinaplint-report.json` (layout “premium”: risco, delta, prioridade de refactor) e publicação desse Markdown como **comentário único** (marcador `<!-- sinaplint-ci -->`).
8. Em **pull requests**, o check usa **`--smart-block`** com [`.github/sinaplint-policy.json`](../.github/sinaplint-policy.json): bloqueia por score, novos SCC, acoplamento (peso) e queda de score vs baseline. O job **falha** se a política bloquear ou se o score for inferior a **80** (via `--fail-under`, alinhado com `fail_under_score` na política).

## Requisitos

- A raiz do repositório Git deve ser a pasta onde existe o pacote `app_sinaplint/` (monólito Core_SinapUm).
- Não é necessário instalar `requirements.txt` completo: o motor SinapLint usa sobretudo biblioteca padrão + AST.
- **Delta no PR:** o runner faz `git fetch` da branch base e um **worktree** nessa ref; sem histórico suficiente ou sem remoto `origin` apontando para o repositório base, `delta.base_available` pode ser `false` (ver `delta.reason` no JSON).

## Modo delta (local ou outro CI)

```bash
python3 -m app_sinaplint check --delta-base main --json -o report.json
```

O valor é normalizado para `origin/<branch>` quando possível (ex.: `main` → `origin/main`).

O núcleo de comparação vive em `app_sinaplint/engine/delta/` (`delta_analyzer`, `delta_formatter`, `git_utils`, `comment_formatter`). O ficheiro `engine/delta_analysis.py` mantém reexports para imports antigos.

## Comentário PR (Markdown)

```bash
python3 -m app_sinaplint pr-comment -i sinaplint-report.json -o sinaplint-pr.md --sha "$GITHUB_SHA" --base-ref main
```

## Personalizar

| Objetivo | Onde |
|----------|------|
| Alterar limiar (ex.: 85) | `--fail-under 85` no workflow |
| Outros ramos | Lista `branches:` em `on:` |
| Desativar comentário no PR | Remover o passo *Comentário único no PR* |

## PRs a partir de forks

Comentários no PR podem falhar por permissões do `GITHUB_TOKEN`. O sumário e o artefacto continuam disponíveis no workflow da fork.

## Webhook / GitHub App

Esta integração é **CI por commit** via Actions. Um **GitHub App** à parte seria necessário para eventos fora do repositório (ex.: comentários em issues noutro org) ou automação adicional.
