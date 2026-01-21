# Testes de Regressão - SparkScore Service

## Objetivo

Garantir que endpoints existentes não quebram após mudanças no código.

## Como Usar

### 1. Gerar Snapshots (Checkpoint 0)

Primeiro, certifique-se de que o serviço está rodando:

```bash
cd /root/Core_SinapUm/services/sparkscore_service
docker compose up -d
# ou
uvicorn app.main:app --host 0.0.0.0 --port 8006
```

Depois, gere os snapshots:

```bash
python tests/regression/generate_snapshots.py
```

Isso criará arquivos em `tests/regression/snapshots/` com exemplos de request/response de cada endpoint.

### 2. Rodar Testes de Regressão

```bash
pytest tests/regression/test_endpoints_regression.py -v
```

Os testes comparam as respostas atuais com os snapshots salvos.

### 3. Atualizar Snapshots (se necessário)

Se você fizer mudanças intencionais que alterem as respostas, atualize os snapshots:

```bash
python tests/regression/generate_snapshots.py
```

**⚠️ ATENÇÃO:** Só atualize snapshots se você tiver certeza de que as mudanças são intencionais e compatíveis.

## Estrutura

```
tests/regression/
├── generate_snapshots.py          # Script para gerar snapshots
├── test_endpoints_regression.py   # Testes de regressão
├── snapshots/                     # Golden files (não commitar)
│   ├── analyze_snapshot.json
│   ├── classify_orbital_snapshot.json
│   ├── semiotic_snapshot.json
│   ├── psycho_snapshot.json
│   ├── metric_snapshot.json
│   ├── orbitals_snapshot.json
│   └── ...
└── README.md                      # Este arquivo
```

## Critérios de Aceite

- [ ] Todos os snapshots gerados
- [ ] Todos os testes de regressão passam
- [ ] Estrutura de resposta mantida
- [ ] Campos obrigatórios presentes
- [ ] Tipos de dados corretos

