"""
URL configuration for Open Finance Gateway Service.
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include


def health_view(request):
    return HttpResponse('OK', content_type='text/plain')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/openfinance/', include('openfinance.urls')),
    path('health/', health_view),
]
