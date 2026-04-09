# SHOPPERBOT ARCHITECTURE SUBMISSION

Este documento reúne os artefatos necessários para avaliação arquitetural do orbital ShopperBot no Core_SinapUm.

## Conteúdo do bundle

1. SHOPPERBOT_ARCHITECTURE_MANIFEST.md
2. SHOPPERBOT_CONTEXT.md
3. SHOPPERBOT_SERVICES_MAP.md
4. SHOPPERBOT_DATA_ARCHITECTURE.md
5. SHOPPERBOT_NOG_OVERVIEW.md
6. SHOPPERBOT_EVALUATION_REQUEST.md

## Caminho no servidor

/app/docs/architecture_bundle/shopperbot_architecture_bundle/

## Objetivo da submissão

Solicitar avaliação arquitetural do orbital ShopperBot pelo architecture_intelligence_service.

## Contexto

ShopperBot é um orbital de IA vendedora do Core_SinapUm, integrado ao VitrineZap para atendimento e conversão em vendas.

## Artefatos incluídos

### Manifesto arquitetural
- Sistema: ShopperBot | Tipo: Orbital especializado | Ecossistema: Core_SinapUm
- Natureza: IA vendedora VitrineZap
- Tese: Orbital de atendimento conversacional com inteligência de vendas
- Princípios: ShopperBot é orbital SinapUm; integração com Creative Engine; intent/classify; handoff

### Contexto do sistema
ShopperBot orbital de IA vendedora Core_SinapUm. Objetivo: atender conversas, classificar intenções, recomendar produtos e realizar handoff quando necessário.

### Mapa de serviços
shopperbot_service (7030) | intent_service | recommendation_service | creative_service | handoff_service

### Solicitação de avaliação
Eixos: identidade orbital, separação de responsabilidades, integração com IA, evolução SinapUm. Entregáveis: score, pontos fortes, riscos, recomendações.
