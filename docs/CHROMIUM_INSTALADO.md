# Chromium Instalado no Container Evolution API

## Problema Identificado ✅

O container Evolution API **não tinha Chromium instalado**, o que é **essencial** para gerar QR codes.

## Solução Aplicada ✅

### 1. Instalação do Chromium
```bash
apk add --no-cache chromium chromium-chromedriver
```

**Versão instalada:** Chromium 136.0.7103.113 Alpine Linux

### 2. Dockerfile Customizado
Criado `Dockerfile.evolution` que:
- Baseia na imagem `atendai/evolution-api:v2.2.3`
- Instala Chromium e Chromedriver
- Verifica instalação

### 3. Docker Compose Atualizado
```yaml
services:
  evolution-api:
    build:
      context: .
      dockerfile: Dockerfile.evolution
    # image: atendai/evolution-api:v2.2.3  # Comentado - usando build customizado
```

### 4. Container Reconstruído
- ✅ Imagem construída com sucesso
- ✅ Chromium instalado e funcionando
- ✅ Container reiniciado

## Verificação

```bash
docker exec evolution-api chromium --version
# Output: Chromium 136.0.7103.113 Alpine Linux
```

## Impacto Esperado

Com Chromium instalado, a Evolution API agora **deve conseguir**:
- ✅ Gerar QR codes
- ✅ Renderizar páginas do WhatsApp Web
- ✅ Processar autenticação

## Próximos Passos

1. ✅ Chromium instalado
2. ⏳ Testar criação de nova instância
3. ⏳ Verificar se QR code é gerado
4. ⏳ Monitorar logs para confirmar funcionamento

## Observação

O problema de `decodeFrame` pode persistir, mas agora com Chromium instalado, há mais chances de o QR code ser gerado. Se ainda não funcionar, o problema será especificamente do protocolo WebSocket com WhatsApp, não da falta de Chromium.
