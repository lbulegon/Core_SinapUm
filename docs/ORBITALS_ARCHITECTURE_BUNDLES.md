# Bundles de Avaliação Arquitetural — Orbitais do Core_SinapUm

Estrutura em `docs/architecture_bundle/` para submeter todos os orbitais à avaliação do Architecture Intelligence.

## Bundles disponíveis

| Orbital | Caminho | Descrição |
|---------|---------|-----------|
| MrFoo | `/app/docs/architecture_bundle/mrfoo_architecture_bundle` | Orbital gastronômico, NOG, Chef Agnos |
| Creative Engine | `/app/docs/architecture_bundle/creative_engine_architecture_bundle` | Geração criativa (texto, imagem), OpenMind |
| DDF | `/app/docs/architecture_bundle/ddf_architecture_bundle` | Detect & Delegate Framework, orquestração MCP |
| ShopperBot | `/app/docs/architecture_bundle/shopperbot_architecture_bundle` | IA vendedora VitrineZap |
| SparkScore | `/app/docs/architecture_bundle/sparkscore_architecture_bundle` | Análise psicológica e semiótica (Peirce) |

## Estrutura de cada bundle

- `{ORBITAL}_ARCHITECTURE_SUBMISSION.md` — documento principal
- `{ORBITAL}_ARCHITECTURE_MANIFEST.md` — manifesto arquitetural
- `{ORBITAL}_CONTEXT.md` — contexto do sistema
- `{ORBITAL}_SERVICES_MAP.md` — mapa de serviços
- `{ORBITAL}_DATA_ARCHITECTURE.md` — arquitetura de dados
- `{ORBITAL}_NOG_OVERVIEW.md` — visão do domínio
- `{ORBITAL}_EVALUATION_REQUEST.md` — solicitação de avaliação

## Como usar

1. Acesse `/architecture/`
2. Use o preset **Bundle Path** para selecionar o orbital
3. Ou informe manualmente: `/app/docs/architecture_bundle/{orbital}_architecture_bundle`
4. Selecione Evaluation Mode (Full Cycle, Grand Jury, Grand Jury Senate)
5. Executar Avaliação

## Caminhos (Docker vs Host)

- **Docker**: `/app/docs/architecture_bundle/{orbital}_architecture_bundle`
- **Host**: `/root/Core_SinapUm/docs/architecture_bundle/{orbital}_architecture_bundle`

O `load_bundle_artifact` tenta ambos automaticamente.
