# Architecture Senate — Análise e Proposta Mínima

## BLOCO 1 — Estado Atual

### Como o Grand Jury funciona hoje

1. **services.py**: Se `evaluation_mode == "grand_jury"`, chama `run_grand_jury_evaluation()` e retorna.
2. **grand_jury.py**: Executa 7 jurados, consolida resultados, gera veredito. Retorna contrato com `jury_members`, `consensus`, `shared_strengths`, `shared_risks`, `shared_recommendations`, `verdict_detail`.
3. **Template**: Quando `jury_members` existe, exibe abas (Jury Members, Consensus, Shared Findings, Final Verdict).

### Onde encaixar o Senate

- **services.py**: Adicionar `if evaluation_mode == "senate": return run_senate_evaluation(...)` antes do Grand Jury.
- **Arquivo novo**: `app_architecture_intelligence/senate.py` — chama Grand Jury, adiciona debate, consenso, veredito institucional.

### Menor conjunto de mudanças

| Arquivo | Alteração |
|---------|-----------|
| `senate.py` | **NOVO** — lógica completa do Senate |
| `services.py` | +5 linhas — branch senate |
| `dashboard.html` | +opção Senate no select, +helper, +seções Senate na UI |

---

## BLOCO 2 — Proposta Arquitetural

### Reutilização do Grand Jury

```
run_senate_evaluation()
  → jury_report = run_grand_jury_evaluation(...)  # reutiliza 100%
  → senate_debate = run_senate_debate(jury_report)
  → consensus_matrix = build_consensus_matrix(jury_report, senate_debate)
  → senate_verdict = build_senate_verdict(...)
  → return transform_senate_report_to_ui_contract(...)
```

### Camada Senate (nova)

- **Debate**: Tópicos extraídos de risks/recommendations/opinions. Entradas estruturadas (agent, position, responds_to, response).
- **Consensus Matrix**: Por tópico, agreement_level (high/medium/low) e notes.
- **Senate Verdict**: classification, summary, conditions, strategic_potential.

---

## BLOCO 3 — Implementação

- **senate.py**: run_senate_evaluation, run_senate_debate, build_consensus_matrix, build_senate_verdict
- **services.py**: branch `if evaluation_mode == "senate"` → run_senate_evaluation
- **dashboard.html**: opção Senate, helper text, senateWrapper com 6 abas

---

## BLOCO 4 — Contrato JSON (Senate)

```json
{
  "evaluation_mode": "senate",
  "jury_members": [...],
  "senate_debate": [{"topic": "...", "entries": [...], "debate_result": "..."}],
  "consensus_matrix": [{"topic": "...", "agreement_level": "high|medium|low", "notes": "..."}],
  "senate_verdict": {"classification": "...", "summary": "...", "conditions": [...], "strategic_potential": "high|medium|low"}
}
```

---

## BLOCO 5 — Teste

1. Acesse `/architecture/`
2. System Name: MrFoo, Bundle Path: `/app/docs/architecture_bundle/mrfoo_architecture_bundle`
3. Evaluation Mode: **Senate**
4. Executar Avaliação
5. Verificar: Senate Verdict, Consensus Matrix, Senate Debate, Jury Members, Shared Findings

---

## BLOCO 6 — Extensibilidade futura

- **run_senate_debate**: substituir heurística por chamadas LLM por agente/tópico
- **extract_debate_topics**: LLM para inferir tópicos refinados
- **build_consensus_matrix**: LLM para analisar divergências e classificar agreement_level
