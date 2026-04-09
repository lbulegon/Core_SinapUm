# Monitoramento de Containers Docker via Grafana

## Situação atual

O stack de monitoramento já está rodando em **`/opt/monitoring/`**:

| Serviço        | Porta | URL                          | Função                          |
|----------------|-------|------------------------------|---------------------------------|
| **Grafana**    | 3000  | http://69.169.102.84:3000    | Dashboards e visualização       |
| **Prometheus** | 9090  | http://69.169.102.84:9090    | Coleta e armazena métricas     |
| **cAdvisor**   | 8080  | http://69.169.102.84:8080    | Métricas dos containers Docker |
| **Node Exporter** | 9100 | http://69.169.102.84:9100 | Métricas do host (CPU, memória) |

O **cAdvisor** já coleta métricas de **todos** os containers do servidor (incluindo Core_SinapUm, Evolution API, MySQL, etc.), pois tem acesso ao `/var/lib/docker`.

---

## 1. Conectar Grafana ao Prometheus

1. Acesse: http://69.169.102.84:3000/login  
2. Login: `admin` / Senha: `TroqueEstaSenha123` (altere após o primeiro login)  
3. Vá em **Configuration** (ícone engrenagem) → **Data sources**  
4. Clique em **Add data source**  
5. Selecione **Prometheus**  
6. Em **URL**, use: `http://prometheus:9090` (ambos estão na rede `monitor-net`)  
7. Clique em **Save & Test** – deve aparecer "Data source is working"

---

## 2. Importar dashboards prontos

### Dashboard de containers (cAdvisor)

1. No Grafana: **Dashboards** → **New** → **Import**  
2. Digite o ID: **893** (Docker Container & Host Metrics)  
3. Clique em **Load**  
4. Selecione o data source **Prometheus**  
5. Clique em **Import**

### Outros dashboards úteis

| ID     | Nome                         | Descrição                    |
|--------|------------------------------|------------------------------|
| 893    | Docker Container & Host      | CPU, memória por container   |
| 11600  | Docker and system monitoring | Containers + sistema         |
| 14282  | cAdvisor exporter            | Focado em cAdvisor           |
| 1860   | Node Exporter Full           | Métricas do host (CPU, disco)|

---

## 3. Estrutura do monitoramento

```
/opt/monitoring/
├── docker-compose.yml
└── prometheus/
    └── prometheus.yml
```

**prometheus.yml** já está configurado para:
- `prometheus:9090` – métricas do próprio Prometheus
- `node-exporter:9100` – métricas do host
- `cadvisor:8080` – métricas de todos os containers

---

## 4. Containers monitorados

O cAdvisor coleta métricas de todos os containers em execução, incluindo:

- `mcp_sinapum_web`, `mcp_sinapum_openmind`, `mcp_sinapum_mcp`
- `mcp_sinapum_ddf`, `mcp_sinapum_sparkscore`, `mcp_sinapum_shopperbot`
- `mcp_sinapum_whatsapp_gateway`, `mcp_sinapum_vectorstore`, `mcp_sinapum_worldgraph`
- `evolution-api`, `sinapum_mysql`, `sinapum_phpmyadmin`
- `grafana`, `prometheus`, `cadvisor`, `node-exporter`
- entre outros

---

## 5. Subir/reiniciar o stack de monitoramento

```bash
cd /opt/monitoring
docker compose up -d
```

---

## 6. Consultas Prometheus úteis

No Grafana, ao criar um painel, use:

- **CPU por container:**  
  `rate(container_cpu_usage_seconds_total{name!=""}[5m])`
- **Memória por container:**  
  `container_memory_usage_bytes{name!=""}`
- **Containers em execução:**  
  `count(container_last_seen{name!=""})`

---

## 7. Como interpretar as métricas

### Filtros do dashboard

Use **container_name** para ver um container específico (ex.: `mcp_sinapum_web`, `evolution-api`). Com "All", os gráficos mostram a **soma** de todos os containers.

---

### Seção **misc** (estado geral)

| Métrica | O que significa | O que observar |
|---------|-----------------|----------------|
| `container_start_time` | Quando o container iniciou | Útil para calcular uptime |
| `container_last_seen` | Última vez que métricas foram coletadas | Se parar de atualizar, o container pode ter travado |
| `container_tasks_state` | Estados das tarefas: running, sleeping, stopped | Maioria em "running" ou "sleeping" = normal |
| `container_oom_events_total` | Eventos de falta de memória (OOM) | **0 = bom**. Se subir, o container está sendo morto por falta de RAM |
| `container_scrape_error` | Erros ao coletar métricas | **0 = bom**. Se subir, há problema no cAdvisor ou Prometheus |

