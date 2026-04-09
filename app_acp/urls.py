from django.urls import path
from . import views

app_name = "app_acp"

urlpatterns = [
    path("tasks/", views.create_task, name="create_task"),
    path("tasks/<uuid:task_id>/", views.get_task, name="get_task"),
    path("tasks/<uuid:task_id>/cancel/", views.cancel_task, name="cancel_task"),
]
