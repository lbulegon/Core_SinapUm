# 📋 Orientações - Lead Registry

Guia prático passo a passo para configurar e usar o sistema central de captação de leads.

---

## 🚀 Configuração Inicial

### 1. Criar Credencial do Projeto no Django Admin

**Acesse:** `http://69.169.102.84:5000/admin/app_leads/projectcredential/add/`

**Preencha:**
- **Project Key:** `vitrinezap` (ou nome do seu projeto)
- **Project Secret:** Gere um secret seguro:
  ```bash
  openssl rand -hex 32
  ```
  Ou use um gerador online de strings aleatórias (mínimo 32 caracteres)
- **Is Active:** ✅ Marque como ativo

**Salve** e anote o `project_secret` - você precisará dele no projeto consumidor.

---

## 🔧 Integração no Projeto (Exemplo: VitrineZap)

### Opção A: Backend Django (Recomendado)

#### Passo 1: Adicionar Secret no Settings

No `settings.py` do VitrineZap:

```python
# Credenciais do Lead Registry
VITRINEZAP_LEAD_SECRET = os.environ.get('VITRINEZAP_LEAD_SECRET', 'seu_secret_aqui')
CORE_LEAD_URL = os.environ.get('CORE_LEAD_URL', 'http://69.169.102.84:5000')
```

#### Passo 2: Criar View de Captação

Crie ou edite `vitrinezap/views.py`:

```python
import hmac
import hashlib
import time
import requests
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages

def capture_lead_vitrinezap(request):
    """
    View que recebe o form do frontend e publica o lead no Core.
    """
    if request.method != 'POST':
        return redirect('/')
    
    # Validar campos obrigatórios
    nome = request.POST.get('nome', '').strip()
    email = request.POST.get('email', '').strip()
    whatsapp = request.POST.get('whatsapp', '').strip()
    cidade = request.POST.get('cidade', '').strip()
    
    if not (nome and email and whatsapp):
        messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
        return redirect('/#lista-antecipada')
    
    # Configurações
    PROJECT_KEY = 'vitrinezap'
    PROJECT_SECRET = settings.VITRINEZAP_LEAD_SECRET
    CORE_URL = settings.CORE_LEAD_URL
    
    # Gerar assinatura HMAC
    timestamp = str(int(time.time()))
    message = f"{PROJECT_KEY}{timestamp}{email}{whatsapp}"
    signature = hmac.new(
        PROJECT_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Headers de autenticação
    headers = {
        'X-Project-Key': PROJECT_KEY,
        'X-Signature': signature,
        'X-Timestamp': timestamp,
    }
    
    # Dados do lead
    data = {
        'nome': nome,
        'email': email,
        'whatsapp': whatsapp,
        'cidade': cidade,
        'source_system': 'vitrinezap',
        'source_entrypoint': 'home',
        'source_context': 'lista_antecipada',
        'return_url': '/#lista-antecipada',
    }
    
    # POST para o Core
    try:
        response = requests.post(
            f'{CORE_URL}/api/leads/capture',
            headers=headers,
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                messages.success(request, 'Cadastro realizado com sucesso!')
            else:
                messages.error(request, 'Erro ao processar cadastro.')
        else:
            messages.error(request, 'Erro ao conectar com o servidor.')
    except Exception as e:
        # Log do erro (opcional)
        print(f"Erro ao capturar lead: {e}")
        messages.error(request, 'Erro ao processar cadastro. Tente novamente.')
    
    return redirect('/#lista-antecipada')
```

#### Passo 3: Configurar URL

No `vitrinezap/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... outras URLs ...
    path('capture-lead/', views.capture_lead_vitrinezap, name='capture_lead'),
]
```

#### Passo 4: Atualizar Form HTML

No template da home do VitrineZap, atualize o form:

```html
<form method="POST" action="{% url 'capture_lead' %}" class="needs-validation" novalidate>
  {% csrf_token %}
  
  <!-- Honeypot (invisível) -->
  <input type="text" name="website" style="display:none" tabindex="-1" autocomplete="off">
  
  <div class="mb-3">
    <label class="form-label">Nome *</label>
    <input name="nome" class="form-control" required>
  </div>
  
  <div class="row g-2">
    <div class="col-12 col-sm-6">
      <label class="form-label">WhatsApp *</label>
      <input name="whatsapp" class="form-control" required>
    </div>
    <div class="col-12 col-sm-6">
      <label class="form-label">E-mail *</label>
      <input type="email" name="email" class="form-control" required>
    </div>
  </div>
  
  <div class="mt-3">
    <label class="form-label">Cidade/Bairro (opcional)</label>
    <input name="cidade" class="form-control">
  </div>
  
  <button type="submit" class="btn btn-primary w-100 mt-3 fw-bold">
    Quero receber vitrines no WhatsApp
  </button>
</form>
```

---

## 🧪 Testar a Integração

### 1. Teste Manual

1. Preencha o form na home do VitrineZap
2. Envie o formulário
3. Verifique no Django Admin do Core (`/admin/app_leads/lead/`) se o lead foi criado
4. Verifique os eventos em `/admin/app_leads/leadevent/`