---

### Seção **cpu**

| Métrica | O que significa | O que observar |
|---------|-----------------|----------------|
| `container_cpu_system` | Tempo de CPU em modo kernel | Picos = muitas chamadas de sistema (I/O, rede) |
| `container_cpu_user` | Tempo de CPU em modo usuário | Código da aplicação rodando |
| `container_cpu_usage` | Uso total de CPU | Alto e estável = carga contínua; picos = picos de processamento |
| `container_cpu_cfs_throttled_*` | CPU limitada pelo scheduler | "No data" = sem limite de CPU ou sem throttling |

**Referência:** Em um host com 4 CPUs, ~4 segundos de uso = 100% de uma CPU.

---

### Seção **memory**

| Métrica | O que significa | O que observar |
|---------|-----------------|----------------|
| `container_memory_usage_bytes` | Memória total usada (inclui cache) | Tendência de crescimento = possível vazamento |
| `container_memory_working_set_bytes` | Memória "ativa" em RAM | Mais relevante que usage_bytes para pressão de memória |
| `container_memory_rss` | Memória residente (em RAM) | Similar ao working set |
| `container_memory_cache` | Memória usada como cache de disco | Pode ser liberada pelo sistema se precisar |
| `container_memory_swap` | Uso de swap | Alto = RAM insuficiente, risco de lentidão |
| `container_memory_failures_total` | Falhas de alocação de memória | **0 = bom** |
| `container_memory_max_usage_bytes` | Pico histórico de memória | Ajuda a dimensionar limites |

**Referência:** ~4,5 GB de uso estável = carga de memória consistente. Se `memory_usage` se aproximar do limite do container, há risco de OOM.

---

### Seção **network**

| Métrica | O que significa |
|---------|-----------------|
| `container_network_receive_bytes_total` | Bytes recebidos |
| `container_network_transmit_bytes_total` | Bytes enviados |

"No data" em alguns painéis pode ser normal se o container não tiver tráfego ou se a métrica não existir para aquele tipo de cgroup.

---

### Sinais de alerta

| Situação | Ação sugerida |
|----------|----------------|
| `container_oom_events_total` > 0 | Aumentar limite de memória ou otimizar a aplicação |
| `container_memory_swap` alto | Avaliar mais RAM ou reduzir uso de memória |
| `container_cpu_usage` constantemente no máximo | Avaliar mais CPUs ou otimizar o código |
| `container_scrape_error` > 0 | Verificar cAdvisor e Prometheus |
| `container_last_seen` parado | Verificar se o container está rodando |

---

### Painéis com "No data"

Alguns painéis (ex.: `docker compose project`, `container_cpu_cfs_throttled`) podem ficar vazios porque:

- A métrica não existe para todos os containers
- O container não tem limite de CPU configurado
- O projeto não usa Docker Compose com esses labels

Isso é esperado e não indica problema.

---

## 8. Segurança

- Altere a senha padrão do Grafana após o primeiro login  
- Considere restringir o acesso às portas 9090, 8080 e 9100 apenas para IPs internos ou VPN

---

## 8. Como interpretar as métricas

### Filtros
Use **container_name** para ver um container específico (ex: mcp_sinapum_web, evolution-api). Com "All", os gráficos mostram a SOMA de todos os containers.

### Seção misc (estado geral)
- container_start_time: quando o container iniciou
- container_last_seen: última coleta de métricas
- container_tasks_state: running, sleeping, stopped
- container_oom_events_total: 0 = bom. Se subir = OOM (falta de RAM)
- container_scrape_error: 0 = bom. Erros na coleta

### Seção cpu
- container_cpu_system: tempo em modo kernel
- container_cpu_user: tempo em modo usuário (aplicação)
- container_cpu_usage: uso total. Alto e estável = carga contínua

### Seção memory
- container_memory_usage_bytes: memória total (inclui cache)
- container_memory_working_set_bytes: memória ativa em RAM
- container_memory_rss: memória residente
- container_memory_swap: uso de swap. Alto = RAM insuficiente
- container_memory_failures_total: 0 = bom

### Sinais de alerta
- OOM events > 0: aumentar RAM ou otimizar
- memory_swap alto: falta de RAM
- cpu_usage no máximo: mais CPUs ou otimizar
- scrape_error > 0: verificar cAdvisor/Prometheus

### Painéis "No data"
Normal em docker compose, CFS throttled - nem todos os containers expõem essas métricas.
