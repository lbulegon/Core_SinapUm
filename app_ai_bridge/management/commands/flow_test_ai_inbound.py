"""
Teste de fluxo: POST /ai/inbound com conversa mínima e evento canónico.

Requisitos:
- FEATURE_EVOLUTION_MULTI_TENANT=True (a rota /ai/ só é montada com este flag)
- FEATURE_OPENMIND_ENABLED=True
- OpenMind acessível (OPENMIND_BASE_URL) se quiseres resposta real do serviço

Uso:
  cd /root/Core_SinapUm && . .venv/bin/activate
  export FEATURE_EVOLUTION_MULTI_TENANT=true
  export FEATURE_OPENMIND_ENABLED=true
  python manage.py flow_test_ai_inbound
  python manage.py flow_test_ai_inbound --url http://127.0.0.1:5000
"""

import json
import sys
import uuid

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from app_conversations.models import Conversation, Message


class Command(BaseCommand):
    help = "Cria conversa+evento e testa POST /ai/inbound (Django test client; opcional HTTP)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            default="",
            help="Se definido, também faz POST HTTP a esta base (ex.: http://127.0.0.1:5000).",
        )
        parser.add_argument(
            "--no-create",
            action="store_true",
            help="Não criar conversa; usar --conversation-id existente (obriga --conversation-id).",
        )
        parser.add_argument(
            "--conversation-id",
            type=str,
            default="",
            help="UUID de uma Conversation existente (com --no-create).",
        )

    def handle(self, *args, **options):
        fe = getattr(settings, "FEATURE_EVOLUTION_MULTI_TENANT", False)
        fo = getattr(settings, "FEATURE_OPENMIND_ENABLED", False)
        if not fe:
            self.stdout.write(
                self.style.ERROR(
                    "FEATURE_EVOLUTION_MULTI_TENANT não está ativo. "
                    "Sem isto, /ai/inbound não existe em setup/urls.py. "
                    "Ex.: export FEATURE_EVOLUTION_MULTI_TENANT=true"
                )
            )
        if not fo:
            self.stdout.write(
                self.style.ERROR(
                    "FEATURE_OPENMIND_ENABLED não está ativo. "
                    "Ex.: export FEATURE_OPENMIND_ENABLED=true"
                )
            )
        if not fe or not fo:
            sys.exit(1)

        # Verificar se a rota está montada
        try:
            path = reverse("app_ai_bridge:inbound")
        except NoReverseMatch as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Rota app_ai_bridge:inbound não encontrada: {e}. "
                    "Confirma que os feature flags acima estão ativos e reimporta URLconf."
                )
            )
            sys.exit(1)

        self.stdout.write(f"Rota resolvida: {path}")

        if options.get("no_create"):
            cid = (options.get("conversation_id") or "").strip()
            if not cid:
                self.stdout.write(self.style.ERROR("--no-create requer --conversation-id"))
                sys.exit(1)
            try:
                conv = Conversation.objects.get(id=cid)
            except Conversation.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Conversation {cid} não existe."))
                sys.exit(1)
            if not conv.messages.exists():
                Message.objects.create(
                    conversation=conv,
                    direction=Message.Direction.IN,
                    text="(mensagem mínima para o flow test)",
                    message_type=Message.MessageType.TEXT,
                    timestamp=timezone.now(),
                )
        else:
            sid = f"flow_test_{uuid.uuid4().hex[:8]}"
            inst = f"test_instance_{uuid.uuid4().hex[:8]}"
            key = f"flow_test:whatsapp:+55119{uuid.uuid4().int % 10**8:08d}"
            phone = f"+55119{uuid.uuid4().int % 10**8:08d}"
            conv = Conversation.objects.create(
                shopper_id=sid,
                instance_id=inst,
                conversation_key=key,
                customer_phone=phone,
                customer_name="Teste flow_test_ai_inbound",
                mode=Conversation.Mode.ASSISTIDO,
            )
            Message.objects.create(
                conversation=conv,
                direction=Message.Direction.IN,
                text="Olá, quero ver produtos",
                message_type=Message.MessageType.TEXT,
                timestamp=timezone.now(),
            )
            self.stdout.write(
                self.style.NOTICE(
                    f"Conversa criada: {conv.id} (shopper={sid})"
                )
            )

        event = {
            "type": "message",
            "conversation_id": str(conv.id),
            "text": "Olá, teste de fluxo flow_test_ai_inbound",
            "source": "flow_test",
        }
        # A view recompõe o contexto a partir da Conversation; {} é aceite.
        # (Útil alinhar o body a um cliente real: incluir context ajuda a documentar o contrato.)
        last_msgs = list(
            conv.messages.order_by("-timestamp")[:5].values(
                "direction", "text", "timestamp"
            )
        )
        for m in last_msgs:
            t = m.get("timestamp")
            m["timestamp"] = t.isoformat() if t else ""
        body = {
            "event": event,
            "context": {
                "last_messages": last_msgs,
                "conversation": {
                    "id": str(conv.id),
                    "customer_phone": conv.customer_phone,
                    "customer_name": conv.customer_name or "",
                    "mode": conv.mode,
                },
            },
        }
        body_json = json.dumps(body, ensure_ascii=False)

        # HTTP_HOST evita DisallowedHost (default do Client é "testserver")
        client = Client(HTTP_HOST="127.0.0.1")
        self.stdout.write("--- POST via Django test Client ---")
        resp = client.post(path, data=body_json, content_type="application/json")
        self.stdout.write(f"status_code={resp.status_code}")
        try:
            out = json.loads(resp.content.decode()) if resp.content else {}
            self.stdout.write(json.dumps(out, ensure_ascii=False, indent=2))
        except Exception:
            self.stdout.write(resp.content.decode()[:2000])

        if resp.status_code != 200:
            self.stdout.write(
                self.style.WARNING(
                    "Resposta não-200. Se OpenMind estiver offline, 500 é possível; "
                    "MCP/ToolCallLog ainda deveria ter tentado o caminho openmind."
                )
            )

        base_url = (options.get("url") or "").strip()
        if base_url:
            url = f"{base_url.rstrip('/')}{path}"
            self.stdout.write(f"\n--- POST HTTP: {url} ---")
            self.stdout.write(
                "Nota: o processo Gunicorn (ou outro) na porta 5000 usa o **seu** "
                "DATABASE_URL, OPENMIND_*, etc. O `Client` acima corre neste processo. "
                "Se o HTTP devolver only fallback (intent=unknown, frase genérica) enquanto "
                "o Client traz resposta rica, alinha o .env do serviço web com o do manage.py.\n"
            )
            try:
                r = requests.post(
                    url,
                    data=body_json.encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                )
                self.stdout.write(f"status_code={r.status_code}")
                self.stdout.write(r.text[:3000])
                try:
                    d = r.json() if r.text else {}
                except Exception:
                    d = {}
                fb = (d.get("suggested_reply") or "").strip()
                if (
                    d.get("intent") == "unknown"
                    and "Vou te ajudar" in fb
                    and float(d.get("confidence") or 0) == 0.0
                ):
                    self.stdout.write(
                        self.style.WARNING(
                            "Parece resposta de **fallback** no HTTP. Confirma no contentor `web` "
                            "as variáveis OPENMIND_AI_KEY / OPENMIND_BASE_URL (e a mesma BD que o manage.py, "
                            "se a conversa for criada a partir deste comando)."
                        )
                    )
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"HTTP falhou: {e}"))

        self.stdout.write(self.style.SUCCESS("\nFim do flow_test_ai_inbound."))
