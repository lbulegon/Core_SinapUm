from django.urls import path
from . import views

urlpatterns = [
    path("run", views.run, name="a2a_run"),
    path("tasks/<uuid:task_id>", views.get_task, name="a2a_get_task"),
]
