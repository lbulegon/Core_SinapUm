# Política de bloqueio (`--smart-block`)

Ficheiro JSON opcional (`--policy` ou `SINAPLINT_POLICY_JSON`). Chaves suportadas:

| Chave | Significado |
|-------|-------------|
| `fail_under_score` | Igual ao `--fail-under` (o CLI sobrescreve com o valor do limiar passado no comando). |
| `block_on_new_cycles` | Bloquear se existirem novos grupos SCC vs baseline. |
| `use_scc_new_groups` | Se `true`, usa `new_cycles_count` (conjunto SCC); se `false`, usa contagem simples `new_cycles`. |
| `block_on_coupling_increase` | Bloquear se o peso total de dependências entre apps aumentar. |
| `min_coupling_weight_delta` | Só aplica o bloqueio de acoplamento se `total_dependency_weight_delta >= N`. |
| `block_on_coupling_score_increase` | Bloquear se a soma de `coupling_score` por app aumentar. |
| `max_score_drop` | Bloquear se `score_change` for **inferior** a este valor (ex.: `-5` bloqueia -6 ou pior). |

Sem `--delta-base`, as regras que dependem de delta são ignoradas (fica apenas o score mínimo).
