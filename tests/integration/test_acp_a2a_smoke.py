"""
Smoke / integração: ACP tasks, A2A run, MCP Resources.
Requer Core Django rodando (docker compose ou local).
PR5 — Hardening + testes.
"""
import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 15
web_config = SERVICES["web"]
base = web_config["root_url"].rstrip("/")


class TestAcpSmoke:
    """POST /acp/tasks/ (criar tarefa) e GET /acp/tasks/<id>/."""

    def test_acp_create_task_noop(self):
        """Cria AgentTask com payload noop e verifica resposta."""
        try:
            resp = requests.post(
                f"{base}/acp/tasks/",
                json={
                    "agent_name": "smoke_test",
                    "payload": {
                        "tool": "noop",
                        "version": "1.0",
                        "input": {"reason": "smoke"},
                    },
                },
                timeout=TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            pytest.skip("Core Web não está rodando")
        if resp.status_code in (404, 501):
            pytest.skip("ACP não registrado (rota ausente)")
        assert resp.status_code in (200, 201), resp.text
        data = resp.json()
        assert "task_id" in data
        assert data.get("status") in ("PENDING", "RUNNING", "COMPLETED")

    def test_acp_get_task(self):
        """GET /acp/tasks/<id>/ retorna 404 para UUID inválido ou 200 para existente."""
        try:
            resp = requests.get(
                f"{base}/acp/tasks/00000000-0000-0000-0000-000000000000/",
                timeout=TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            pytest.skip("Core Web não está rodando")
        if resp.status_code == 404:
            assert resp.json().get("error") or "task" in resp.text.lower()
        else:
            assert resp.status_code == 200


class TestA2ASmoke:
    """POST /a2a/run e GET /a2a/tasks/<id>/."""

    def test_a2a_run_post(self):
        """POST /a2a/run com input mínimo."""
        try:
            resp = requests.post(
                f"{base}/a2a/run",
                json={"input": "listar catálogo"},
                timeout=TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            pytest.skip("Core Web não está rodando")
        if resp.status_code == 503:
            data = resp.json()
            if data.get("code") == "A2A_DISABLED":
                pytest.skip("A2A desabilitado por feature flag")
        if resp.status_code == 404:
            pytest.skip("A2A não registrado")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "trace_id" in data
        assert "status" in data
        # Pode vir task_id (ACP) ou result (sync)
        assert "task_id" in data or "result" in data or "status" in data


class TestResourcesSmoke:
    """GET /core/resources/ e /core/resources/list/."""

    def test_resources_get_requires_uri(self):
        """GET /core/resources/ sem uri retorna 400."""
        try:
            resp = requests.get(f"{base}/core/resources/", timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            pytest.skip("Core Web não está rodando")
        if resp.status_code == 404:
            pytest.skip("MCP Resources não registrado")
        assert resp.status_code == 400
        data = resp.json()
        assert "uri" in data.get("error", "").lower() or "uri" in str(data)

    def test_resources_list_requires_uri(self):
        """GET /core/resources/list/ sem uri retorna 400."""
        try:
            resp = requests.get(f"{base}/core/resources/list/", timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            pytest.skip("Core Web não está rodando")
        if resp.status_code == 404:
            pytest.skip("MCP Resources não registrado")
        assert resp.status_code == 400
