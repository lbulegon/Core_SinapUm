# 🏗️ Estrutura dos Servidores - SinapUm e OpenMind

## 📍 Localização dos Servidores

### 1. OpenMind AI Server (FastAPI)
**Localização:** `/opt/openmind-ai/`

**Tecnologia:** FastAPI + Uvicorn  
**Porta:** `8000`  
**Função:** Servidor de IA para análise de imagens

**Estrutura:**
```
/opt/openmind-ai/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/v1/endpoints/
│   │   └── analyze.py       # Endpoint de análise
│   ├── core/
│   │   ├── config.py
│   │   ├── image_analyzer.py
│   │   └── json_transformer.py
│   └── models/
│       └── schemas.py
├── venv/                    # Ambiente virtual
└── requirements.txt
```

**Status:** ✅ Rodando e funcionando

---

### 2. SinapUm (Django)
**Localização:** `/root/SinapUm/`

**Tecnologia:** Django  
**Porta:** `80` (quando rodando)  
**Função:** Servidor principal, orquestrador, MCP futuro

**Estrutura:**
```
/root/SinapUm/
├── app_sinapum/
│   ├── views.py             # Views Django
│   ├── services.py          # Serviços (chama OpenMind)
│   ├── models.py            # Models Django
│   ├── utils.py             # Utilitários
│   └── ...
├── setup/
│   ├── settings.py          # Configurações Django
│   └── urls.py              # Rotas Django
├── manage.py
```

**Status:** ⚠️ Não está rodando atualmente (mas pode ser iniciado)

---

## 🔄 Relação Entre os Servidores

### Fluxo Atual

```
VitrineZap
    ↓
SinapUm (Django) - Porta 80
    ├─> Recebe requisição
    ├─> Salva imagem
    └─> Chama OpenMind
        ↓
OpenMind AI Server (FastAPI) - Porta 8000
    ├─> Processa imagem
    ├─> Retorna JSON
    └─> Serve imagens via /media/
        ↓
SinapUm (Django)
    └─> Retorna resposta completa
        ↓
VitrineZap
```

### Observação Importante

**O PDF menciona FastAPI, mas:**
- ✅ **OpenMind** é FastAPI (em `/opt/openmind-ai/`)
- ✅ **SinapUm** é Django (em `/root/SinapUm/`)

**Para o MCP:**
- O MCP será implementado no **SinapUm (Django)**, não no OpenMind
- O SinapUm já funciona como orquestrador (chama OpenMind)
- Agora vamos **formalizar** isso como MCP

---

## 🎯 Onde Implementar o MCP?

### ✅ Resposta: No SinapUm (Django)

**Por quê?**
1. SinapUm já é o orquestrador central
2. SinapUm já chama OpenMind, CrewAI, Agnos
3. SinapUm é onde ficam as decisões de negócio
4. OpenMind é apenas um serviço especializado (análise de imagens)

**Estrutura MCP no SinapUm:**
```
/root/SinapUm/
├── app_sinapum/
│   ├── mcp/                 # 🆕 Módulo MCP
│   │   ├── core/
│   │   │   ├── router.py    # Roteador MCP
│   │   │   └── registry.py  # Registry de agentes
│   │   ├── agents/
│   │   │   ├── agent_openmind.py    # Chama OpenMind
│   │   │   ├── agent_vitrinezap.py
│   │   │   └── agent_crewai.py
│   │   └── schemas/
│   │       └── task_schema.py
│   ├── views.py             # Views Django (mantidas)
│   └── views_mcp.py         # 🆕 Views MCP
└── setup/
    └── urls.py              # Adicionar rotas MCP
```

---

## 🔍 Confusão do PDF

### O PDF menciona FastAPI porque:

1. **Contexto geral:** Muitos MCPs são implementados em FastAPI
2. **Exemplo genérico:** O PDF usa FastAPI como exemplo
3. **Mas não é obrigatório:** MCP pode ser implementado em Django também!

### Adaptação para Django:

**PDF sugere (FastAPI):**
```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/mcp/route-task")
def route_task(task: TaskRequest):
    ...
```

**SinapUm (Django):**
```python
from django.http import JsonResponse
from mcp.schemas.task_schema import TaskRequest

def mcp_route_task(request):
    task = TaskRequest(**json.loads(request.body))
    ...
    return JsonResponse(response.dict())
```

**Funcionalidade idêntica, framework diferente!**

---

## 📊 Resumo

| Servidor | Localização | Tecnologia | Porta | Função |
|----------|-------------|------------|-------|--------|
| **OpenMind** | `/opt/openmind-ai/` | FastAPI | 8000 | Análise de imagens |
| **SinapUm** | `/root/SinapUm/` | Django | 80 | Orquestrador/MCP |

**MCP será implementado em:** SinapUm (Django)  
**OpenMind continuará como:** Serviço especializado chamado pelo MCP

---

## ✅ Conclusão

**Sim, o FastAPI está em `/opt/openmind-ai/`**, mas:
- É o **OpenMind AI Server** (serviço especializado)
- **NÃO** é onde o MCP será implementado
- O MCP será no **SinapUm (Django)** em `/root/SinapUm/`

O SinapUm já funciona como orquestrador, vamos apenas **formalizar** isso como MCP usando Django (não FastAPI).

---




# Comando Uteis

# Ver status
sudo systemctl status sinapum-django.service

# Reiniciar
sudo systemctl restart sinapum-django.service

# Ver logs
sudo journalctl -u sinapum-django.service -f

# Parar
sudo systemctl stop sinapum-django.service

# Iniciar
sudo systemctl start sinapum-django.service

**Última atualização:** 2025-01-10

