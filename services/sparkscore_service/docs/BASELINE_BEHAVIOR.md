# Baseline Behavior - SparkScore Service

**Data:** 2026-01-14  
**Versão:** 1.0.0

## Objetivo

Documentar o comportamento atual do SparkScore Service antes de qualquer evolução. Este documento serve como referência para garantir compatibilidade.

## Comportamento Atual dos Endpoints

### POST /sparkscore/analyze

**Comportamento:**
1. Recebe `stimulus` (obrigatório) e `context` (opcional)
2. Executa análise completa:
   - Classificação orbital (0-6)
   - Análise semiótica (Peirce)
   - Análise psicológica (atração, risco, ruído)
   - Análise métrica (engajamento, conversão)
   - Processamento pelo motor do orbital dominante
3. Calcula SparkScore final (0.0-1.0) como média ponderada
4. Calcula PPA baseado no orbital dominante
5. Gera recomendações baseadas nos scores
6. Retorna tudo em `{"success": true, "result": {...}}`

**Algoritmo de SparkScore:**
- Pesos: orbital (0.3), semiótico (0.2), psico (0.25), métrica (0.15), motor (0.1)
- Score final: média ponderada, limitado entre 0.0 e 1.0

**Algoritmo de PPA:**
- Orbital 2 → PPA "nascente" (confidence * 0.5)
- Orbital 3 → PPA "validado" (confidence * 0.7)
- Orbital 4 → PPA "ativo" (confidence * 0.9)
- Orbital 6 → PPA "cristalizado" (confidence * 1.0)
- Outros → PPA "inativo" (confidence 0.0)

### POST /sparkscore/classify-orbital

**Comportamento:**
1. Normaliza estímulo semioticamente
2. Extrai sinais (familiaridade, coerência, antecipação, etc.)
3. Calcula score para cada orbital (0-6)
4. Determina orbital dominante (maior score)
5. Determina orbitais secundários (score > 0.3)
6. Calcula estabilidade e impacto
7. Gera justificativa textual

**Algoritmo de Classificação:**
- Orbital 0 (Ruído): (1 - familiaridade) * (1 - coerência)
- Orbital 1 (Reconhecimento): familiaridade * (1 - antecipação)
- Orbital 2 (Expectativa): antecipação * familiaridade
- Orbital 3 (Alinhamento): coerência * (1 - intensidade_emocional)
- Orbital 4 (Engajamento): intensidade_emocional * coerência
- Orbital 5 (Memória): familiaridade * tempo_exposição
- Orbital 6 (Efeito Mandela): recorrência_coletiva * familiaridade

### POST /sparkscore/semiotic

**Comportamento:**
1. Analisa tipo de Peirce (ícone, índice, símbolo)
2. Extrai categorias semióticas
3. Detecta potencial de efeito Mandela
4. Calcula coerência simbólica
5. Retorna análise completa

**Algoritmo de Peirce:**
- Ícone: detecta imagem ou palavras-chave visuais
- Índice: detecta palavras-chave de causalidade/referência
- Símbolo: detecta palavras-chave de linguagem/convenção

### POST /sparkscore/psycho

**Comportamento:**
1. Analisa fatores de atração (emoções positivas, desejo, benefícios, exclusividade)
2. Analisa fatores de risco (medo, incerteza, perda, resultados negativos)
3. Analisa fatores de ruído (complexidade, ambiguidade, falta de contexto)
4. Calcula intensidade emocional
5. Calcula score psicológico geral

**Algoritmo:**
- Atração: soma de scores de fatores, normalizado
- Risco: soma de scores de fatores, normalizado
- Ruído: média de complexidade, ambiguidade, falta de contexto
- Score geral: atração * 0.5 + (1 - risco) * 0.3 + (1 - ruído) * 0.2

### POST /sparkscore/metric

**Comportamento:**
1. Calcula probabilidade de engajamento (CTA, urgência, curiosidade, prova social)
2. Calcula probabilidade de conversão (proposta de valor, sinais de confiança, simplicidade, exclusividade)
3. Calcula métricas de qualidade (comprimento, clareza, relevância)
4. Calcula score métrico geral

**Algoritmo:**
- Engajamento: média de fatores (0.25 cada), ajustado por histórico (0.7 atual + 0.3 histórico)
- Conversão: média de fatores (0.25 cada), ajustado por histórico (0.7 atual + 0.3 histórico)
- Qualidade: comprimento (0.3) + clareza (0.4) + relevância (0.3)
- Score geral: engajamento * 0.4 + conversão * 0.4 + qualidade * 0.2

## Padrões de Resposta

### Estrutura Padrão
```json
{
  "success": true,
  "result": {...}
}
```

### Campos Obrigatórios em /analyze
- `sparkscore` (float 0.0-1.0)
- `ppa` (dict com `status`, `stage`, `confidence`, `profile`)
- `orbital` (dict com `orbital_dominante`, `orbitais_secundarios`, etc.)
- `semiotic` (dict com análise semiótica)
- `psycho` (dict com análise psicológica)
- `metric` (dict com análise métrica)
- `motor_result` (dict com resultado do motor)
- `recommendations` (list de strings)

## Tratamento de Erros

### Status Codes
- `200`: Sucesso
- `400`: Bad Request (stimulus obrigatório faltando)
- `500`: Erro interno (exceção não tratada)

### Formato de Erro
```json
{
  "detail": "mensagem de erro"
}
```

## Limitações Conhecidas

1. **Sem persistência:** Análises não são salvas
2. **Sem versionamento:** Não há controle de versão de pipeline
3. **Sem rastreabilidade:** Não há IDs de análise
4. **Sem cache:** Cada requisição recalcula tudo
5. **Sem testes:** Nenhum teste automatizado
6. **Sem observability:** Logs básicos, sem métricas

## Notas de Implementação

- Todos os scores são normalizados entre 0.0 e 1.0
- Algoritmos são determinísticos (mesmo input = mesmo output)
- Não há dependências externas (APIs, bancos de dados)
- Configuração de orbitais vem de `config/orbitals.yaml`
- Motores são instanciados via factory pattern

## Garantias de Compatibilidade

Para manter compatibilidade, NÃO alterar:
- Estrutura de resposta dos endpoints existentes
- Algoritmos de cálculo (sem versionamento)
- Nomes de campos em responses
- Status codes
- Formato de erro
- Valores válidos de orbitais (0-6)
- Valores válidos de PPA status

