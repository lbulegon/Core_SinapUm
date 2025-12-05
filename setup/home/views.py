from django.shortcuts import render
from django.http import JsonResponse
import socket
import platform
from datetime import datetime


def home(request):
    """Página inicial do servidor."""
    context = {
        'server_info': {
            'hostname': socket.gethostname(),
            'ip': _get_server_ip(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        },
        'services': [
            {
                'name': 'OpenMind AI Server',
                'port': 8000,
                'status': 'running',
                'description': 'API FastAPI para análise de imagens com IA'
            },
            {
                'name': 'Grafana',
                'port': 3000,
                'status': 'running',
                'description': 'Dashboard de monitoramento e visualização'
            },
            {
                'name': 'Django - Página Inicial',
                'port': 80,
                'status': 'running',
                'description': 'Página inicial do servidor (este site)'
            }
        ]
    }
    return render(request, 'home/index.html', context)


def api_status(request):
    """Endpoint de status da API."""
    return JsonResponse({
        'status': 'online',
        'server': socket.gethostname(),
        'timestamp': datetime.now().isoformat(),
        'services': {
            'django': 'running',
            'openmind_ai': 'running',
            'grafana': 'running'
        }
    })


def _get_server_ip():
    """Obtém o IP do servidor."""
    try:
        # Conecta a um servidor externo para descobrir o IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

