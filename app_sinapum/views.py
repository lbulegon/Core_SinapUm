from django.shortcuts import render

def home(request):
    """View para a página inicial com menu."""
    context = {
        'grafana_url': 'http://69.169.102.84:3000/login',
    }
    return render(request, 'app_sinapum/home.html', context)
