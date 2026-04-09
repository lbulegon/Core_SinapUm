# DDF ARCHITECTURE MANIFEST

## 1. Identificação

- Sistema: DDF (Detect & Delegate Framework)
- Tipo: Orbital especializado
- Ecossistema: Core_SinapUm
- Natureza: Orquestração e roteamento de chamadas

---

## 2. Tese arquitetural

O DDF é um orbital de detecção e delegação dentro do ecossistema SinapUm.

Sua função é rotear e orquestrar chamadas entre ferramentas MCP e provedores (prompt, openmind, pipeline, etc.).

---

## 3. Objetivo do orbital

O DDF existe para:

- detectar intenções de chamadas
- delegar execução a provedores configuráveis
- integrar com mcp_service e tools
- suportar context_pack e trace_id

---

## 4. Princípios arquiteturais

1. O DDF é um orbital do SinapUm.
2. Providers configuráveis via config/*.yaml.
3. Integração com gateway MCP.
4. Deve respeitar a arquitetura do Core_SinapUm.
