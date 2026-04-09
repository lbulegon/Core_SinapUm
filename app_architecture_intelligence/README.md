# app_architecture_intelligence

App Django para persistência do Architecture Intelligence Service.
Usa **migrations** (não SQL direto).

## Integração no projeto Django

### 1. Adicionar ao INSTALLED_APPS

Em `setup/settings.py` (ou seu settings):

```python
INSTALLED_APPS = [
    # ...
    "app_architecture_intelligence",
]
```

### 2. Garantir que o app está no Python path

Se o app está em `Core_SinapUm/app_architecture_intelligence/`, adicione ao `sys.path` ou instale o pacote.

### 3. Rodar migrations

```bash
python manage.py makemigrations app_architecture_intelligence  # se precisar regenerar
python manage.py migrate app_architecture_intelligence
```

### 4. Uso no Architecture Intelligence Service (FastAPI)

O serviço em `services/architecture_intelligence_service/` pode usar o DjangoRepository quando `AIS_STORAGE_BACKEND=postgres` e Django estiver configurado.
