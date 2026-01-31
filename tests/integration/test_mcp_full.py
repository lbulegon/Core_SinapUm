"""
Testes de integração MCP - MCP Service, Core Registry e ShopperBot proxy.
Requer serviços rodando (docker compose up).
"""
import pytest
import requests
from tests.services_config import SERVICES

TIMEOUT = 15


@pytest.fixture
def mcp_config():
    return SERVICES["mcp_service"]


@pytest.fixture
def web_config():
    return SERVICES["web"]


@pytest.fixture
def shopperbot_config():
    return SERVICES["shopperbot_service"]


class TestMCPService:
    """Testes do MCP Service (porta 7010)"""

    def test_mcp_service_health(self, mcp_config):
        try:
            resp = requests.get(mcp_config["health_url"], timeout=TIMEOUT)
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("status") == "healthy"
            assert data.get("service") == "mcp_service"
        except requests.exceptions.ConnectionError:
            pytest.skip("MCP Service não está rodando")

    def test_mcp_service_list_tools(self, mcp_config):
        try:
            url = f"{mcp_config['root_url'].rstrip('/')}/mcp/tools"
            resp = requests.get(url, timeout=TIMEOUT)
            if resp.status_code == 503:
                pytest.skip("MCP Service: Core unreachable (deploy em andamento)")
            assert resp.status_code == 200
            tools = resp.json()
            assert isinstance(tools, list)
        except requests.exceptions.ConnectionError:
            pytest.skip("MCP Service não está rodando")


class TestCoreRegistry:
    """Testes do Core Registry (Django /core/)"""

    def test_core_list_tools(self, web_config):
        try:
            url = f"{web_config['root_url'].rstrip('/')}/core/tools/"
            resp = requests.get(url, timeout=TIMEOUT)
            assert resp.status_code == 200
            tools = resp.json()
            assert isinstance(tools, list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Core Web não está rodando")


class TestShopperBotMCP:
    """Testes do ShopperBot proxy MCP (porta 7030)"""

    def test_shopperbot_mcp_tools_list(self, shopperbot_config):
        try:
            url = f"{shopperbot_config['root_url'].rstrip('/')}/v1/mcp/tools"
            resp = requests.get(url, timeout=TIMEOUT)
            if resp.status_code == 404:
                pytest.skip("ShopperBot: router MCP não presente (rebuild necessário)")
            assert resp.status_code == 200
            data = resp.json()
            assert "tools" in data
            assert isinstance(data["tools"], list)
            assert "mcp_enabled" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("ShopperBot não está rodando")

    def test_shopperbot_mcp_call_catalog_search(self, shopperbot_config):
        """Chama catalog.search via ShopperBot - pode retornar 503 se MCP desabilitado"""
        try:
            url = f"{shopperbot_config['root_url'].rstrip('/')}/v1/mcp/call"
            payload = {
                "tool_name": "catalog.search",
                "shopper_id": "test-shopper-001",
                "args": {"query": "arroz"},
            }
            resp = requests.post(url, json=payload, timeout=TIMEOUT)
            if resp.status_code == 404:
                pytest.skip("ShopperBot: router MCP não presente (rebuild necessário)")
            assert resp.status_code in (200, 503)
            if resp.status_code == 200:
                data = resp.json()
                assert "success" in data
                assert data.get("tool_name") == "catalog.search"
        except requests.exceptions.ConnectionError:
            pytest.skip("ShopperBot não está rodando")


class TestDDFMCP:
    """Testes do DDF como servidor MCP (porta 8005)"""

    def test_ddf_mcp_list_tools(self):
        try:
            url = "http://localhost:8005/ddf/mcp/tools"
            resp = requests.get(url, timeout=TIMEOUT)
            if resp.status_code == 404:
                pytest.skip("DDF: rotas MCP não presentes (rebuild necessário)")
            assert resp.status_code == 200
            data = resp.json()
            assert "tools" in data
            assert isinstance(data["tools"], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("DDF Service não está rodando")

    def test_ddf_mcp_call_detect(self):
        config = SERVICES["ddf_service"]
        try:
            base = config["root_url"].rstrip("/")
            url = f"{base}/ddf/mcp/call"
            payload = {"tool": "ddf_detect", "arguments": {"text": "escreva um poema"}}
            resp = requests.post(url, json=payload, timeout=TIMEOUT)
            if resp.status_code == 404:
                pytest.skip("DDF: rotas MCP não presentes (rebuild necessário)")
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("success") is True
            assert "output" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("DDF Service não está rodando")
