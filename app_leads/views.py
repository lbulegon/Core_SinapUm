"""
Views do Lead Registry - Endpoint de captação com hardening HMAC.
"""
import logging
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Lead, LeadEvent
from .utils import (
    validate_hmac_signature,
    get_client_ip,
    rate_limit_check
)

logger = logging.getLogger(__name__)


@csrf_exempt  # Permite POST cross-site (de múltiplos projetos)
@require_POST
def capture_lead(request):
    """
    Endpoint de captação de leads com validação HMAC.
    
    Fluxo:
    1. Honeypot check
    2. Rate limit por IP
    3. Validação HMAC
    4. Validação de campos
    5. Salvar lead e evento
    6. Retornar resposta (JSON ou redirect)
    """
    # ============================================================
    # 1. HONEYPOT CHECK (anti-bot básico)
    # ============================================================
    honeypot = (request.POST.get("website") or "").strip()
    if honeypot:
        # Bot preencheu o campo honeypot - retornar sucesso silencioso
        logger.warning(f"Honeypot triggered from IP: {get_client_ip(request)}")
        return JsonResponse({"ok": True}, status=200)
    
    # ============================================================
    # 2. RATE LIMIT POR IP
    # ============================================================
    if not rate_limit_check(request, limit=20, window_seconds=60):
        ip = get_client_ip(request)
        logger.warning(f"Rate limit exceeded from IP: {ip}")
        
        # Registrar evento de rate limit (sem lead associado)
        LeadEvent.objects.create(
            lead=None,  # Sem lead ainda
            event_type="rate_limited",
            ip=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:2000],
            referrer=request.META.get("HTTP_REFERER", "")[:2000],
        )
        
        return JsonResponse(
            {"ok": False, "error": "rate_limited"},
            status=429
        )
    
    # ============================================================
    # 3. VALIDAÇÃO HMAC
    # ============================================================
    project_key = request.headers.get("X-Project-Key", "").strip()
    signature = request.headers.get("X-Signature", "").strip()
    timestamp = request.headers.get("X-Timestamp", "").strip()
    
    # Extrair dados do lead para validação HMAC
    email = (request.POST.get("email") or "").strip()
    whatsapp = (request.POST.get("whatsapp") or "").strip()
    
    # Log detalhado para debug
    logger.info(
        f"🔐 HMAC Validation - IP: {get_client_ip(request)} | "
        f"Project Key: {project_key} | "
        f"Timestamp: {timestamp} | "
        f"Email: {email} | "
        f"WhatsApp: {whatsapp} | "
        f"Signature (first 20): {signature[:20] if signature else 'MISSING'}..."
    )
    
    # Validar presença dos headers obrigatórios
    if not (project_key and signature and timestamp):
        missing = []
        if not project_key:
            missing.append("X-Project-Key")
        if not signature:
            missing.append("X-Signature")
        if not timestamp:
            missing.append("X-Timestamp")
        logger.warning(
            f"❌ Missing HMAC headers: {', '.join(missing)} from IP: {get_client_ip(request)}"
        )
        return JsonResponse(
            {"ok": False, "error": "missing_authentication", "message": f"Headers faltando: {', '.join(missing)}"},
            status=401
        )
    
    # Validar assinatura HMAC
    is_valid, error_msg = validate_hmac_signature(
        project_key=project_key,
        signature=signature,
        timestamp=timestamp,
        email=email,
        whatsapp=whatsapp
    )
    
    if not is_valid:
        logger.warning(
            f"❌ HMAC validation failed: {error_msg} | "
            f"IP: {get_client_ip(request)} | "
            f"Project Key: {project_key} | "
            f"Timestamp: {timestamp}"
        )
        
        # Registrar evento de rejeição (sem lead associado)
        LeadEvent.objects.create(
            lead=None,
            event_type="rejected",
            ip=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:2000],
            referrer=request.META.get("HTTP_REFERER", "")[:2000],
        )
        
        return JsonResponse(
            {"ok": False, "error": "authentication_failed", "message": error_msg},
            status=403
        )
    
    logger.info(f"✅ HMAC validation successful for project: {project_key}")
    
    # ============================================================
    # 4. VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
    # ============================================================
    nome = (request.POST.get("nome") or "").strip()
    cidade = (request.POST.get("cidade") or "").strip()
    
    if not (nome and whatsapp and email):
        error_msg = "Por favor, preencha Nome, WhatsApp e E-mail."
        
        # Se for form HTML (não AJAX), redirecionar com mensagem
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
            messages.error(request, error_msg)
            return_url = request.POST.get("return_url") or "/"
            return redirect(return_url)
        
        # Se for AJAX, retornar JSON
        return JsonResponse(
            {"ok": False, "error": "validation_failed", "message": error_msg},
            status=400
        )
    
    # ============================================================
    # 5. EXTRAIR DADOS ADICIONAIS
    # ============================================================
    source_system = (request.POST.get("source_system") or "unknown").strip()
    source_entrypoint = (request.POST.get("source_entrypoint") or "").strip()
    source_context = (request.POST.get("source_context") or "").strip()
    
    # UTM parameters (pode vir via POST ou querystring)
    utm_source = (
        request.POST.get("utm_source") or
        request.GET.get("utm_source") or
        ""
    ).strip()
    utm_campaign = (
        request.POST.get("utm_campaign") or
        request.GET.get("utm_campaign") or
        ""
    ).strip()
    utm_medium = (
        request.POST.get("utm_medium") or
        request.GET.get("utm_medium") or
        ""
    ).strip()
    utm_content = (
        request.POST.get("utm_content") or
        request.GET.get("utm_content") or
        ""
    ).strip()
    
    # ============================================================
    # 6. SALVAR LEAD (update_or_create por email)
    # ============================================================
    lead, created = Lead.objects.update_or_create(
        email=email,
        defaults={
            "nome": nome,
            "whatsapp": whatsapp,
            "cidade": cidade,
            "source_system": source_system,
            "source_entrypoint": source_entrypoint,
            "source_context": source_context,
            "utm_source": utm_source,
            "utm_campaign": utm_campaign,
            "utm_medium": utm_medium,
            "utm_content": utm_content,
            "is_opt_out": False,
        },
    )
    
    # ============================================================
    # 7. REGISTRAR EVENTO DE AUDITORIA
    # ============================================================
    LeadEvent.objects.create(
        lead=lead,
        event_type="created" if created else "updated",
        ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:2000],
        referrer=request.META.get("HTTP_REFERER", "")[:2000],
    )
    
    logger.info(
        f"Lead {'created' if created else 'updated'}: {lead.email} "
        f"from {source_system} (IP: {get_client_ip(request)})"
    )
    
    # ============================================================
    # 8. RETORNAR RESPOSTA
    # ============================================================
    # Se for chamada AJAX/fetch, retornar JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "ok": True,
            "lead_id": lead.id,
            "created": created
        })
    
    # Se for form HTML normal, redirecionar
    return_url = request.POST.get("return_url") or "/"
    messages.success(request, "Cadastro realizado com sucesso!")
    return redirect(return_url)

