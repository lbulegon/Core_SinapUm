# Classificação de IAs - DDF

Este documento apresenta a classificação completa de IAs implementada no DDF, baseada no PDF fornecido.

## 📊 Categorias e Providers

### 1. IDEIAS
Providers para geração de ideias, brainstorming e planejamento:
- **ChatGPT** - OpenAI
- **Gemini** - Google
- **Claude** - Anthropic
- **Perplexity** - Perplexity AI
- **Copilot** - GitHub

### 2. CHATBOT
Assistentes conversacionais e atendimento:
- **Monica** - Monica AI
- **Grok** - xAI
- **Poe** - Quora
- **Copilot** - GitHub

### 3. UI/UX
Ferramentas para design de interface e experiência do usuário:
- **Galileo AI** - Galileo AI
- **Khroma** - Khroma
- **Uizard** - Uizard
- **Visily** - Visily
- **VisualEyes** - VisualEyes

### 4. APRESENTAÇÃO
Criação de apresentações e slides:
- **Gamma** - Gamma
- **Tome** - Tome
- **Beautiful.ai** - Beautiful.ai
- **Slidebean** - Slidebean
- **Pitch** - Pitch

### 5. WEBSITE
Construtores de sites e páginas web:
- **Dora** - Dora
- **Durable** - Durable
- **Wegic** - Wegic
- **Framer** - Framer
- **10Web** - 10Web

### 6. MARKETING
Ferramentas de marketing e publicidade:
- **AdCopy** - AdCopy
- **Predis AI** - Predis AI
- **Howler AI** - Howler AI
- **Bardeen AI** - Bardeen AI
- **AdCreative** - AdCreative

### 7. IMAGEM
Geração e edição de imagens:
- **Midjourney** - Midjourney
- **NANO BANANA** - NANO BANANA
- **Stable Diffusion** - Stability AI
- **Leonardo AI** - Leonardo AI
- **Adobe Firefly** - Adobe

### 8. AUTOMAÇÃO
Automação de workflows e tarefas:
- **Zapier** - Zapier
- **Make** - Make (Integromat)
- **Phrasee** - Phrasee
- **Outreach** - Outreach
- **ClickUp** - ClickUp

### 9. ESCRITA
Geração e edição de texto:
- **Jasper** - Jasper
- **Rytr** - Rytr
- **TextBlaze** - TextBlaze
- **Sudowrite** - Sudowrite
- **Claude** - Anthropic
- **ChatGPT** - OpenAI
- **Copy.ai** - Copy.ai
- **Writer** - Writer

### 10. VOZ → TEXTO
Transcrição de áudio para texto:
- **Fluently AI** - Fluently AI
- **Descript** - Descript
- **Rev AI** - Rev AI
- **Clipto** - Clipto
- **TextCortex** - TextCortex

### 11. TEXTO → VOZ
Síntese de voz (Text-to-Speech):
- **ElevenLabs** - ElevenLabs
- **Murf AI** - Murf AI
- **Speechify** - Speechify
- **Deepgram** - Deepgram
- **Lovo** - Lovo

### 12. VÍDEO
Geração e edição de vídeos:
- **Sora** - OpenAI
- **Pika** - Pika
- **Runway** - Runway
- **Luma** - Luma
- **Kling** - Kling

### 13. BLOGGING
Criação de conteúdo para blogs:
- **ChatGPT** - OpenAI
- **Jasper** - Jasper
- **Claude** - Anthropic
- **Copy.ai** - Copy.ai
- **Writer** - Writer

### 14. REUNIÕES
Ferramentas para reuniões e transcrições:
- **TLDV** - TLDV
- **Krisp** - Krisp
- **Otter** - Otter
- **Avoma** - Avoma
- **Fireflies** - Fireflies

### 15. DESIGN
Ferramentas de design gráfico:
- **Canva** - Canva
- **Figma (with AI)** - Figma
- **Looka** - Looka
- **Clipdrop** - Clipdrop
- **Autodraw** - Google

### 16. AI DETECTOR
Detecção de conteúdo gerado por IA:
- **GPTZero** - GPTZero
- **Originality.ai** - Originality.ai
- **Turnitin** - Turnitin
- **Copyleaks** - Copyleaks
- **ZeroGPT** - ZeroGPT

## 🔄 Fluxo de Roteamento

1. **Detect**: Analisa o texto da tarefa e identifica a categoria
2. **Delegate**: Escolhe o provider mais apropriado baseado em:
   - Categoria detectada
   - Provider padrão configurado
   - Contexto do projeto (Évora, MotoPro, etc.)
   - Disponibilidade do provider
3. **Execute**: Executa a tarefa no provider escolhido
4. **Audit**: Registra toda a operação para auditoria

## 📝 Configuração

A classificação está configurada em:
- `config/providers.yaml` - Lista de providers por categoria
- `config/routes.yaml` - Regras de roteamento padrão
- `config/policies.yaml` - Políticas de segurança e limites

## 🚀 Expansão

Para adicionar novos providers:
1. Adicionar na lista apropriada em `config/providers.yaml`
2. Criar implementação em `app/providers/`
3. Registrar no `ProviderFactory`

