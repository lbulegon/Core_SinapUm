# 📋 Plano de Desenvolvimento - ÉVORA/VitrineZap

## 🏗️ Arquitetura do Projeto

### Backend (MCP_SinapUm)
- **Localização:** `/root/MCP_SinapUm/`
- **Tecnologias:** Django, FastAPI, OpenMind AI
- **Responsabilidades:**
  - Agentes de IA (ágnostos)
  - Análise de imagens de produtos
  - APIs de backend
  - Serviços (OpenMind, Evolution API, etc.)

### Frontend (Évora)
- **Localização:** `/root/evora/`
- **Tecnologias:** Django (templates), WhatsApp Integration
- **Responsabilidades:**
  - Interface do usuário
  - Fluxo WhatsApp
  - Dashboards (Cliente, Shopper, Keeper)
  - Integração com backend (MCP_SinapUm)

---

## 🎯 Prioridades de Desenvolvimento

### 🔴 ALTA PRIORIDADE

#### 1. Melhorar Velocidade de Análise (Backend)
- [ ] Implementar cache de análises similares
- [ ] Otimizar processamento de imagens (reduzir qualidade antes de enviar)
- [ ] Processar múltiplas imagens em paralelo
- [ ] Adicionar progresso visual durante análise (Frontend)

#### 2. Fluxo de Cadastro de Estabelecimento (Frontend + Backend)
- [ ] Capturar localização GPS do usuário
- [ ] Integrar com Google Places API / Foursquare
- [ ] Buscar estabelecimentos próximos
- [ ] Permitir seleção de estabelecimento
- [ ] Auto-preenchimento de dados

#### 3. Completar Agente Ágnosto (Backend)
- [ ] Implementar busca de preço do produto (TODO no código)
- [ ] Melhorar respostas do agente
- [ ] Integrar com contexto de ofertas

### 🟡 MÉDIA PRIORIDADE

#### 4. Comentários de Voz (Frontend + Backend)
- [ ] Adicionar gravação de áudio no formulário
- [ ] Integrar com API de transcrição (Whisper/Google Speech)
- [ ] Salvar comentários de voz vinculados ao produto
- [ ] Permitir reprodução no WhatsApp

#### 5. Edição Rápida de Itens (Frontend)
- [ ] Edição inline de outros campos (nome, marca, etc.)
- [ ] Salvar alterações sem recarregar página (AJAX)
- [ ] Melhorar UX do formulário

#### 6. Integração WhatsApp - Respostas de Voz
- [ ] Permitir que shoppers respondam com áudio
- [ ] Transcrever áudio para texto
- [ ] Enviar respostas via WhatsApp

### 🟢 BAIXA PRIORIDADE

#### 7. Melhorias de UX
- [ ] Progresso visual durante análise
- [ ] Notificações em tempo real
- [ ] Melhorias de performance

---

## 📝 Tarefas por Componente

### Backend (MCP_SinapUm)

#### Agentes
- [ ] Completar `_handle_ask_price()` - buscar preço real do produto
- [ ] Melhorar contexto do agente com dados de ofertas
- [ ] Adicionar mais ações ao agente (sugerir produtos, etc.)

#### Análise de Imagens
- [ ] Implementar cache de análises
- [ ] Otimização de imagens antes de enviar
- [ ] Processamento paralelo

#### APIs
- [ ] Endpoint para busca de estabelecimentos (Google Places)
- [ ] Endpoint para transcrição de áudio
- [ ] Melhorar documentação das APIs

### Frontend (Évora)

#### Cadastro de Produtos
- [ ] Adicionar captura de GPS
- [ ] Integração com Google Places
- [ ] Seleção de estabelecimento
- [ ] Gravação de áudio

#### Edição de Produtos
- [ ] Edição inline de campos
- [ ] Salvar via AJAX
- [ ] Feedback visual

#### WhatsApp
- [ ] Respostas de voz
- [ ] Transcrição de áudio
- [ ] Melhorias de UX

---

## 🚀 Próximos Passos Sugeridos

1. **Implementar cache de análises** (Backend - MCP_SinapUm)
2. **Completar busca de preço no agente** (Backend - MCP_SinapUm)
3. **Fluxo de cadastro de estabelecimento** (Frontend - Évora)
4. **Otimização de imagens** (Backend - MCP_SinapUm)

---

## 📊 Status Atual

### ✅ Concluído Recentemente
- Fluxo completo WhatsApp (grupo → click-to-chat → privado → pedido)
- Integração com pagamento
- Escolha de método de entrega
- Webhook de confirmação de pagamento
- Integração com KMN
- Notificação de prova social

### 🔄 Em Desenvolvimento
- Melhorias de performance
- Cache de análises
- Fluxo de estabelecimento

### ⏳ Pendente
- Comentários de voz
- Respostas de voz no WhatsApp
- Edição inline completa

---

**Última atualização:** 21/12/2025

