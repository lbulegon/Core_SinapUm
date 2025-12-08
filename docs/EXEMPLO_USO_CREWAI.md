# Exemplo de Uso - CrewAI + OpenMind

## 🚀 Como Usar a Integração

### 1. Instalação

```bash
cd /root/SinapUm
pip install -r requirements_crewai.txt
```

### 2. Configuração de Variáveis de Ambiente

```bash
# Apenas a chave do OpenMind é necessária!
export OPENMIND_AI_KEY="sua_chave_openmind"
export OPENMIND_AI_URL="http://127.0.0.1:8000"

# O CrewAI usa OpenMind.org como LLM backend (mesma chave)
# Não precisa de OPENAI_API_KEY separada!
```

Ou adicione ao `settings.py`:

```python
# CrewAI usa OpenMind.org como LLM backend
OPENMIND_AI_KEY = 'sua_chave_openmind'  # Usada para tudo!
OPENMIND_ORG_BASE_URL = 'https://api.openmind.org/api/core/openai'
OPENMIND_ORG_MODEL = 'gpt-4o'  # Pode mudar para claude-3-opus, gemini-pro, etc.
```

### 3. Uso no Django (Views)

```python
from app_sinapum.crewai_services import analisar_produto_com_crew

# Análise completa (4 agentes)
resultado = analisar_produto_com_crew(
    image_path="/caminho/para/imagem.jpg",
    modo_completo=True
)

# Análise rápida (2 agentes)
resultado = analisar_produto_com_crew(
    image_path="/caminho/para/imagem.jpg",
    modo_completo=False
)
```

### 4. Uso via API

```bash
curl -X POST http://69.169.102.84:5000/api/crewai/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/caminho/para/imagem.jpg",
    "modo_completo": true
  }'
```

### 5. Uso na Interface Web

Acesse: `http://69.169.102.84:5000/analyze/crewai/`

## 📊 Fluxo de Execução

### Modo Completo (4 Agentes)

1. **Agente Análise** → OpenMind API → Extrai dados da imagem
2. **Agente Enriquecimento** → Busca preços/reviews → Enriquece dados
3. **Agente Validação** → Valida qualidade → Corrige inconsistências
4. **Agente Geração** → Cria anúncio → Texto pronto para WhatsApp

### Modo Rápido (2 Agentes)

1. **Agente Análise** → OpenMind API → Extrai dados
2. **Agente Validação** → Valida dados → Relatório de qualidade

## 🔧 Personalização

### Adicionar Novo Agente

```python
def criar_agente_customizado() -> Agent:
    return Agent(
        role='Seu Papel',
        goal='Seu Objetivo',
        backstory="Sua história",
        tools=[sua_ferramenta],
        verbose=True
    )
```

### Criar Nova Ferramenta

```python
@tool("Nome da Ferramenta")
def sua_ferramenta(parametro: str) -> Dict[str, Any]:
    """
    Descrição da ferramenta.
    
    Args:
        parametro: Descrição do parâmetro
    
    Returns:
        dict: Resultado
    """
    # Sua lógica aqui
    return {"resultado": "valor"}
```

### Modificar Crew

```python
def criar_crew_customizado() -> Crew:
    agente1 = criar_agente_analise()
    agente2 = criar_agente_customizado()
    
    tarefa1 = Task(
        description="Descrição da tarefa",
        agent=agente1,
        expected_output="Output esperado"
    )
    
    tarefa2 = Task(
        description="Outra tarefa",
        agent=agente2,
        expected_output="Outro output"
    )
    
    crew = Crew(
        agents=[agente1, agente2],
        tasks=[tarefa1, tarefa2],
        process=Process.sequential,
        verbose=True
    )
    
    return crew
```

## 📝 Sobre Agnos

**Nota**: Se "Agnos" refere-se a outro framework, por favor forneça mais detalhes para integração adequada. Possíveis interpretações:

1. **Framework de Agentes**: Pode ser integrado de forma similar ao CrewAI
2. **Biblioteca específica**: Pode ser adicionada como dependência adicional
3. **Sistema interno**: Pode ser integrado como serviço externo

## 🐛 Troubleshooting

### Erro: "CrewAI não está instalado"
```bash
pip install crewai crewai[tools]
```

### Erro: "OpenAI API Key não configurada"
```bash
export OPENAI_API_KEY="sua_chave"
```

### Erro: "OpenMind AI não responde"
- Verifique se o servidor está rodando: `curl http://127.0.0.1:8000/health`
- Verifique a URL e chave no `settings.py`

### Agentes não executam
- Verifique os logs: `tail -f /var/log/django/error.log`
- Aumente `verbose=True` nos agentes para mais detalhes

