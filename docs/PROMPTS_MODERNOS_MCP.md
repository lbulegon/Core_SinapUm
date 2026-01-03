# Prompts Modernos com MCP - Alternativas ao PostgreSQL

## 📋 Problemas com Prompts no PostgreSQL

### Desvantagens do Modelo Atual:

1. **Dependência de Banco de Dados**
   - Requer conexão PostgreSQL sempre ativa
   - Se o banco cair, prompts não funcionam
   - Migrações complexas para atualizar prompts

2. **Versionamento Limitado**
   - Versionamento manual (campo `versao`)
   - Difícil rastrear mudanças
   - Sem histórico de alterações

3. **Deploy Complexo**
   - Precisa rodar scripts Django para atualizar prompts
   - Migrações podem quebrar se schema mudar
   - Dependência de acesso ao banco

4. **Segurança**
   - Prompts sensíveis no banco de dados
   - Acesso ao banco = acesso aos prompts
   - Sem controle de acesso granular

5. **Manutenção**
   - Edição via admin Django (não ideal para desenvolvedores)
   - Sem validação de sintaxe
   - Difícil fazer rollback

---

## ✅ Alternativas Modernas com MCP

O MCP já suporta múltiplas fontes de prompts! Veja o código em `app_mcp_tool_registry/utils.py`:

### 1. **Prompts Inline no Config (Recomendado para Produção)**

**Como funciona:**
- Prompt armazenado diretamente no `config` da `ToolVersion`
- Sem dependência de banco de dados
- Versionado junto com o código
- Deploy simples (atualiza tool = atualiza prompt)

**Exemplo:**

```python
# Em register_vitrinezap_tool.py
runtime_config = {
    "url": "http://openmind:8001/api/v1/analyze-product-image",
    "timeout_s": 60,
    "prompt_inline": """Você é um especialista em análise de produtos. 
Analise esta imagem detalhadamente e retorne um JSON estruturado no formato modelo.json COMPLETO.

IMPORTANTE: Você DEVE retornar um JSON com TODAS as seções do modelo.json...

[prompt completo aqui]
"""
}
```

**Vantagens:**
- ✅ Sem dependência de banco
- ✅ Versionado no código (Git)
- ✅ Deploy simples
- ✅ Rollback fácil (Git revert)
- ✅ Validação em PR
- ✅ Code review de prompts

**Desvantagens:**
- ⚠️ Requer redeploy para atualizar
- ⚠️ Prompts grandes podem poluir o código

---

### 2. **Prompts via URL Externa (Recomendado para Desenvolvimento)**

**Como funciona:**
- Prompt armazenado em servidor externo (GitHub, S3, CDN)
- `prompt_ref` aponta para URL
- Atualização instantânea (sem redeploy)

**Exemplo:**

```python
# ToolVersion config
{
    "prompt_ref": "https://raw.githubusercontent.com/seu-org/prompts/main/analise-produto-v2.txt",
    "runtime": "openmind_http",
    "config": {
        "url": "http://openmind:8001/api/v1/analyze-product-image"
    }
}
```

**Vantagens:**
- ✅ Atualização instantânea (sem redeploy)
- ✅ Versionado no Git (URL aponta para branch/tag)
- ✅ Cacheável (CDN)
- ✅ Acesso controlado (autenticação na URL)
- ✅ Histórico completo (Git)

**Desvantagens:**
- ⚠️ Requer servidor externo
- ⚠️ Dependência de internet
- ⚠️ Latência (se não cacheado)

**Implementação com GitHub:**

```python
# Versão específica (recomendado)
"prompt_ref": "https://raw.githubusercontent.com/seu-org/prompts/v2.0.0/analise-produto.txt"

# Branch (desenvolvimento)
"prompt_ref": "https://raw.githubusercontent.com/seu-org/prompts/main/analise-produto.txt"

# Commit específico (máxima segurança)
"prompt_ref": "https://raw.githubusercontent.com/seu-org/prompts/abc123def456/analise-produto.txt"
```

---

### 3. **Prompts via Arquivo Local (Futuro)**

**Como funciona:**
- Prompt em arquivo no sistema de arquivos
- `prompt_ref` aponta para `file:///path/to/prompt.txt`
- Útil para desenvolvimento local

**Exemplo:**

```python
{
    "prompt_ref": "file:///app/prompts/analise-produto-v2.txt",
    "runtime": "openmind_http"
}
```

---

## 🎯 Recomendação: Abordagem Híbrida

### Para Produção:
1. **Prompts Inline no Config** (versão estável)
   - Prompts críticos e estáveis
   - Versionados no código
   - Deploy controlado

2. **Prompts via URL** (experimentação)
   - Prompts em teste/A-B
   - Atualização rápida
   - Rollback instantâneo

### Para Desenvolvimento:
1. **Prompts via URL (GitHub)**
   - Edição rápida
   - Teste imediato
   - Histórico completo

---

## 🔧 Como Migrar

