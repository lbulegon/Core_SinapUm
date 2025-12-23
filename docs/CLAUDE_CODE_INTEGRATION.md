# Integração DDF com Claude Code

## 🎯 Visão Geral

O DDF pode ser usado diretamente pelo **Claude Code** através do Model Context Protocol (MCP), permitindo que Claude:

1. **Use o DDF como barramento de IAs** - Claude não precisa escolher qual IA usar
2. **Execute tarefas complexas** - Pipelines que combinam múltiplas IAs e ferramentas
3. **Beneficiar-se de auditoria centralizada** - Todas as operações registradas
4. **Respeitar políticas de segurança** - Bloqueios e limites aplicados automaticamente

## 🚀 Configuração

### 1. Instalar Dependências

```bash
cd /root/ddf
pip install -r requirements.txt
```

### 2. Configurar Claude Code

Adicionar o DDF como servidor MCP no Claude Code:

```bash
claude mcp add ddf \
  --command "python" \
  --args "-m" "app.mcp_tools.mcp_server" \
  --env "DATABASE_URL=postgresql://ddf:ddf@postgres:5432/ddf"
```

Ou editar `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "ddf": {
      "command": "python",
      "args": ["-m", "app.mcp_tools.mcp_server"],
      "env": {
        "DATABASE_URL": "postgresql://ddf:ddf@postgres:5432/ddf",
        "REDIS_URL": "redis://redis:6379/0"
      }
    }
  }
}
```

## 📋 Ferramentas Disponíveis

### `ddf_detect`
Classifica uma tarefa em categoria e intenção.

**Exemplo:**
```
Claude Code: "Use ddf_detect para classificar: 'Criar uma imagem de um gato'"
```

**Resposta:**
```json
{
  "category": "imagem",
  "intent": "gerar",
  "confidence": 0.95
}
```

### `ddf_execute`
Executa tarefa completa: detecta, delega e executa.

**Exemplo:**
```
Claude Code: "Use ddf_execute para: 'Escrever um artigo sobre IA'"
```

**Resposta:**
```json
{
  "request_id": "abc123",
  "category": "escrita",
  "provider": "claude",
  "result": {
    "output": "Artigo completo sobre IA..."
  }
}
```

### `ddf_generate_text`
Gera texto usando IA apropriada.

**Exemplo:**
```
Claude Code: "Use ddf_generate_text com prompt: 'Explique o que é MCP'"
```

### `ddf_generate_image`
Gera imagem usando IA apropriada.

**Exemplo:**
```
Claude Code: "Use ddf_generate_image com prompt: 'Um gato astronauta'"
```

### `ddf_list_categories`
Lista todas as categorias disponíveis.

### `ddf_list_providers`
Lista providers disponíveis para uma categoria.

## 💡 Casos de Uso

### Caso 1: Implementar Feature Completa

```
Claude Code: "Implementar feature do issue JIRA-123"

1. Claude usa ddf_execute para gerar código:
   → DDF detecta: categoria="escrita", intent="codar"
   → DDF delega para: Claude (melhor para código)
   → Claude gera código

2. Claude usa MCP Git para:
   → Criar commit
   → Criar Pull Request

3. Resultado: PR criado automaticamente
```

### Caso 2: Pipeline de Conteúdo

```
Claude Code: "Criar landing page completa"

1. Claude usa ddf_generate_text para:
   → Gerar copy da landing page
   → Gerar meta description

2. Claude usa ddf_generate_image para:
   → Gerar hero image
   → Gerar ícones

3. Claude usa ddf_execute com categoria="website":
   → DDF delega para Framer
   → Framer cria página

4. Resultado: Landing page completa
```

### Caso 3: Análise e Relatório

```
Claude Code: "Analisar dados do banco e criar relatório"

1. Claude usa MCP PostgreSQL para:
   → Consultar dados

2. Claude usa ddf_generate_text para:
   → Gerar análise
   → Criar relatório

3. Claude usa ddf_generate_image para:
   → Criar gráficos

4. Resultado: Relatório completo
```

## 🔧 Integração com MCP SinapUm

O DDF pode se conectar ao servidor MCP do SinapUm para:

- **Compartilhar storage** - Imagens, vídeos, documentos
- **Acessar banco de dados** - Dados de produtos, usuários
- **Usar ferramentas existentes** - Evolution API, WhatsApp, etc.

```python
# Exemplo: DDF usando MCP SinapUm
from app.mcp_tools.mcp_client import MCPClient, MCPManager

manager = MCPManager()

# Conectar ao MCP SinapUm
sinapum_client = MCPClient(
    "sinapum",
    ["python", "-m", "mcp_sinapum_server"]
)
manager.register_client("sinapum", sinapum_client)

# Usar ferramentas do SinapUm
result = await manager.call_tool(
    "sinapum",
    "whatsapp_send",
    {"to": "+5511999999999", "message": "Olá!"}
)
```

## 📊 Benefícios

### Para Claude Code:
- ✅ **Roteamento Inteligente** - Não precisa escolher qual IA usar
- ✅ **Auditoria** - Todas as operações registradas
- ✅ **Políticas** - Segurança e limites aplicados
- ✅ **Abstração** - Não precisa conhecer APIs de cada IA

### Para o DDF:
- ✅ **Expansão** - Acesso a ferramentas externas via MCP
- ✅ **Integração** - Compatível com Claude Code e outros clientes
- ✅ **Composição** - Pipelines complexos com múltiplas ferramentas
- ✅ **Padrão Aberto** - Compatível com qualquer cliente MCP

## 🚀 Próximos Passos

1. **Implementar servidor MCP completo**
2. **Criar exemplos de uso com Claude Code**
3. **Integrar com MCP SinapUm**
4. **Documentar todas as ferramentas disponíveis**

