# DDF - Detect & Delegate Framework

Barramento inteligente de tarefas de IA para o SinapUm.

**Localização:** `/root/MCP_SinapUm/services/ddf_service/`

## 📋 Sobre

O DDF é um sistema de roteamento cognitivo que detecta a intenção de uma tarefa e delega automaticamente para o provider de IA mais apropriado, baseado na classificação completa de IAs.

## 🏗️ Arquitetura

```
Entrada → Detect → Delegate → Execute → Audit
```

### Componentes

- **Detect**: Classifica tarefas em categorias (ideias, escrita, imagem, vídeo, etc.)
- **Delegate**: Roteia para o provider de IA apropriado
- **Execute**: Executa a tarefa no provider escolhido
- **Audit**: Registra todas as operações para auditoria

## 📂 Estrutura do Projeto

**Localização:** `/root/MCP_SinapUm/services/ddf_service/`

```
ddf_service/
├── app/
│   ├── api/          # Endpoints FastAPI
│   ├── core/         # Detect, Delegate, Registry
│   ├── providers/    # Implementações de providers
│   ├── models/       # Modelos de dados
│   ├── mcp_tools/    # Integrações MCP (storage, database)
│   └── main.py       # Entrypoint
├── config/
│   ├── providers.yaml    # Registry de IAs
│   ├── routes.yaml       # Regras de roteamento
│   └── policies.yaml     # Políticas de segurança
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🚀 Como Usar

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas API keys
```

### 2. Subir com Docker Compose

```bash
docker compose up -d --build
```

A API estará disponível em: `http://localhost:8005/docs`

### 3. Usar a API

#### Detectar categoria de uma tarefa

```bash
curl -X POST http://localhost:8005/ddf/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Criar uma imagem de um gato"}'
```

#### Executar tarefa completa

```bash
curl -X POST http://localhost:8005/ddf/execute \
  -H "Content-Type: application/json" \
  -d '{"text": "Gerar uma imagem de um gato fofo"}'
```

## 📊 Categorias de IA Disponíveis

O DDF suporta as seguintes categorias (baseadas no PDF):

- **Ideias**: ChatGPT, Gemini, Claude, Perplexity, Copilot
- **Chatbot**: Monica, Grok, Poe, Copilot
- **UI/UX**: Galileo AI, Khroma, Uizard, Visily, VisualEyes
- **Apresentação**: Gamma, Tome, Beautiful.ai, Slidebean, Pitch
- **Website**: Dora, Durable, Wegic, Framer, 10Web
- **Marketing**: AdCopy, Predis AI, Howler AI, Bardeen AI, AdCreative
- **Imagem**: Midjourney, NANO BANANA, Stable Diffusion, Leonardo AI, Adobe Firefly
- **Automação**: Zapier, Make, Phrasee, Outreach, ClickUp
- **Escrita**: Jasper, Rytr, TextBlaze, Sudowrite, Claude, ChatGPT, Copy.ai, Writer
- **Voz → Texto**: Fluently AI, Descript, Rev AI, Clipto, TextCortex
- **Texto → Voz**: ElevenLabs, Murf AI, Speechify, Deepgram, Lovo
- **Vídeo**: Sora, Pika, Runway, Luma, Kling
- **Blogging**: ChatGPT, Jasper, Claude, Copy.ai, Writer
- **Reuniões**: TLDV, Krisp, Otter, Avoma, Fireflies
- **Design**: Canva, Figma (with AI), Looka, Clipdrop, Autodraw
- **AI Detector**: GPTZero, Originality.ai, Turnitin, Copyleaks, ZeroGPT

## 🔌 Endpoints da API

- `POST /ddf/detect` - Detecta categoria de uma tarefa
- `POST /ddf/delegate` - Delega tarefa para provider
- `POST /ddf/execute` - Executa fluxo completo
- `GET /ddf/audit/{request_id}` - Obtém log de auditoria
- `GET /ddf/categories` - Lista todas as categorias
- `GET /ddf/providers/{category}` - Lista providers de uma categoria

## 🔧 Desenvolvimento

### Adicionar novo Provider

1. Criar classe em `app/providers/` herdando de `BaseProvider`
2. Registrar no `ProviderFactory`
3. Adicionar configuração em `config/providers.yaml`

### Modificar Roteamento

Editar `config/routes.yaml` para alterar providers padrão e fallbacks.

## 📚 Documentação

- **[ORIENTACOES.md](ORIENTACOES.md)** - Guia completo com todas as orientações
- **[docs/CASOS_DE_USO.md](docs/CASOS_DE_USO.md)** - 20+ casos de uso práticos
- **[docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)** - Integração com MCP
- **[docs/CLAUDE_CODE_INTEGRATION.md](docs/CLAUDE_CODE_INTEGRATION.md)** - Uso com Claude Code
- **[docs/CLASSIFICACAO_IAS.md](docs/CLASSIFICACAO_IAS.md)** - Classificação completa de IAs

## 🔗 Integração com MCP SinapUm

O DDF está na porta **8005** e integrado ao ecossistema MCP SinapUm.

**Localização:** `/root/MCP_SinapUm/services/ddf_service/`

### Estrutura no SinapUm

```
MCP_SinapUm/
└── services/
    ├── ddf_service/           ← DDF aqui (Porta 8005)
    │   ├── app/
    │   ├── config/
    │   ├── docker-compose.yml
    │   └── README.md
    └── sparkscore_service/   ← SparkScore aqui (Porta 8006)
        ├── app/
        ├── config/
        └── README.md
```

## 📝 Licença

Projeto interno SinapUm

