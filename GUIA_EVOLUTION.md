# Guia Rápido - Evolution API (Porta 8004)

## 🚀 Como Subir o Serviço

### Opção 1: Usando o script (recomendado)
```bash
cd /root/Core_SinapUm
./start_evolution.sh
```

### Opção 2: Comandos Docker diretos

#### Iniciar o container:
```bash
docker start evolution_api
```

#### Se o container não existir, criar e iniciar:
```bash
cd /root/Core_SinapUm
docker compose up -d evolution_api
```

#### Iniciar todos os serviços relacionados (Evolution + PostgreSQL + Redis):
```bash
cd /root/Core_SinapUm
docker compose up -d
```

## 🔍 Verificar Status

```bash
# Ver se está rodando
docker ps | grep evolution

# Ver status detalhado
docker ps --filter "name=evolution_api"

# Ver logs
docker logs evolution_api --tail 50

# Ver logs em tempo real
docker logs -f evolution_api
```

## 🔄 Reiniciar o Serviço

### Reiniciar apenas Evolution API:
```bash
docker restart evolution_api
```

### Reiniciar todos os serviços:
```bash
cd /root/Core_SinapUm
./restart_services.sh
```

## 🛑 Parar o Serviço

```bash
# Parar Evolution API
docker stop evolution_api

# Parar todos os serviços
cd /root/Core_SinapUm
docker compose stop
```

## 🔧 Reset Completo (quando há problemas)

```bash
cd /root/Core_SinapUm
./reset_evolution.sh
```

Este script:
- Deleta todas as instâncias WhatsApp
- Reinicia o container
- Limpa sessões corrompidas

## ✅ Verificar se está Funcionando

```bash
# Teste simples
curl http://127.0.0.1:8004/

# Deve retornar:
# {"status":200,"message":"Welcome to the Evolution API..."}

# Ver instâncias
curl -H "apikey: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg" \
  http://127.0.0.1:8004/instance/fetchInstances
```

## 📋 Informações do Serviço

- **URL**: http://69.169.102.84:8004
- **Container**: `evolution_api`
- **Porta**: 8004 (externa) → 8080 (interna)
- **API Key**: GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg
- **Versão**: v2.1.1

## 🐛 Troubleshooting

### Serviço não inicia:
```bash
# Ver logs de erro
docker logs evolution_api --tail 100

# Verificar se porta está em uso
sudo ss -lntp | grep 8004

# Verificar recursos do sistema
docker stats evolution_api
```

### Serviço está lento/travando:
```bash
# Reiniciar
docker restart evolution_api

# Ver uso de memória
docker stats evolution_api --no-stream
```

### QR Code não aparece:
```bash
# Reset completo
./reset_evolution.sh

# Ver logs do Baileys
docker logs evolution_api | grep -i "connection\|qrcode\|baileys"
```

