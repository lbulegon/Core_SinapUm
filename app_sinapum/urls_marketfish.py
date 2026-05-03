from django.urls import path

from app_sinapum import views_marketfish_tasks

urlpatterns = [
    path("tasks/create/", views_marketfish_tasks.create_task, name="sinapum-marketfish-create"),
    path("tasks/result/", views_marketfish_tasks.receive_result, name="sinapum-marketfish-result"),
]
