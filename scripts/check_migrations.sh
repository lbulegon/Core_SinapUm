#!/bin/sh
# Verifica estado das migrations do app_mcp_tool_registry
echo "=== Migrations app_mcp_tool_registry ==="
docker compose run --rm --entrypoint "" web sh -c "python manage.py showmigrations app_mcp_tool_registry" 2>/dev/null || true