### Passo 1: Criar Repositório de Prompts (Opcional)

```bash
# Criar repositório Git para prompts
mkdir prompts-repo
cd prompts-repo
git init

# Estrutura sugerida:
prompts/
  ├── analise-produto/
  │   ├── v1.0.0.txt
  │   ├── v2.0.0.txt
  │   └── latest.txt -> v2.0.0.txt
  └── README.md
```

### Passo 2: Atualizar ToolVersion

**Opção A: Prompt Inline (Recomendado)**

```python
# register_vitrinezap_tool.py
def register_vitrinezap_tool():
    # ... código existente ...
    
    # Ler prompt de arquivo local
    with open('/app/prompts/analise-produto-v2.txt', 'r', encoding='utf-8') as f:
        prompt_text = f.read()
    
    runtime_config = {
        "url": f"{openmind_url}/api/v1/analyze-product-image",
        "timeout_s": 60,
        "prompt_inline": prompt_text  # ← Prompt inline no config
    }
    
    version, created = ToolVersion.objects.get_or_create(
        tool=tool,
        version="2.0.0",
        defaults={
            'runtime': 'openmind_http',
            'config': runtime_config,
            # prompt_ref pode ser None ou usado para referência
            'prompt_ref': 'analise-produto-v2-inline'
        }
    )
```

**Opção B: Prompt via URL**

```python
version, created = ToolVersion.objects.get_or_create(
    tool=tool,
    version="2.0.0",
    defaults={
        'runtime': 'openmind_http',
        'config': {
            "url": f"{openmind_url}/api/v1/analyze-product-image"
        },
        'prompt_ref': 'https://raw.githubusercontent.com/seu-org/prompts/v2.0.0/analise-produto.txt'
    }
)
```

### Passo 3: Prioridade de Resolução

O MCP já implementa a prioridade correta:

1. **`config.prompt_inline`** (maior prioridade)
2. **`prompt_ref` como URL** (http/https)
3. **`prompt_ref` como referência PostgreSQL** (fallback)

---

## 📊 Comparação

| Característica | PostgreSQL | Inline Config | URL Externa |
|---------------|------------|--------------|-------------|
| **Dependência de BD** | ❌ Sim | ✅ Não | ✅ Não |
| **Versionamento** | ⚠️ Manual | ✅ Git | ✅ Git |
| **Deploy** | ❌ Complexo | ✅ Simples | ✅ Instantâneo |
| **Rollback** | ❌ Difícil | ✅ Git revert | ✅ Mudar URL |
| **Code Review** | ❌ Não | ✅ Sim | ✅ Sim |
| **Atualização Rápida** | ⚠️ Script | ❌ Redeploy | ✅ Instantâneo |
| **Segurança** | ⚠️ Média | ✅ Alta | ✅ Alta |
| **Histórico** | ⚠️ Limitado | ✅ Completo | ✅ Completo |

---

## 🚀 Exemplo Prático: Migração Completa

### 1. Criar arquivo de prompt

```bash
# /root/Core_SinapUm/prompts/analise-produto-v2.txt
Você é um especialista em análise de produtos...
[prompt completo]
```

### 2. Atualizar register_vitrinezap_tool.py

```python
import os
from pathlib import Path

def register_vitrinezap_tool():
    # ... código existente ...
    
    # Carregar prompt de arquivo
    prompt_file = Path(__file__).parent.parent / 'prompts' / 'analise-produto-v2.txt'
    if prompt_file.exists():
        prompt_text = prompt_file.read_text(encoding='utf-8')
        logger.info(f"✅ Prompt carregado de arquivo: {len(prompt_text)} caracteres")
    else:
        # Fallback para prompt inline
        prompt_text = """Prompt padrão..."""
        logger.warning("⚠️ Arquivo de prompt não encontrado, usando fallback")
    
    runtime_config = {
        "url": f"{openmind_url}/api/v1/analyze-product-image",
        "timeout_s": 60,
        "prompt_inline": prompt_text  # ← Prompt inline
    }
    
    version, created = ToolVersion.objects.get_or_create(
        tool=tool,
        version="2.0.0",
        defaults={
            'runtime': 'openmind_http',
            'config': runtime_config,
            'prompt_ref': None  # Não precisa mais
        }
    )
```

### 3. Benefícios Imediatos

- ✅ Prompt versionado no Git
- ✅ Code review antes de deploy
- ✅ Rollback instantâneo
- ✅ Sem dependência de banco
- ✅ Deploy mais rápido

---

## 🎓 Conclusão

**Para produção, recomendo:**

1. **Prompts críticos/estáveis**: Inline no config (versionado no código)
2. **Prompts experimentais**: URL externa (GitHub) para atualização rápida
3. **PostgreSQL**: Apenas como fallback ou para prompts dinâmicos (raro)

**Vantagens principais:**
- ✅ Menos pontos de falha
- ✅ Versionamento adequado
- ✅ Deploy mais simples
- ✅ Melhor segurança
- ✅ Histórico completo

