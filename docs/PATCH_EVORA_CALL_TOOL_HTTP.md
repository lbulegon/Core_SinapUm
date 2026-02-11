# Patch: _call_tool() HTTP no EvoraMCPClient

Aplicar em: `/root/Core_SinapUm/app_mcp/clients/evora_mcp_client.py`

---

## A) Import no topo do arquivo

Adicione (junto aos outros imports):

    import requests

---

## B) Substituir o método _call_tool inteiro por:

    def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chamada MCP via HTTP no padrão:
          POST {EVORA_MCP_URL}/mcp/call
          body: {"tool": "<nome>", "input": {...}}
        retorno esperado:
          {"output": {...}}  (ou o payload direto)
        """
        if not self.evora_mcp_url:
            raise EvoraMCPClientError("EVORA_MCP_URL não configurada")

        url = f"{self.evora_mcp_url.rstrip('/')}/mcp/call"

        headers = {"Content-Type": "application/json"}
        if self.evora_mcp_token:
            headers["Authorization"] = f"Bearer {self.evora_mcp_token}"

        payload = {"tool": tool_name, "input": tool_input}

        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)

        if resp.status_code >= 400:
            raise EvoraMCPClientError(f"MCP HTTP {resp.status_code}: {resp.text[:500]}")

        try:
            data = resp.json()
        except Exception as e:
            raise EvoraMCPClientError("Resposta MCP não é JSON válido") from e

        return data.get("output", data)

---

Com isso: se EVORA_MCP_URL estiver setada e o Evora expuser /mcp/call, o Core usa MCP real; senão continua o fallback.
