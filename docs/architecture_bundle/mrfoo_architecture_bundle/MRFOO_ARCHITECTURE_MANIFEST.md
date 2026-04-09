# MRFOO_ARCHITECTURE_MANIFEST

## 1. Identificação

- Sistema: MrFoo
- Tipo: Orbital especializado
- Ecossistema: Core_SinapUm
- Natureza: Inteligência Operacional Gastronômica
- Núcleo conceitual: NOG — Núcleo Operacional Gastronômico
- Agente principal: Chef Agnos

---

## 2. Tese arquitetural

O MrFoo não é apenas um software de gestão gastronômica.
Ele é um orbital de inteligência operacional gastronômica dentro do ecossistema SinapUm.

Sua função é observar, interpretar e otimizar a operação real da cozinha, com base no modelo do NOG (Núcleo Operacional Gastronômico), integrando dados transacionais, modelagem relacional profunda e análise por agente de IA.

---

## 3. Objetivo do orbital

O MrFoo existe para:

- estruturar a operação gastronômica sob a ótica do NOG
- organizar cardápio, receitas, ingredientes, compras, estoque, produção, montagem e expedição
- transformar dados operacionais em inteligência de decisão
- permitir que o agente Chef Agnos observe a operação e produza recomendações
- integrar a camada transacional do produto à camada estratégica do SinapUm

---

## 4. Princípios arquiteturais

1. O MrFoo é um orbital do SinapUm, não um sistema isolado.
2. O NOG é o núcleo semântico do domínio.
3. O Chef Agnos é o agente de inteligência operacional do orbital.
4. Dados transacionais convencionais operam no Railway.
5. Dados estratégicos, analíticos e relacionais profundos operam no SinapUm.
6. O Neo4j do SinapUm é a base do grafo operacional do NOG.
7. O Postgres de serviços do SinapUm apoia serviços analíticos, estados e inteligência.
8. O MrFoo deve respeitar a arquitetura do Core_SinapUm e a lógica de orbitais.

---

## 5. Estrutura de domínio

### Domínios centrais
- cardápio
- receitas
- ingredientes
- estoque
- compras
- produção
- montagem
- expedição
- inteligência operacional

### Conceito nuclear
NOG — Núcleo Operacional Gastronômico

Fluxo estrutural do NOG:

Cardápio
→ Receitas
→ Ingredientes
→ Estoque
→ Produção
→ Montagem
→ Expedição
→ Venda

---

## 6. Papel do Chef Agnos

O Chef Agnos é o agente de IA do MrFoo.

Funções esperadas:
- observar sinais operacionais
- identificar gargalos
- avaliar complexidade operacional
- sugerir compras
- recomendar ajustes de cardápio
- apoiar decisões operacionais da cozinha

O Chef Agnos não deve concentrar lógica CRUD.
Seu papel é analítico, interpretativo e recomendador.

---

## 7. Arquitetura de dados

### Camada transacional
- provider: Railway
- database: PostgreSQL
- finalidade:
  - usuários
  - cadastros
  - pedidos
  - CRUD operacional
  - registros administrativos
  - dados de uso cotidiano

### Camada estratégica
- provider: SinapUm
- databases:
  - PostgreSQL de serviços
  - Neo4j
- finalidade:
  - NOG
  - causalidade operacional
  - observabilidade
  - inteligência operacional
  - estados analíticos
  - suporte ao Chef Agnos
  - relações profundas entre entidades da cozinha

---

## 8. Serviços esperados

### Camada MrFoo
- mrfoo_app
- mrfoo_api

### Camada de integração
- mrfoo_sync_service

### Camada semântica/operacional
- mrfoo_nog_service

### Camada inteligente
- chef_agnos_service

---

## 9. Fluxo arquitetural principal

MrFoo App / API
→ Railway Postgres
→ camada de sincronização
→ Core_SinapUm
→ Postgres de serviços
→ Neo4j
→ Chef Agnos
→ recomendações e inteligência devolvidas ao MrFoo

---

## 10. Uso do Neo4j

O Neo4j será usado para representar o NOG como grafo operacional.

Exemplos de nós:
- Prato
- Receita
- Ingrediente
- Estação
- Pedido
- Plano de compra
- Fornecedor

Exemplos de relações:
- USA
- DEPENDE_DE
- É_PREPARADO_EM
- GERA_CONSUMO_DE
- ABASTECE
- EXIGE
- COMPÕE

Objetivo:
- detectar gargalos
- medir dependências críticas
- avaliar impacto de ruptura
- apoiar simulações operacionais
- sustentar análise do Chef Agnos

---

## 11. Critérios desejados de avaliação arquitetural

Solicitamos que a arquitetura do MrFoo seja avaliada nos seguintes eixos:

1. identidade arquitetural do orbital
2. aderência ao NOG
3. separação entre camada transacional e camada estratégica
4. separação de responsabilidades
5. coesão de domínio
6. acoplamento entre serviços
7. arquitetura de dados
8. posicionamento do Chef Agnos
9. prontidão para inteligência operacional
10. capacidade evolutiva no ecossistema SinapUm

---

## 12. Riscos já percebidos

- dispersão de regras do NOG em múltiplas camadas
- excesso de lógica analítica na camada transacional
- sync layer pouco formalizada
- indefinição de contratos entre Railway e SinapUm
- risco de acoplamento excessivo entre MrFoo e Chef Agnos

---

## 13. Resultado esperado da avaliação

Esperamos receber:

- score geral
- score por eixo
- pontos fortes
- riscos arquiteturais
- recomendações priorizadas
- leitura sobre aderência ao SinapUm
- leitura sobre prontidão para escalar como orbital inteligente

---

## 14. Observação final

O MrFoo deve ser entendido como um orbital gastronômico do SinapUm.
Seu valor arquitetural não está apenas na gestão operacional, mas na capacidade de evoluir para inteligência operacional gastronômica baseada no NOG e interpretada pelo Chef Agnos.
