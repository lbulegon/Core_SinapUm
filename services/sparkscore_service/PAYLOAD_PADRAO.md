# Payload Padrão - Creative Engine → SparkScore

Este documento descreve o payload padrão oficial para integração do Creative Engine do VitrineZap com o SparkScore.

## Estrutura Completa

```json
{
  "source": "vitrinezap_creative_engine",
  "source_version": "1.0.0",
  "piece": {
    "piece_id": "ce_2026_01_16_000123",
    "piece_type": "image",
    "created_at": "2026-01-16T14:32:10Z",
    "asset": {
      "asset_url": "https://cdn.vitrinezap.com/creatives/abc123.png",
      "asset_base64": null,
      "mime_type": "image/png",
      "width": 1080,
      "height": 1920
    },
    "text_overlay": "PROMOÇÃO SÓ HOJE",
    "caption": "Chame no WhatsApp e aproveite",
    "hashtags": ["#promoção", "#oferta", "#whatsapp"],
    "language": "pt-BR"
  },
  "brand": {
    "brand_id": "vitrinezap",
    "name": "VitrineZap",
    "tone": "direto, amigável",
    "palette": ["#FFC700", "#111111"],
    "category": "varejo_local"
  },
  "objective": {
    "primary_goal": "whatsapp_click",
    "cta_expected": true,
    "conversion_type": "conversa_whatsapp"
  },
  "audience": {
    "segment": "varejo_local",
    "persona": "consumidor_proximo",
    "awareness_level": "medio"
  },
  "distribution": {
    "channel": "whatsapp_status",
    "format": "story_vertical",
    "duration_seconds": null
  },
  "context": {
    "locale": "pt-BR",
    "region": "BR-RS",
    "time_context": "oferta_imediata",
    "campaign_id": "camp_janeiro_2026"
  },
  "options": {
    "return_placeholders": true,
    "explainability_level": "full",
    "store_analysis": true
  }
}
```

## Estrutura Mínima

Para testes rápidos, este é o mínimo aceito:

```json
{
  "source": "vitrinezap_creative_engine",
  "piece": {
    "piece_id": "ce_test_001",
    "piece_type": "image",
    "text_overlay": "PROMOÇÃO HOJE",
    "caption": "Chame no WhatsApp"
  },
  "objective": {
    "primary_goal": "whatsapp_click"
  },
  "distribution": {
    "channel": "whatsapp_status",
    "format": "story_vertical"
  }
}
```

## Campos Obrigatórios

- `source`: String identificando a origem (padrão: "vitrinezap_creative_engine")
- `piece.piece_id`: ID único da peça
- `piece.piece_type`: Tipo da peça ("image", "text", "video")
- `objective.primary_goal`: Objetivo principal (ex: "whatsapp_click", "link_click", "purchase")
- `distribution.channel`: Canal de distribuição (ex: "whatsapp_status", "instagram_feed")
- `distribution.format`: Formato (ex: "story_vertical", "feed_horizontal")

## Campos Opcionais

Todos os outros campos são opcionais, mas recomendados para análise mais precisa:

- `piece.text_overlay`: Texto sobreposto na imagem
- `piece.caption`: Legenda/caption
- `piece.asset`: Informações do asset (URL ou base64)
- `brand.*`: Informações da marca
- `audience.*`: Informações da audiência
- `context.*`: Contexto adicional (locale, região, etc)
- `options.*`: Opções de processamento

## Goals Suportados

- `whatsapp_click`: Gerar cliques/conversas no WhatsApp
- `link_click`: Gerar cliques em links
- `purchase`: Gerar compras
- `download`: Gerar downloads
- `signup`: Gerar cadastros

## Canais Suportados

- `whatsapp_status`: Status do WhatsApp
- `whatsapp_story`: Story do WhatsApp
- `instagram_story`: Story do Instagram
- `instagram_feed`: Feed do Instagram
- `facebook_feed`: Feed do Facebook

## Formatos Suportados

- `story_vertical`: Story vertical (1080x1920)
- `feed_horizontal`: Feed horizontal (1080x1080 ou similar)
- `feed_vertical`: Feed vertical

## Exemplo de Uso

```bash
curl -X POST http://localhost:8006/api/v1/analyze_piece \
  -H "Content-Type: application/json" \
  -d @payload.json
```

## Compatibilidade

O SparkScore suporta tanto o payload padrão do Creative Engine quanto o formato antigo (para compatibilidade retroativa):

**Formato Antigo (ainda suportado):**
```json
{
  "text_overlay": "...",
  "caption": "...",
  "goal": "whatsapp_click",
  "context": {
    "channel": "...",
    "format": "..."
  }
}
```

O sistema detecta automaticamente qual formato está sendo usado e extrai os dados corretamente.


