# Prompt: Orbital Circulação Simbólica Vetorial (CSV)

## Objetivo

Criar o **Orbital Circulação Simbólica Vetorial (CSV)** dentro do SparkScore, analisando como os símbolos da peça criativa **circulam** em direção ao público e ao objetivo (fluxo vetorial). O orbital deve ser implementado como **placeholder inicial** (`enabled: false`) para não quebrar nada existente. Depois, pode ser ativado quando a lógica estiver pronta.

---

## Conceito Teórico: Circulação Simbólica Vetorial

**Circulação Simbólica Vetorial (CSV)** analisa o **fluxo vetorial** dos símbolos na peça:

- **Vetor** = direção + magnitude: para onde o signo aponta e com que intensidade
- **Circulação** = capacidade da mensagem de se propagar (compartilhar, encaminhar, viralizar)
- **Simbólica** = natureza dos signos que compõem a peça (ícone, índice, símbolo – Peirce)

Métricas sugeridas:
- **Direção do vetor**: a peça aponta claramente para ação/compartilhamento?
- **Densidade de circulação**: sinais que convidam à propagação (hashtags, "compartilhe", "envie", "marque")
- **Canal-circulação**: adequação do formato ao canal (ex: story vertical para WhatsApp status)
- **Clareza do alvo**: quem deve receber/agir (receptor claro)?
- **Obstáculos à circulação**: ruído, ambiguidade, excesso de texto que dificulta o encaminhamento

---

## Especificação Técnica

### Identificadores

- **orbital_id**: `csv` (Circulação Simbólica Vetorial)
- **name**: `"Orbital Circulação Simbólica Vetorial (CSV)"`
- **version inicial**: `"0.1.0"` (placeholder) → `"1.0.0"` (ativo)

### raw_features (MVP heurístico)

| Feature | Tipo | Descrição |
|--------|------|-----------|
| `circulation_triggers_found` | int | Quantidade de gatilhos de circulação (hashtags, "compartilhe", "envie", "marque", "chame") |
| `hashtag_count` | int | Número de hashtags |
| `share_invitation_detected` | bool | Detectou convite explícito a compartilhar |
| `vector_clarity` | float (0–1) | Clareza da direção do vetor (objetivo + CTA) |
| `channel_circulation_fit` | float (0–1) | Adequação do formato ao canal de circulação |
| `obstacle_score` | float (0–1) | Obstáculos à circulação (texto longo, ambiguidade) |

### top_features (strings)

Exemplos: `circulation_triggers_detected`, `high_vector_clarity`, `good_channel_fit`, `low_obstacle`.

### Heurística de score (0–100)

- Base: 60
- `+10` por `share_invitation_detected`
- `+5 * circulation_triggers_found` (máx +15)
- `+15 * vector_clarity`
- `+10 * channel_circulation_fit`
- `-20 * obstacle_score`

### Heurística de confidence (0–1)

- Base: 0.5
- Aumenta se houver hashtags, CTA e formato adequado ao canal

### rationale (texto)

Exemplo:  
`"Vetor com direção moderada. 2 gatilhos de circulação (hashtags). Bom ajuste ao formato story. Baixo obstáculo à circulação."`

---

## Passos de Implementação (sem quebrar o existente)

### 1. Criar o arquivo do orbital

**Arquivo:** `app/orbitals/csv_orbital.py`

- Herdar de `BaseOrbital`
- `orbital_id="csv"`, `name="Orbital Circulação Simbólica Vetorial (CSV)"`
- Implementar `analyze(payload) -> OrbitalResult`
- Fase 1: retornar **placeholder** (`status="placeholder"`, `score=None`, `confidence=None`) com `rationale` descritivo
- Fase 2: implementar heurísticas e retornar `status="active"` com scores

### 2. Registrar no registry

**Arquivo:** `app/orbitals/registry.py`

- Importar: `from app.orbitals.csv_orbital import CsvOrbital`
- Adicionar no `_orbital_classes`: `"csv": CsvOrbital`

### 3. Configurar no YAML

**Arquivo:** `config/orbitals.yaml`

Na seção `orbital_configs`, adicionar:

```yaml
  csv:
    enabled: false
    description: "Circulação Simbólica Vetorial: fluxo vetorial, propagação, adequação ao canal (placeholder)"
```

### 4. Ordem de execução

O pipeline já itera sobre `get_active_orbitals()` e `get_placeholder_orbitals()`. Com `enabled: false`, o CSV será executado como placeholder junto com narrative, cultural, etc., sem impacto em overall_score.

---

## Keywords sugeridas para heurísticas

**Gatilhos de circulação:**
- `compartilhe`, `envie`, `marque`, `repasse`, `encaminhe`, `chame`, `convide`, `indique`, `divulga`

**Hashtags:** contagem de tokens que começam com `#`

**Formato-canal:** mapear `distribution.format` (ex: `story_vertical`) e `distribution.channel` (ex: `whatsapp_status`) para score de adequação.

---

## Checklist de integração

- [ ] Criar `app/orbitals/csv_orbital.py`
- [ ] Registrar `CsvOrbital` em `registry.py`
- [ ] Adicionar entrada `csv` em `config/orbitals.yaml` com `enabled: false`
- [ ] Executar pipeline existente e verificar que não quebrou
- [ ] (Opcional) Implementar heurísticas completas e ativar com `enabled: true`
- [ ] Atualizar `README.md` do SparkScore com menção ao orbital CSV

---

## Exemplo de OrbitalResult (placeholder)

```json
{
  "orbital_id": "csv",
  "name": "Orbital Circulação Simbólica Vetorial (CSV)",
  "status": "placeholder",
  "score": null,
  "confidence": null,
  "rationale": "Orbital CSV mediria a circulação simbólica vetorial da peça: direção do vetor (emissor→receptor), gatilhos de propagação (hashtags, compartilhe, envie), adequação do formato ao canal e obstáculos à circulação. Implementação futura.",
  "top_features": [],
  "raw_features": {},
  "version": "0.1.0"
}
```

---

## Exemplo de OrbitalResult (ativo, após implementação)

```json
{
  "orbital_id": "csv",
  "name": "Orbital Circulação Simbólica Vetorial (CSV)",
  "status": "active",
  "score": 78.0,
  "confidence": 0.62,
  "rationale": "Vetor com direção clara. 2 gatilhos de circulação (hashtags). Bom ajuste ao formato story vertical para WhatsApp. Baixo obstáculo à circulação.",
  "top_features": ["circulation_triggers_detected", "high_vector_clarity", "good_channel_fit"],
  "raw_features": {
    "circulation_triggers_found": 2,
    "hashtag_count": 2,
    "share_invitation_detected": false,
    "vector_clarity": 0.85,
    "channel_circulation_fit": 0.9,
    "obstacle_score": 0.15
  },
  "version": "1.0.0"
}
```

---

## Compatibilidade

- Não alterar `base_orbital.py`, `orbital_result.py`, `pipeline.py` ou outros orbitais existentes
- O novo orbital é **aditivo**: apenas novo arquivo + 2 linhas no registry + entrada no YAML
- Com `enabled: false`, o overall_score e os insights continuam iguais
