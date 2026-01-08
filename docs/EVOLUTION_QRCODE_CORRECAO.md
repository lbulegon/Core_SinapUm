# Correção: Problema de Geração de QR Code - Evolution API

## Problema Identificado

O endpoint `/instance/connect/{instance_id}` estava retornando apenas `{"count": 0}` ao invés do QR code em base64, impedindo a conexão do WhatsApp.

## Correções Implementadas

### 1. Melhorias no `EvolutionClient.get_qr()`

**Arquivo:** `app_whatsapp_gateway/clients/evolution_client.py`

- ✅ Adicionado suporte para múltiplos formatos de resposta da Evolution API
- ✅ Implementado método `_extract_qrcode_from_response()` que trata diferentes formatos:
  - `{"qrcode": {"base64": "...", "code": "..."}}`
  - `{"base64": "..."}`
  - `{"data": [{"base64": "..."}]}`
  - `{"code": "..."}`
- ✅ Adicionado retry automático quando QR code ainda não está disponível
- ✅ Tentativa de endpoint alternativo `/instance/qrcode/{instance_id}` se o principal falhar
- ✅ Melhor tratamento de erros HTTP (404, etc.)

### 2. Melhorias no `EvolutionClient.create_instance()`

**Arquivo:** `app_whatsapp_gateway/clients/evolution_client.py`

- ✅ Adicionado parâmetro `integration: 'WHATSAPP-BAILEYS'` na criação
- ✅ Aguarda 2 segundos após criar instância para inicialização
- ✅ Tenta obter QR code automaticamente após criar se não vier na resposta
- ✅ Melhor detecção de sucesso na criação (mesmo sem QR code imediato)

### 3. Melhorias no `InstanceService`

**Arquivo:** `app_whatsapp_gateway/services/instance_service.py`

- ✅ Melhor tratamento quando QR code não vem imediatamente na criação
- ✅ Tenta obter QR code automaticamente se não vier na resposta de criação
- ✅ Retorna status `waiting` quando QR code está sendo gerado (não é erro fatal)
- ✅ Melhor logging para debug

### 4. Melhorias no `_request()`

**Arquivo:** `app_whatsapp_gateway/clients/evolution_client.py`

- ✅ Adicionado parâmetro `raise_on_error` para controlar quando levantar exceções
- ✅ Melhor tratamento de erros HTTP (404, etc.)
- ✅ Retorna informações de status code nos erros

## Como Funciona Agora

1. **Criação de Instância:**
   - Cria a instância na Evolution API
   - Aguarda 2 segundos para inicialização
   - Tenta obter QR code automaticamente
   - Se não conseguir, marca como `CONNECTING` e permite tentar novamente depois

2. **Obtenção de QR Code:**
   - Tenta endpoint principal `/instance/connect/{instance_id}`
   - Extrai QR code de diferentes formatos de resposta
   - Se retornar `{"count": 0}`, aguarda 3 segundos e tenta novamente
   - Tenta endpoint alternativo `/instance/qrcode/{instance_id}` se necessário
   - Retorna status `waiting` se QR code ainda não está disponível (não é erro)

## Configurações Verificadas

- ✅ `CONFIG_SESSION_PHONE_VERSION: 2.3000.1025205472` (configurado no docker-compose)
- ✅ `QRCODE_LIMIT: 30` (configurado)
- ✅ `QRCODE_COLOR: '#198754'` (configurado)

## Próximos Passos para Teste

1. Reiniciar o serviço Evolution API:
   ```bash
   cd /root/Core_SinapUm/services/evolution_api_service
   docker compose restart evolution-api
   ```

2. Testar criação de instância:
   ```bash
   curl -X POST http://localhost:8000/instances/evolution/create \
     -H "Content-Type: application/json" \
     -d '{"shopper_id": "test_123", "instance_id": "test_instance"}'
   ```

3. Testar obtenção de QR code:
   ```bash
   curl http://localhost:8000/instances/evolution/test_instance/qr
   ```

4. Verificar logs:
   ```bash
   docker compose logs -f evolution-api
   ```

## Observações

- O QR code pode demorar alguns segundos para ser gerado após criar a instância
- Se o QR code não aparecer imediatamente, o sistema agora tenta automaticamente
- O status `waiting` indica que o QR code está sendo gerado (não é erro)
- Recomenda-se implementar polling no frontend para atualizar o QR code periodicamente

## Referências

- Evolution API Documentation: https://doc.evolution-api.com
- Versão: v2.2.3
- API URL: http://69.169.102.84:8004
