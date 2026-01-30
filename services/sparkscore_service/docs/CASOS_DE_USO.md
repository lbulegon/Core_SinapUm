# Casos de Uso - SparkScore

Casos de uso documentados para o serviço de análise orbital de peças criativas (Creative Engine / VitrineZap).

---

## 1. Story ideal para WhatsApp Status

**Objetivo:** Peça otimizada para circulação em stories do WhatsApp.

| Campo | Valor |
|-------|-------|
| text_overlay | "50% OFF - Chame no WhatsApp #oferta #promo" |
| caption | "Compartilhe com seus amigos" |
| hashtags | ["#oferta", "#promo"] |
| channel | whatsapp_status |
| format | story_vertical |

**Esperado:**
- Orbital CSV: score ≥ 70, circulation_triggers ≥ 2, channel_circulation_fit ≥ 0.8
- Orbital Semiótico: CTA detectado
- overall_score dentro da faixa esperada

---

## 2. Peça sem Call-to-Action

**Objetivo:** Peça promocional sem CTA explícito (whatsapp_click).

| Campo | Valor |
|-------|-------|
| text_overlay | "PROMOÇÃO" |
| caption | "Aproveite nossa oferta" |
| primary_goal | whatsapp_click |

**Esperado:**
- Insight de alto nível: "CTA ausente para objetivo WhatsApp"
- Orbital Semiótico: cta_detected = false

---

## 3. Texto excessivamente longo

**Objetivo:** Peça com obstáculos à circulação (texto > 50 palavras).

| Campo | Valor |
|-------|-------|
| text_overlay | Texto com ~60 palavras |
| caption | Continuação do texto |

**Esperado:**
- Orbital CSV: obstacle_score > 0.2
- Orbital Cognitivo: insight de texto muito longo (se aplicável)

---

## 4. Payload vazio (mínimo textual)

**Objetivo:** Peça sem overlay nem caption.

| Campo | Valor |
|-------|-------|
| text_overlay | "" |
| caption | "" |

**Esperado:**
- API retorna 200
- Orbitais retornam resultados (scores mais baixos ou neutros)
- Orbital CSV: obstacle_score = 0

---

## 5. Formato legado (sem piece aninhado)

**Objetivo:** Compatibilidade com payload antigo.

| Campo | Valor |
|-------|-------|
| text_overlay | No root |
| caption | No root |
| goal | No root |
| context | {channel, format} |

**Esperado:**
- Pipeline processa sem erro
- overall_score calculado

---

## Execução dos testes

```bash
cd /root/Core_SinapUm/services/sparkscore_service
pytest tests/ -v
```

### Por categoria

```bash
pytest tests/unit/ -v           # Unit tests
pytest tests/use_cases/ -v      # Casos de uso
pytest tests/test_edge_cases.py -v  # Edge cases
pytest tests/test_analyze_piece.py -v  # Integração API
```
