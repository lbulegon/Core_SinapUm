# ETAPA 1-2 — Análise e Plano de Mudança Mínima

## Como o modo atual funciona

1. **views.py** → `evaluate()` recebe POST com system_name, system_type, bundle_path, evaluation_mode
2. **services.py** → `start_architecture_evaluation()`:
   - Carrega artifact via `load_bundle_artifact()`
   - Mapeia evaluation_mode → cycle_type (EVALUATION_MODE_TO_CYCLE)
   - Chama architecture_intelligence_service: cycle/start, run_stage (por stage), report
   - Transforma com `_transform_report_to_ui_contract()` → contrato UI
3. **Contrato atual**: system_name, system_type, bundle_path, evaluation_mode, status, scores, strengths, risks, recommendations, final_verdict, stage_runs
4. **Template** → `renderResults(data)` preenche summaryGrid, scoresGrid, strengthsList, risksList, recommendationsList, finalVerdict

## Onde o Grand Jury deve ser inserido

Em `services.start_architecture_evaluation()`, logo após carregar o artifact:

```python
if evaluation_mode == "grand_jury":
    return run_grand_jury_evaluation(system_name, system_type, bundle_path, ...)
# fluxo atual
```

## Arquivos a alterar

| Arquivo | Alteração |
|---------|-----------|
| `services.py` | +1 bloco if no início (após load artifact) |
| `dashboard.html` | +1 option no select; +lógica em renderResults para jury_members |

## Arquivos novos

| Arquivo | Conteúdo |
|---------|----------|
| `grand_jury.py` | run_grand_jury_evaluation, run_jury_member, consolidate_jury_results, build_final_verdict |

## Contrato Grand Jury (extensão)

O retorno deve incluir os campos atuais (para compatibilidade) + novos:

- `jury_members`: lista de pareceres
- `consensus`: { agreements, disagreements }
- `shared_strengths`, `shared_risks`, `shared_recommendations`
- `verdict_detail`: { classification, summary, conditions }

---

## Exemplo de resposta JSON (Grand Jury)

```json
{
  "system_name": "MrFoo",
  "system_type": "Orbital",
  "bundle_path": "/app/docs/architecture_bundle/mrfoo_architecture_bundle",
  "evaluation_mode": "grand_jury",
  "status": "completed",
  "scores": { "final_score": 8.2, ... },
  "strengths": [...],
  "risks": [...],
  "recommendations": [...],
  "final_verdict": "Approved for Integration: Aprovado para integração...",
  "jury_members": [
    { "agent_name": "Chief Architect", "focus": "...", "score": 8.2, "opinion": "..." },
    ...
  ],
  "consensus": { "agreements": [...], "disagreements": [...] },
  "shared_strengths": [...],
  "shared_risks": [...],
  "shared_recommendations": [...],
  "verdict_detail": {
    "classification": "Approved for Integration",
    "summary": "Aprovado para integração. Pequenos ajustes recomendados.",
    "conditions": ["Formalizar contratos da sync layer"]
  }
}
```

---

## Instruções de teste

1. Acesse http://localhost:5000/architecture/
2. Selecione **Grand Jury** em Evaluation Mode
3. Mantenha System Name: MrFoo, Bundle Path: /app/docs/architecture_bundle/mrfoo_architecture_bundle
4. Clique em **Executar Avaliação**
5. Verifique no popup: Jury Members (7 cards), Consensus, Shared Findings, Final Verdict (classification, summary, conditions)
