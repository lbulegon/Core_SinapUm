"""
Views para integração com Evolution API (WhatsApp)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .evolution_service import get_evolution_service
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def whatsapp_connect(request):
    """
    View principal para conectar WhatsApp via Evolution API
    Mostra QR code ou status da conexão
    """
    service = get_evolution_service()
    instance_name = service.instance_name if hasattr(service, 'instance_name') else 'core_sinapum'
    
    # Verificar status da instância
    status_result = service.get_instance_status(instance_name)
    
    # Se a instância não existe, não é erro crítico - apenas significa que precisa ser criada
    instance_not_found = False
    if not status_result.get('success') and 'não encontrada' in status_result.get('error', '').lower():
        instance_not_found = True
        status_result = {'success': False, 'status': 'not_found'}
    
    context = {
        'instance_name': instance_name,
        'status': status_result.get('status', 'close') if status_result.get('success') else ('not_found' if instance_not_found else 'error'),
        'connected': status_result.get('status') == 'open' if status_result.get('success') else False,
        'profile_name': status_result.get('profile_name'),
        'number': status_result.get('number'),
        'error': status_result.get('error') if not status_result.get('success') and not instance_not_found else None,
        'instance_not_found': instance_not_found,
    }
    
    return render(request, 'app_sinapum/whatsapp_connect.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_create_instance(request):
    """
    Endpoint AJAX para criar uma nova instância WhatsApp
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        instance_name = data.get('instance_name', 'core_sinapum')
        
        service = get_evolution_service()
        
        # Primeiro verificar se a instância já existe
        status_result = service.get_instance_status(instance_name)
        if status_result.get('success'):
            # Instância já existe
            status = status_result.get('status')
            if status == 'close':
                # Instância existe mas está fechada, deletar e recriar para gerar QR code
                logger.info(f"Instância '{instance_name}' está desconectada. Deletando para recriar...")
                delete_result = service.delete_instance(instance_name)
                if delete_result.get('success'):
                    # Aguardar um pouco antes de recriar para garantir que a deleção foi processada
                    import time
                    time.sleep(2)
                    # Agora criar novamente
                    result = service.create_instance(instance_name)
                    if result.get('success'):
                        logger.info(f"Instância '{instance_name}' recriada com sucesso")
                        return JsonResponse({
                            'success': True,
                            'message': f'Instância "{instance_name}" recriada. Aguarde alguns segundos para o QR code ser gerado.',
                            'instance_exists': False,
                            'status': 'creating',
                            'recreated': True
                        })
                    else:
                        # Se falhou ao criar, retornar erro
                        logger.error(f"Erro ao recriar instância '{instance_name}': {result.get('error')}")
                        return JsonResponse({
                            'success': False,
                            'error': f"Erro ao recriar instância: {result.get('error', 'Erro desconhecido')}",
                            'instance_name': instance_name
                        }, status=500)
                else:
                    # Se falhou ao deletar, tentar criar mesmo assim (pode ser que já tenha sido deletada)
                    logger.warning(f"Erro ao deletar instância '{instance_name}': {delete_result.get('error')}. Tentando criar mesmo assim...")
                    import time
                    time.sleep(1)
                    result = service.create_instance(instance_name)
                    if result.get('success'):
                        return JsonResponse({
                            'success': True,
                            'message': f'Instância "{instance_name}" criada com sucesso.',
                            'instance_exists': False,
                            'status': 'creating'
                        })
                    else:
                        # Verificar se o erro é porque já existe
                        error_msg = result.get('error', '')
                        if 'already in use' in error_msg.lower() or 'already exists' in error_msg.lower():
                            # Instância ainda existe, retornar status atual
                            return JsonResponse({
                                'success': True,
                                'message': f'Instância "{instance_name}" já existe e está desconectada. Tente obter o QR code.',
                                'instance_exists': True,
                                'status': 'close',
                                'connected': False
                            })
                        return JsonResponse({
                            'success': False,
                            'error': f"Erro ao criar instância: {error_msg}",
                            'instance_name': instance_name
                        }, status=500)
            
            # Instância existe e está ativa ou conectada
            return JsonResponse({
                'success': True,
                'message': f'Instância "{instance_name}" já existe',
                'instance_exists': True,
                'status': status,
                'connected': status == 'open'
            })
        
        # Se não existe, criar
        result = service.create_instance(instance_name)
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'message': f'Instância "{instance_name}" criada com sucesso',
                'data': result.get('data', {}),
                'instance_exists': False
            })
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            # Verificar se o erro é porque já existe
            if 'already in use' in error_msg.lower() or 'already exists' in error_msg.lower():
                return JsonResponse({
                    'success': True,
                    'message': f'Instância "{instance_name}" já existe',
                    'instance_exists': True,
                    'error': error_msg
                })
            
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=500)
            
    except Exception as e:
        logger.error(f"Erro ao criar instância: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def whatsapp_get_qrcode(request):
    """
    Endpoint AJAX para obter QR code da instância
    """
    try:
        instance_name = request.GET.get('instance_name', 'core_sinapum')
        
        service = get_evolution_service()
        result = service.get_qrcode(instance_name)
        
        if result.get('success'):
            if result.get('connected'):
                return JsonResponse({
                    'success': True,
                    'connected': True,
                    'status': 'connected',
                    'message': 'WhatsApp já está conectado',
                    'profile_name': result.get('profile_name'),
                    'number': result.get('number')
                })
            elif result.get('qrcode_base64') or result.get('qrcode'):
                qrcode = result.get('qrcode_base64') or result.get('qrcode')
                return JsonResponse({
                    'success': True,
                    'qrcode': qrcode,
                    'status': 'qrcode',
                    'message': 'QR code gerado com sucesso'
                })
            elif result.get('status') == 'waiting':
                return JsonResponse({
                    'success': True,
                    'status': 'waiting',
                    'message': result.get('message', 'Aguardando geração do QR code')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'QR code não disponível. Certifique-se de que a instância foi criada.',
                    'status': 'error'
                }, status=404)
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Erro desconhecido'),
                'status': 'error'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Erro ao obter QR code: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def whatsapp_get_status(request):
    """
    Endpoint AJAX para obter status da instância
    """
    try:
        instance_name = request.GET.get('instance_name', 'core_sinapum')
        
        service = get_evolution_service()
        result = service.get_instance_status(instance_name)
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'status': result.get('status'),
                'connected': result.get('status') == 'open',
                'profile_name': result.get('profile_name'),
                'number': result.get('number'),
                'owner_jid': result.get('owner_jid')
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Erro desconhecido'),
                'status': 'error'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'status': 'error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_delete_instance(request):
    """
    Endpoint AJAX para deletar uma instância WhatsApp
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        instance_name = data.get('instance_name', 'core_sinapum')
        
        service = get_evolution_service()
        result = service.delete_instance(instance_name)
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'message': f'Instância "{instance_name}" deletada com sucesso'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Erro desconhecido')
            }, status=500)
            
    except Exception as e:
        logger.error(f"Erro ao deletar instância: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_restart_instance(request):
    """
    Endpoint AJAX para reiniciar uma instância WhatsApp
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        instance_name = data.get('instance_name', 'core_sinapum')
        
        service = get_evolution_service()
        result = service.restart_instance(instance_name)
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'message': f'Instância "{instance_name}" reiniciada com sucesso'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Erro desconhecido')
            }, status=500)
            
    except Exception as e:
        logger.error(f"Erro ao reiniciar instância: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

