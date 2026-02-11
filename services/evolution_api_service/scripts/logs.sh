#!/bin/bash
set -e
cd "$(dirname "$0")/.."
docker compose logs evolution-api --tail 100 -f
