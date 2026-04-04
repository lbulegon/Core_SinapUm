# SinapLint — dashboard do grafo arquitetural

Visualização opcional do JSON do motor (`architecture.visual` com nós enriquecidos: `risk`, `impact_score`, `color`, `size`).

## Arranque

```bash
cd tools/sinaplint-architecture-dashboard
npm install
npm run dev
```

Abre `http://localhost:5174`, cola o JSON completo de `python -m app_sinaplint check --json` (ou só o objeto `architecture`).

## Dados esperados

- `architecture.visual.nodes[]`: `id`, `risk` ou `risk_index`, `edges`, opcionalmente `impact_score`, `dependencies`, `in_cycles`, `fan_in`.
- `architecture.visual.edges[]`: `source`, `target` (strings).

O motor já devolve `links` compatíveis após o `ForceGraph2D` (mapeamento interno de `edges` → `links` no `App.tsx`).
