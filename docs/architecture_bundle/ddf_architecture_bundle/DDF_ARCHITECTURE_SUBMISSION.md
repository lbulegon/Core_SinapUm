# DDF ARCHITECTURE SUBMISSION

Este documento reúne os artefatos necessários para avaliação arquitetural do orbital DDF (Detect & Delegate Framework) no Core_SinapUm.

## Conteúdo do bundle

1. DDF_ARCHITECTURE_MANIFEST.md
2. DDF_CONTEXT.md
3. DDF_SERVICES_MAP.md
4. DDF_DATA_ARCHITECTURE.md
5. DDF_NOG_OVERVIEW.md
6. DDF_EVALUATION_REQUEST.md

## Caminho no servidor

/app/docs/architecture_bundle/ddf_architecture_bundle/

## Objetivo da submissão

Solicitar avaliação arquitetural do orbital DDF pelo architecture_intelligence_service.

## Contexto

DDF (Detect & Delegate Framework) é um orbital de detecção e delegação do Core_SinapUm, responsável por rotear e orquestrar chamadas entre ferramentas e provedores.

## Artefatos incluídos

### Manifesto arquitetural
- Sistema: DDF | Tipo: Orbital especializado | Ecossistema: Core_SinapUm
- Natureza: Detect & Delegate Framework
- Tese: Orbital de orquestração e roteamento de chamadas MCP/tools
- Princípios: DDF é orbital SinapUm; providers configuráveis; integração com mcp_service

### Contexto do sistema
DDF orbital de orquestração Core_SinapUm. Objetivo: detectar intenções e delegar execução a provedores (prompt, openmind, pipeline, etc.).

### Mapa de serviços
ddf_service | providers/ | mcp_tools/ | config/*.yaml

### Solicitação de avaliação
Eixos: identidade orbital, separação de responsabilidades, integração com MCP, evolução SinapUm. Entregáveis: score, pontos fortes, riscos, recomendações.