### 2. Teste via Python

Use o arquivo `example_integration.py`:

```python
from app_leads.example_integration import capture_lead_to_core

result = capture_lead_to_core(
    core_url="http://69.169.102.84:5000",
    project_key="vitrinezap",
    project_secret="seu_secret_aqui",
    nome="João Silva",
    email="joao@example.com",
    whatsapp="5511999999999",
    cidade="São Paulo",
)

if result.get("ok"):
    print(f"✅ Lead capturado! ID: {result.get('lead_id')}")
else:
    print(f"❌ Erro: {result.get('error')}")
```

---

## 📊 Monitoramento e Gestão

### Ver Leads no Admin

**URL:** `http://69.169.102.84:5000/admin/app_leads/lead/`

**Filtros úteis:**
- Por `source_system` (ex: "vitrinezap")
- Por `lead_status` (new, qualified, activated, dormant)
- Por data de criação

### Ver Eventos de Auditoria

**URL:** `http://69.169.102.84:5000/admin/app_leads/leadevent/`

**Eventos importantes:**
- `created`: Lead criado com sucesso
- `updated`: Lead atualizado (email já existia)
- `rejected`: Requisição rejeitada (HMAC inválido)
- `rate_limited`: Rate limit excedido

### Ver Credenciais de Projetos

**URL:** `http://69.169.102.84:5000/admin/app_leads/projectcredential/`

Aqui você pode:
- Criar novas credenciais para outros projetos
- Desativar projetos (marcar `is_active=False`)
- Ver quando foram criadas/atualizadas

---

## 🔐 Segurança - Checklist

- [ ] `project_secret` armazenado em variável de ambiente (não hardcoded)
- [ ] Secret com no mínimo 32 caracteres aleatórios
- [ ] Cada projeto tem seu próprio `project_key` e `project_secret`
- [ ] Honeypot (`website`) presente no form HTML
- [ ] Rate limit configurado (padrão: 20 req/min por IP)
- [ ] Timestamp validado (janela de ±5 minutos)

---

## 🐛 Troubleshooting

### Erro: "Projeto não autorizado ou inativo"

**Causa:** `ProjectCredential` não existe ou está inativo.

**Solução:**
1. Verificar se existe `ProjectCredential` com `project_key` correto
2. Verificar se `is_active=True`
3. Verificar se o `project_secret` está correto

### Erro: "Assinatura HMAC inválida"

**Causa:** Assinatura não confere com o secret.

**Solução:**
1. Verificar se o `project_secret` está correto
2. Verificar se a ordem dos campos na mensagem está correta: `project_key + timestamp + email + whatsapp`
3. Verificar se o timestamp está dentro da janela válida (±5 minutos)

### Erro: "Rate limit exceeded"

**Causa:** Muitas requisições do mesmo IP em pouco tempo.

**Solução:**
- Aguardar 1 minuto antes de tentar novamente
- Verificar se não há loop infinito no frontend
- Considerar aumentar o limite no código (não recomendado)

### Erro: "Timestamp fora da janela válida"

**Causa:** Relógio do servidor desatualizado ou timestamp muito antigo.

**Solução:**
1. Sincronizar relógio do servidor (NTP)
2. Gerar timestamp novo antes de cada requisição

---

## 📝 Adicionar Novo Projeto

Para adicionar um novo projeto (ex: MotoPro, Eventix):

1. **Criar credencial no Admin:**
   - `project_key`: "motopro" (ou nome do projeto)
   - `project_secret`: Gerar novo secret
   - `is_active`: True

2. **Repetir os passos de integração:**
   - Adicionar secret no settings do projeto
   - Criar view de captação
   - Configurar URL
   - Atualizar form HTML

3. **Testar:**
   - Enviar lead de teste
   - Verificar no Admin do Core

---

## 🔄 Fluxo Completo

```
1. Usuário preenche form no VitrineZap
   ↓
2. Form POST para view do VitrineZap
   ↓
3. View gera assinatura HMAC
   ↓
4. View faz POST para Core (/api/leads/capture)
   ↓
5. Core valida HMAC, honeypot, rate limit
   ↓
6. Core salva Lead e LeadEvent
   ↓
7. Core retorna JSON {ok: true, lead_id: 123}
   ↓
8. View do VitrineZap redireciona usuário
   ↓
9. Usuário vê mensagem de sucesso
```

---

## 📞 Suporte

Em caso de dúvidas ou problemas:

1. Verificar logs do Core: `docker compose logs web`
2. Verificar eventos rejeitados no Admin
3. Testar assinatura HMAC manualmente
4. Verificar se o Core está acessível: `curl http://69.169.102.84:5000/health`

---

## ✅ Checklist de Implementação

- [ ] Credencial criada no Admin
- [ ] Secret configurado no settings do projeto
- [ ] View de captação criada
- [ ] URL configurada
- [ ] Form HTML atualizado
- [ ] Teste manual realizado
- [ ] Lead aparecendo no Admin do Core
- [ ] Eventos de auditoria sendo registrados

---

**Última atualização:** 27/12/2025

