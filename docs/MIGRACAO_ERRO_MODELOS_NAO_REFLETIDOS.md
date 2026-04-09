# Erro: "Your models have changes that are not yet reflected in a migration"

## Por que esse erro aparece?

O Django compara o estado atual dos **models** (código em `models.py`) com o estado que resulta de **aplicar todas as migrations** do app. Quando os dois não batem, ele **não aplica** novas migrations e pede para você gerar as que faltam.

No seu caso, o Django apontou dois apps:

1. **`app_acp`** — pode haver pequena diferença entre o `AgentTask` no código e o que está na migration `0001_initial.py` (por exemplo, ordem de opções no `Meta` ou índices).
2. **`whatsapp`** — é o app `core.services.whatsapp` (label interno `whatsapp`). Pode ter mudança no modelo (ex.: uso de `JSONField` em vez de `jsonb`) que ainda não virou migration.

Enquanto existir essa divergência em **qualquer** app, o `migrate` (mesmo só para `app_acp`) é bloqueado.

## Como corrigir

Rode estes comandos **no mesmo ambiente onde você roda o Django** (por exemplo, dentro do container `web` ou com o venv ativado):

```bash
# 1. Gerar migrations para os apps com alterações (Django descobre sozinho)
python manage.py makemigrations app_acp
python manage.py makemigrations

# 2. Se o makemigrations criou arquivos novos, aplicar tudo
python manage.py migrate
```

Se você usa Docker:

```bash
cd /root/Core_SinapUm
docker compose run --rm web python manage.py makemigrations app_acp
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate
```

- **`makemigrations app_acp`** — gera só migrations do `app_acp` (por exemplo, um `0002_...` se houver diferença em relação à `0001_initial`).
- **`makemigrations`** (sem app) — gera migrations para **todos** os apps com mudanças (incluindo `whatsapp`).
- **`migrate`** — aplica todas as migrations pendentes.

Depois disso, o erro de “models have changes that are not yet reflected in a migration” tende a sumir e o `migrate app_acp` (e o restante) passa a funcionar.
