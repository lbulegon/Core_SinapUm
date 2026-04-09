# Architecture Intelligence — Implementação Completa

## BLOCO 1 — Análise do padrão atual

- **Home MCP SinapUm:** `app_sinapum/templates/app_sinapum/home.html` + `app_sinapum/views.home`
- **Cards:** `.services-grid` com `.service-card` (classes: primary, creative, mlflow)
- **Rotas:** `setup/urls.py` — path('', views.home), includes para apps
- **Padrão de módulo:** app_creative_engine — views em `views.py`, urls em `api/urls.py`, template em `templates/app_creative_engine/test.html`

## BLOCO 2 — Arquivos criados/alterados

| Arquivo | Ação |
|---------|------|
| `app_architecture_intelligence/views.py` | Criado — dashboard + evaluate |
| `app_architecture_intelligence/urls.py` | Criado — / e /evaluate |
| `app_architecture_intelligence/services.py` | Criado — adapter + load_bundle + transform |
| `app_architecture_intelligence/templates/.../dashboard.html` | Criado — UI completa |
| `setup/urls.py` | Alterado — path architecture/ |
| `app_sinapum/templates/.../home.html` | Alterado — card + nav link |
| `docker-compose.yml` | Alterado — ARCHITECTURE_SERVICE_URL no web |
| `docs/architecture_bundle/mrfoo_architecture_bundle/` | Copiado para Core_SinapUm/docs/ |

## BLOCO 4 — Integração com architecture_intelligence_service

- **Adapter:** `services.start_architecture_evaluation()` chama HTTP:
  - POST /architecture/cycle/start
  - POST /architecture/cycle/{id}/run_stage?stage=...
  - GET /architecture/cycle/{id}/report
- **Mock:** Se serviço indisponível ou bundle não encontrado → `_get_mock_response()`
- **Substituir mock:** Remover try/except em `start_architecture_evaluation` e garantir serviço + bundle

## BLOCO 5 — Como testar

1. Subir serviços: `docker compose up -d web architecture_intelligence_service`
2. Acessar: http://localhost:5000/
3. Clicar no card "Architecture Intelligence"
4. Preencher (defaults MrFoo) e clicar "Executar Avaliação"
5. Bundle path: `/app/docs/architecture_bundle/mrfoo_architecture_bundle` (Docker) ou `/root/docs/mrfoo_architecture_bundle` (host)
