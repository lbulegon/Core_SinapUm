"""
Configuração Django mínima para demonstrar o agent_core isoladamente.

Uso na raiz do repositório Core_SinapUm:

    export DJANGO_SETTINGS_MODULE=demo_settings
    python -m agent_core.examples.run_agent_demo

No dia a dia use setup.settings (manage.py).
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SECRET_KEY = "demo-not-for-production"
DEBUG = True
ALLOWED_HOSTS: list[str] = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "agent_core.apps.AgentCoreConfig",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db_agent_core_demo.sqlite3"),
    }
}

USE_TZ = True
TIME_ZONE = "UTC"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
