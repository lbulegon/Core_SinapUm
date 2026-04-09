# MRFOO ARCHITECTURE SUBMISSION

Este documento reúne os artefatos necessários para avaliação arquitetural do orbital MrFoo no Core_SinapUm.

## Conteúdo do bundle

1. MRFOO_ARCHITECTURE_MANIFEST.md
2. MRFOO_CONTEXT.md
3. MRFOO_SERVICES_MAP.md
4. MRFOO_DATA_ARCHITECTURE.md
5. MRFOO_NOG_OVERVIEW.md
6. MRFOO_EVALUATION_REQUEST.md

## Caminho no servidor

/app/docs/architecture_bundle/mrfoo_architecture_bundle/

## Objetivo da submissão

Solicitar avaliação arquitetural do orbital MrFoo pelo architecture_intelligence_service.

## Contexto

MrFoo é um orbital gastronômico do Core_SinapUm orientado pelo conceito de NOG (Núcleo Operacional Gastronômico) e pelo agente de IA Chef Agnos.

## Artefatos incluídos

### Manifesto arquitetural
# MRFOO_ARCHITECTURE_MANIFEST
- Sistema: MrFoo | Tipo: Orbital especializado | Ecossistema: Core_SinapUm
- Natureza: Inteligência Operacional Gastronômica | Núcleo: NOG | Agente: Chef Agnos
- Tese: Orbital de inteligência operacional gastronômica, observa/interpreta/otimiza operação da cozinha
- Princípios: MrFoo é orbital SinapUm; NOG núcleo semântico; Chef Agnos agente IA; Railway transacional; SinapUm estratégico
- Domínios: cardápio, receitas, ingredientes, estoque, compras, produção, montagem, expedição
- Fluxo NOG: Cardápio→Receitas→Ingredientes→Estoque→Produção→Montagem→Expedição→Venda
- Chef Agnos: analítico, interpretativo, recomendador; não concentra CRUD
- Dados: Railway Postgres (transacional); SinapUm Postgres + Neo4j (estratégico, NOG, Chef Agnos)
- Serviços: mrfoo_app, mrfoo_api, mrfoo_sync_service, mrfoo_nog_service, chef_agnos_service
- Neo4j: nós Prato/Receita/Ingrediente/Estação/Pedido; relações USA, DEPENDE_DE, É_PREPARADO_EM
- Riscos: dispersão NOG, lógica analítica em transacional, sync layer informal, acoplamento MrFoo-Chef

### Contexto do sistema
MrFoo orbital gastronômico Core_SinapUm. Objetivo: estruturar operação com NOG, integrando transacional (Railway Postgres), inteligência operacional e análise relacional (SinapUm Postgres, Neo4j). Chef Agnos observa, interpreta e sugere melhorias.

### Mapa de serviços
mrfoo_app, mrfoo_api | mrfoo_sync_service | mrfoo_nog_service | chef_agnos_service

### Arquitetura de dados
Railway Postgres: usuários, pedidos, cadastros, CRUD. SinapUm Postgres: estados analíticos, telemetria. Neo4j: NOG grafo, dependências, gargalos, Chef Agnos.

### Descrição do NOG
Núcleo Operacional Gastronômico. Fluxo: Cardápio→Receitas→Ingredientes→Compras→Estoque→Produção→Montagem→Expedição→Venda. Organiza domínio, base semântica Chef Agnos.

### Solicitação de avaliação
Eixos: identidade orbital, aderência NOG, separação transacional/estratégico, responsabilidades, coesão, acoplamento, dados, Chef Agnos, inteligência operacional, evolução SinapUm. Entregáveis: score, pontos fortes, riscos, recomendações.