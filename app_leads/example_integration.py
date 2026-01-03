"""
Exemplo de integração do Lead Registry no VitrineZap (ou qualquer projeto).

Este arquivo mostra como gerar a assinatura HMAC e fazer POST para o Core.
"""

import hmac
import hashlib
import time
import requests
from typing import Dict, Optional


def generate_hmac_signature(
    secret: str,
    project_key: str,
    timestamp: str,
    email: str,
    whatsapp: str
) -> str:
    """
    Gera assinatura HMAC-SHA256 para autenticação no Core.
    
    Args:
        secret: Secret do projeto (ProjectCredential.project_secret)
        project_key: Identificador do projeto
        timestamp: Timestamp Unix (string)
        email: Email do lead
        whatsapp: WhatsApp do lead
    
    Returns:
        Assinatura hexadecimal HMAC-SHA256
    """
    message = f"{project_key}{timestamp}{email}{whatsapp}"
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature


def capture_lead_to_core(
    core_url: str,
    project_key: str,
    project_secret: str,
    nome: str,
    email: str,
    whatsapp: str,
    cidade: Optional[str] = None,
    source_entrypoint: str = "home",
    source_context: str = "lista_antecipada",
    utm_params: Optional[Dict[str, str]] = None,
    return_url: Optional[str] = None,
) -> Dict:
    """
    Capta lead no Core_SinapUm via API.
    
    Args:
        core_url: URL base do Core (ex: "http://69.169.102.84:5000")
        project_key: Identificador do projeto
        project_secret: Secret do projeto
        nome: Nome do lead
        email: Email do lead
        whatsapp: WhatsApp do lead
        cidade: Cidade (opcional)
        source_entrypoint: Ponto de entrada (ex: "home", "modal")
        source_context: Contexto específico (ex: "lista_antecipada")
        utm_params: Dicionário com utm_source, utm_campaign, etc. (opcional)
        return_url: URL de retorno (opcional)
    
    Returns:
        Dicionário com resposta do Core: {"ok": bool, "lead_id": int, "created": bool}
    """
    # Gerar timestamp e assinatura
    timestamp = str(int(time.time()))
    signature = generate_hmac_signature(
        project_secret,
        project_key,
        timestamp,
        email,
        whatsapp
    )
    
    # Headers de autenticação
    headers = {
        'X-Project-Key': project_key,
        'X-Signature': signature,
        'X-Timestamp': timestamp,
        'X-Requested-With': 'XMLHttpRequest',  # Para receber JSON
    }
    
    # Dados do lead
    data = {
        'nome': nome,
        'email': email,
        'whatsapp': whatsapp,
        'source_system': project_key,  # Usar project_key como source_system
        'source_entrypoint': source_entrypoint,
        'source_context': source_context,
    }
    
    if cidade:
        data['cidade'] = cidade
    
    if return_url:
        data['return_url'] = return_url
    
    # Adicionar UTM params se fornecidos
    if utm_params:
        data.update({
            'utm_source': utm_params.get('utm_source', ''),
            'utm_campaign': utm_params.get('utm_campaign', ''),
            'utm_medium': utm_params.get('utm_medium', ''),
            'utm_content': utm_params.get('utm_content', ''),
        })
    
    # Fazer POST para o Core
    endpoint = f"{core_url}/api/leads/capture"
    
    try:
        response = requests.post(endpoint, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "ok": False,
            "error": "request_failed",
            "message": str(e)
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Configurações do VitrineZap
    CORE_URL = "http://69.169.102.84:5000"
    PROJECT_KEY = "vitrinezap"
    PROJECT_SECRET = "seu_secret_aqui"  # Obter do Django Admin (ProjectCredential)
    
    # Dados do lead
    lead_data = {
        "nome": "João Silva",
        "email": "joao@example.com",
        "whatsapp": "5511999999999",
        "cidade": "São Paulo",
        "source_entrypoint": "home",
        "source_context": "lista_antecipada",
        "utm_params": {
            "utm_source": "google",
            "utm_campaign": "lista_antecipada",
            "utm_medium": "cpc",
        },
    }
    
    # Captar lead
    result = capture_lead_to_core(
        core_url=CORE_URL,
        project_key=PROJECT_KEY,
        project_secret=PROJECT_SECRET,
        **lead_data
    )
    
    if result.get("ok"):
        print(f"✅ Lead capturado com sucesso! ID: {result.get('lead_id')}")
    else:
        print(f"❌ Erro ao capturar lead: {result.get('error')} - {result.get('message')}")

