# 📚 Orientações - DDF (Detect & Delegate Framework)

Este arquivo contém todas as orientações importantes sobre o DDF, incluindo integração MCP, uso com Claude Code e configuração.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Integração MCP](#integração-mcp)
3. [Uso com Claude Code](#uso-com-claude-code)
4. [Configuração](#configuração)
5. [Arquitetura](#arquitetura)
6. [Classificação de IAs](#classificação-de-ias)

---

## 🎯 Visão Geral

O DDF é um **barramento inteligente de tarefas de IA** que:

- **Detecta** automaticamente a categoria e intenção de uma tarefa
- **Delega** para o provider de IA mais apropriado
- **Executa** a tarefa no provider escolhido
- **Audita** todas as operações para rastreabilidade

### Por que usar o DDF?

✅ **Roteamento Inteligente** - Não precisa escolher qual IA usar  
✅ **Auditoria Centralizada** - Todas as operações registradas  
✅ **Políticas de Segurança** - Bloqueios e limites aplicados  
✅ **Abstração de Providers** - Não precisa conhecer APIs de cada IA  
✅ **Integração MCP** - Compatível com Claude Code e outros clientes MCP  

---

## 🔌 Integração MCP

O DDF pode se beneficiar do **Model Context Protocol (MCP)** de três formas:

### 1. DDF como Servidor MCP

O DDF expõe suas capacidades como **ferramentas MCP**, permitindo que:
- **Claude Code** use o DDF para rotear tarefas automaticamente
- Outros clientes MCP usem o DDF como barramento de IAs
- O DDF se torne uma ferramenta universal de orquestração

**Ferramentas MCP disponíveis:**
- `ddf_detect` - Classifica tarefa em categoria e intenção
- `ddf_execute` - Executa tarefa completa (detect → delegate → execute)
- `ddf_generate_text` - Gera texto usando IA apropriada
- `ddf_generate_image` - Gera imagem usando IA apropriada
- `ddf_list_categories` - Lista todas as categorias disponíveis
- `ddf_list_providers` - Lista providers de uma categoria

### 2. DDF como Cliente MCP

O DDF pode se conectar a **servidores MCP externos** para:
- **Git** - Commits, Pull Requests, Issues
- **Jira** - Criar/atualizar issues
- **Figma** - Obter designs
- **PostgreSQL** - Consultas e atualizações
- **Outras ferramentas** do ecossistema MCP

### 3. Integração com MCP SinapUm

O DDF pode usar ferramentas do **MCP SinapUm**:
- Storage compartilhado (imagens, vídeos, documentos)
- Banco de dados (produtos, usuários)
- Evolution API / WhatsApp
- Outros serviços do SinapUm

**📖 Documentação completa:** [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)

---

## 💻 Uso com Claude Code

### Configuração Rápida

1. **Instalar dependências:**
```bash
cd /root/ddf
pip install -r requirements.txt
```

2. **Configurar Claude Code:**

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

### Exemplos de Uso

#### Exemplo 1: Gerar Texto
```
Claude Code: "Use ddf_generate_text com prompt: 'Explique o que é MCP'"
```

#### Exemplo 2: Gerar Imagem
```
Claude Code: "Use ddf_generate_image com prompt: 'Um gato astronauta'"
```

#### Exemplo 3: Pipeline Completo
```
Claude Code: "Implementar feature do issue JIRA-123"

1. Claude usa ddf_execute("Implementar feature X")
   → DDF detecta: categoria="escrita", intent="codar"
   → DDF delega para: Claude (melhor para código)
   → Claude gera código

2. Claude usa MCP Git (via DDF):
   → Criar commit
   → Criar Pull Request

3. Resultado: PR criado automaticamente
```

**📖 Guia completo:** [docs/CLAUDE_CODE_INTEGRATION.md](docs/CLAUDE_CODE_INTEGRATION.md)

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Copiar `.env.example` para `.env` e configurar:

```bash
cp .env.example .env
```

Variáveis importantes:
- `DATABASE_URL` - URL do PostgreSQL
- `REDIS_URL` - URL do Redis
- `STORAGE_PATH` - Caminho para armazenamento de artefatos
- `OPENAI_API_KEY` - Chave da API OpenAI (para ChatGPT)
- `ANTHROPIC_API_KEY` - Chave da API Anthropic (para Claude)
- Outras chaves de API conforme necessário

### 2. Subir com Docker

```bash
cd /root/ddf
docker compose up -d --build
```

A API estará disponível em: `http://localhost:8005/docs`

### 3. Testar API

```bash
# Detectar categoria
curl -X POST http://localhost:8005/ddf/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Criar uma imagem de um gato"}'

# Executar tarefa completa
curl -X POST http://localhost:8005/ddf/execute \
  -H "Content-Type: application/json" \
  -d '{"text": "Gerar uma imagem de um gato fofo"}'
```

---

## 🏗️ Arquitetura

```
Entrada → Detect → Delegate → Execute → Audit
```

### Componentes Principais

- **Detect** (`app/core/detect.py`) - Classifica tarefas em categorias
- **Delegate** (`app/core/delegate.py`) - Roteia para provider apropriado
- **Registry** (`app/core/registry.py`) - Mantém registro de IAs
- **Policies** (`app/core/policies.py`) - Gerencia regras e limites
- **Providers** (`app/providers/`) - Implementações de IAs
- **MCP Tools** (`app/mcp_tools/`) - Integrações MCP

### Estrutura de Arquivos

```
ddf/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── core/                   # Núcleo do DDF
│   │   ├── detect.py           # Classificação
│   │   ├── delegate.py         # Roteamento
│   │   ├── policies.py         # Regras/limites
│   │   └── registry.py         # Registry de IAs
│   ├── providers/              # Adaptadores de IA
│   │   ├── chatgpt.py
│   │   ├── claude.py
│   │   ├── image_sd.py
│   │   └── elevenlabs.py
│   ├── mcp_tools/              # Ferramentas MCP
│   │   ├── storage.py
│   │   ├── database.py
│   │   ├── queue.py
│   │   ├── mcp_server.py       # Servidor MCP
│   │   └── mcp_client.py       # Cliente MCP
│   ├── models/
│   │   └── audit.py            # Auditoria
│   └── api/
│       ├── routes.py
│       └── schemas.py
├── config/
│   ├── providers.yaml          # Registry de IAs
│   ├── routes.yaml             # Regras de roteamento
│   └── policies.yaml           # Políticas de segurança
└── docs/                       # Documentação
    ├── MCP_INTEGRATION.md
    ├── CLAUDE_CODE_INTEGRATION.md
    └── CLASSIFICACAO_IAS.md
```

---

## 📊 Classificação de IAs

O DDF suporta **16 categorias** com **80+ IAs**:

1. **Ideias** - ChatGPT, Gemini, Claude, Perplexity, Copilot
2. **Chatbot** - Monica, Grok, Poe, Copilot
3. **UI/UX** - Galileo AI, Khroma, Uizard, Visily, VisualEyes
4. **Apresentação** - Gamma, Tome, Beautiful.ai, Slidebean, Pitch
5. **Website** - Dora, Durable, Wegic, Framer, 10Web
6. **Marketing** - AdCopy, Predis AI, Howler AI, Bardeen AI, AdCreative
7. **Imagem** - Midjourney, NANO BANANA, Stable Diffusion, Leonardo AI, Adobe Firefly
8. **Automação** - Zapier, Make, Phrasee, Outreach, ClickUp
9. **Escrita** - Jasper, Rytr, TextBlaze, Sudowrite, Claude, ChatGPT, Copy.ai, Writer
10. **Voz → Texto** - Fluently AI, Descript, Rev AI, Clipto, TextCortex
11. **Texto → Voz** - ElevenLabs, Murf AI, Speechify, Deepgram, Lovo
12. **Vídeo** - Sora, Pika, Runway, Luma, Kling
13. **Blogging** - ChatGPT, Jasper, Claude, Copy.ai, Writer
14. **Reuniões** - TLDV, Krisp, Otter, Avoma, Fireflies
15. **Design** - Canva, Figma (with AI), Looka, Clipdrop, Autodraw
16. **AI Detector** - GPTZero, Originality.ai, Turnitin, Copyleaks, ZeroGPT

**📖 Lista completa:** [docs/CLASSIFICACAO_IAS.md](docs/CLASSIFICACAO_IAS.md)

---

## 📋 Casos de Uso

O DDF suporta **20+ casos de uso principais** organizados por:

- **Categoria** - Ideias, Escrita, Imagem, Vídeo, Voz, etc.
- **Integração** - WhatsApp, Claude Code, MCP SinapUm
- **Fluxo** - Pipelines encadeados complexos
- **Avançados** - Orquestração, auditoria, otimização

**📖 Lista completa:** [docs/CASOS_DE_USO.md](docs/CASOS_DE_USO.md)

---

## 🔗 Links Úteis

- **Casos de Uso:** [docs/CASOS_DE_USO.md](docs/CASOS_DE_USO.md)
- **Documentação MCP:** [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)
- **Guia Claude Code:** [docs/CLAUDE_CODE_INTEGRATION.md](docs/CLAUDE_CODE_INTEGRATION.md)
- **Classificação de IAs:** [docs/CLASSIFICACAO_IAS.md](docs/CLASSIFICACAO_IAS.md)
- **README Principal:** [README.md](README.md)

---

## ❓ Dúvidas Frequentes

### Como adicionar um novo provider?

1. Criar classe em `app/providers/` herdando de `BaseProvider`
2. Registrar no `ProviderFactory`
3. Adicionar em `config/providers.yaml`

### Como modificar roteamento?

Editar `config/routes.yaml` para alterar providers padrão e fallbacks.

### Como usar com Claude Code?

Ver seção [Uso com Claude Code](#uso-com-claude-code) acima.

### Como integrar com MCP SinapUm?

Ver seção [Integração MCP](#integração-mcp) acima.

---

**Última atualização:** 14/12/2024  
**Versão:** 1.0.0

