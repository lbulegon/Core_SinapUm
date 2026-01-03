# Lead Registry - Sistema Central de Captação de Leads

Sistema centralizado de captação de leads reutilizável por todos os projetos (VitrineZap, MotoPro, Eventix, MrFoo, etc.).

> 📋 **Para orientações práticas passo a passo, consulte:** [`ORIENTACOES.md`](./ORIENTACOES.md)

## 🎯 Arquitetura

O Lead Registry é um sistema **CORE** que:
- ✅ Centraliza todos os leads de todos os projetos
- ✅ Fornece auditoria completa (IP, user_agent, referrer)
- ✅ Valida requisições via assinatura HMAC
- ✅ Protege contra bots (honeypot + rate limit)
- ✅ Permite rastreamento UTM
- ✅ Base para Identity Graph e SparkScore futuros

## 🔐 Segurança

### Autenticação HMAC

Cada projeto precisa ter credenciais registradas no Core:

1. **ProjectCredential** no Django Admin:
   - `project_key`: Identificador único (ex: "vitrinezap")
   - `project_secret`: Secret para geração de assinatura HMAC
   - `is_active`: Se o projeto está autorizado

2. **Headers obrigatórios** em cada requisição:
   - `X-Project-Key`: project_key do projeto
   - `X-Signature`: Assinatura HMAC-SHA256
   - `X-Timestamp`: Timestamp Unix (string)

### Geração de Assinatura HMAC

```python
import hmac
import hashlib
import time

def generate_hmac_signature(secret, project_key, timestamp, email, whatsapp):
    message = f"{project_key}{timestamp}{email}{whatsapp}"
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

# Exemplo de uso
secret = "seu_project_secret_aqui"
project_key = "vitrinezap"
timestamp = str(int(time.time()))
email = "usuario@example.com"
whatsapp = "5511999999999"

signature = generate_hmac_signature(secret, project_key, timestamp, email, whatsapp)
```

## 📡 Endpoint de Captação

**URL:** `POST /api/leads/capture`

### Headers Obrigatórios
```
X-Project-Key: vitrinezap
X-Signature: <hmac_signature>
X-Timestamp: <unix_timestamp>
```

### Campos POST

**Obrigatórios:**
- `nome`: Nome do lead
- `email`: Email do lead
- `whatsapp`: WhatsApp do lead

**Opcionais:**
- `cidade`: Cidade/Bairro
- `source_system`: Sistema origem (ex: "vitrinezap")
- `source_entrypoint`: Ponto de entrada (ex: "home", "modal")
- `source_context`: Contexto específico (ex: "lista_antecipada")
- `utm_source`, `utm_campaign`, `utm_medium`, `utm_content`: Parâmetros UTM
- `return_url`: URL de retorno após sucesso (para forms HTML)
- `website`: Campo honeypot (deve estar vazio)

### Respostas

**Sucesso (200):**
```json
{
  "ok": true,
  "lead_id": 123,
  "created": true
}
```

**Erro (400/403/429):**
```json
{
  "ok": false,
  "error": "validation_failed|authentication_failed|rate_limited",
  "message": "Descrição do erro"
}
```

## 🔧 Integração no VitrineZap (Exemplo)

### Opção 1: Backend Django (Recomendado)

No backend do VitrineZap, criar uma view que:
1. Recebe o form do frontend
2. Gera a assinatura HMAC
3. Faz POST server-to-server para o Core
4. Redireciona o usuário

**Exemplo de view no VitrineZap:**

```python
# vitrinezap/views.py
import hmac
import hashlib
import time
import requests
from django.shortcuts import redirect
from django.conf import settings

def capture_lead_vitrinezap(request):
    if request.method != 'POST':
        return redirect('/')
    
    # Dados do form
    nome = request.POST.get('nome')
    email = request.POST.get('email')
    whatsapp = request.POST.get('whatsapp')
    cidade = request.POST.get('cidade', '')
    
    # Credenciais do VitrineZap (armazenar em settings ou env)
    PROJECT_KEY = 'vitrinezap'
    PROJECT_SECRET = settings.VITRINEZAP_LEAD_SECRET  # Configurar no settings.py
    
    # Gerar assinatura HMAC
    timestamp = str(int(time.time()))
    message = f"{PROJECT_KEY}{timestamp}{email}{whatsapp}"
    signature = hmac.new(
        PROJECT_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # POST para o Core
    core_url = 'http://69.169.102.84:5000/api/leads/capture'
    headers = {
        'X-Project-Key': PROJECT_KEY,
        'X-Signature': signature,
        'X-Timestamp': timestamp,
    }
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
    
    try:
        response = requests.post(core_url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            # Sucesso
            return redirect('/#lista-antecipada?success=1')
        else:
            # Erro
            return redirect('/#lista-antecipada?error=1')
    except Exception as e:
        # Erro de conexão
        return redirect('/#lista-antecipada?error=1')
```

### Opção 2: Frontend com Fetch (Menos Seguro)

⚠️ **Não recomendado em produção** - expõe o secret no frontend.

Se necessário, usar apenas para testes:

```javascript
// Gerar assinatura no frontend (NÃO RECOMENDADO)
async function submitLead(formData) {
    const timestamp = Math.floor(Date.now() / 1000).toString();
    const message = `vitrinezap${timestamp}${formData.email}${formData.whatsapp}`;
    const signature = await generateHMAC(message, SECRET); // Implementar HMAC em JS
    
    const response = await fetch('http://69.169.102.84:5000/api/leads/capture', {
        method: 'POST',
        headers: {
            'X-Project-Key': 'vitrinezap',
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
    });
    
    return response.json();
}
```

## 📊 Admin Django

Acesse `/admin/app_leads/` para:
- ✅ Gerenciar credenciais de projetos (`ProjectCredential`)
- ✅ Visualizar todos os leads (`Lead`)
- ✅ Ver eventos de auditoria (`LeadEvent`)

## 🚀 Próximos Passos

1. **Criar credencial para VitrineZap:**
   - Acessar Django Admin
   - Criar `ProjectCredential` com:
     - `project_key`: "vitrinezap"
     - `project_secret`: Gerar secret seguro (ex: `openssl rand -hex 32`)
     - `is_active`: True

2. **Integrar no VitrineZap:**
   - Implementar view backend (Opção 1)
   - Atualizar form HTML para POST na view do VitrineZap
   - Testar captação

3. **Repetir para outros projetos:**
   - MotoPro, Eventix, MrFoo, etc.
   - Cada um com seu próprio `project_key` e `project_secret`

## 🔍 Monitoramento

- **Eventos rejeitados:** Verificar `LeadEvent` com `event_type="rejected"`
- **Rate limits:** Verificar `LeadEvent` com `event_type="rate_limited"`
- **Leads por sistema:** Filtrar `Lead` por `source_system`

## 📝 Notas

- O endpoint aceita POST cross-site (`@csrf_exempt`) para permitir requisições de múltiplos projetos
- Rate limit: 20 requisições/minuto por IP
- Honeypot: Campo `website` (se preenchido, retorna sucesso silencioso)
- Timestamp válido: ±5 minutos da hora atual

