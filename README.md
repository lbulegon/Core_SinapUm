# Core_SinapUm — Cognitive Operations Framework

O **Core_SinapUm** é o framework cognitivo interno do monólito Django: arquitetura modular para **interpretar o ambiente**, **decidir (PAOR)**, **executar comandos** de forma desacoplada e **governar** o sistema pelo **EOC** (Centro de Operações Cognitivas), com **auditoria** obrigatória.

Este documento é a referência técnica oficial para desenvolvimento, onboarding e revisão de código.

---

## Objetivo

Disponibilizar um *runtime* cognitivo que:

| Capacidade | Onde vive |
|------------|-----------|
| Perceber o ambiente (indícios) | `agent_core` — perceptors / módulos |
| Interpretar sinais (contexto semântico) | `agent_core` — analyzers |
| Orquestrar decisões | `agent_core` — orchestrators |
| Responder com ações estruturadas | `agent_core` — responders |
| Enfileirar e executar comandos | `command_engine` + `services` |
| Controlar e monitorar | EOC (`app_sinapcore` + URLs) |

---

## Arquitetura (visão de pastas)

```
Core_SinapUm/
├── agent_core/           # Runtime cognitivo (PAOR) — sem Django nos núcleos puros
│   ├── core/             # Motor, interfaces, agent
│   ├── modules/          # Módulos orbitais (ex.: environmental/)
│   ├── perceptors/       # Compat / wrappers
│   └── registry/         # Registro de módulos plugáveis
├── command_engine/       # Handlers + registry + executor (fachada)
├── services/             # Infraestrutura Django (Redis, fila, logs ORM, alertas)
├── models/               # Reexport dos modelos de governança (ver abaixo)
├── views/                # Documentação do boundary HTTP (implementação em app_sinapcore)
├── utils/                # Utilitários (ex.: validação do framework)
├── app_sinapcore/        # App Django: modelos ORM, EOC, templates, admin
└── setup/                # Projeto Django (settings, urls)
```

**Nota:** os modelos Django (`SinapCoreModule`, `SinapCoreCommand`, `SinapCoreLog`) estão definidos em `app_sinapcore/models/`. O pacote `models/` na raiz reexporta-os para alinhar com a documentação do framework e facilitar imports consistentes.

---

## Camadas do sistema

### 1. Agent Core (PAOR)

Fluxo conceitual: **Perceive → Analyze → Orchestrate → Respond**.

- **Regra:** o núcleo cognitivo **não importa Django**; trabalha com `dict` de contexto.
- **Extensão:** novos comportamentos entram como módulos em `agent_core/modules/<domínio>/` e registro no bootstrap/registry.

### 2. Command Engine

- **Registry** de handlers por `command_name`.
- **Executor** (`command_engine/executor.py`): fachada que delega a `services.command_execution_runtime` (ORM, transações, auditoria).
- **Sem** ramificações `if comando == ...` no fluxo principal: o despacho é pelo registry.

### 3. Handlers (plugáveis)

Cada comando operacional é uma classe:

```python
from command_engine.base import BaseCommandHandler


class PauseOrdersHandler(BaseCommandHandler):
    command_name = "pause_orders"

    def execute(self, command, context):
        ...
```

Características: plugável, testável, registado no `bootstrap` da app.

### 4. Services (infraestrutura)

Ponto de integração com **Django**, **Redis**, **ORM**, **alertas**, **modo de sistema**. Exemplos: `environmental_state_service`, `command_executor`, `system_mode_service`, `alert_service`, `decision_audit`.

### 5. Models (governança)

| Modelo | Função |
|--------|--------|
| `SinapCoreModule` | Ativação / prioridade / config dos módulos |
| `SinapCoreCommand` | Fila de comandos |
| `SinapCoreLog` | Auditoria (decisões, comandos, falhas, contexto) |
| `ArchitectureScore` | Histórico de scores do validador arquitetural (`validate_framework.py`) |

### 6. EOC (Centro de Comando)

Interface para monitoramento, execução manual de comandos e visão global. Implementação: vistas e templates em `app_sinapcore` (ex.: `eoc_views`, URLs sob `/sinapcore/`).

---

## System mode

Modos típicos: **NORMAL**, **PRESSURE**, **CRITICAL** (derivados do contexto ambiental e decisões PAOR). Impactam planejamento, limites de ação e comportamento global — **sem** atalhos hardcoded em views; preferir decisões nos módulos e execução via comandos.

---

## Alertas

Baseados em, entre outros:

- estado ambiental (serviços + Redis onde aplicável);
- padrões em logs recentes;
- recorrência de falhas.

---

## Logging e auditoria

Registar sempre que possível:

- decisões e respostas por módulo;
- comandos enfileirados e resultado da execução;
- falhas e *stack* resumido;
- *snapshot* de contexto relevante (sem dados sensíveis).

---

## Extensibilidade (checklist de implementação)

1. Criar módulo PAOR em `agent_core/modules/<nome>/` (perceptor, analyzer, orchestrator, responder).
2. Registar o módulo no bootstrap/registry.
3. Criar handlers em `command_engine/handlers/<domínio>/` e registar em `command_engine/bootstrap.py`.
4. (Opcional) Ativar módulo e prioridade via Admin (`SinapCoreModule`).

---

## Anti-patterns vs padrões

**Evitar:** decisão de negócio na view ou `if estado == "colapso": pause_orders()` acoplado.

**Preferir:** emissão de comando nomeado (`pause_orders`) para a fila, execução pelo handler registado e auditoria em `SinapCoreLog`.

---

## Base conceitual (referências)

- **Semiótica** — Charles Sanders Peirce (interpretação de signos).
- **Método indiciário** — Carlo Ginzburg (rastreio de indícios).
- **Comportamento emergente** — Kevin Kelly (*Out of Control*).

---

## SinapLint (governança arquitetural)

**SinapLint** é o motor de lint cognitivo/arquitetural do Core_SinapUm: valida estrutura, módulos PAOR, padrões (regex) e **AST**, calcula **score** e pode sugerir melhorias.

```
sinaplint/
├── engine.py           # Orquestração e scoring
├── path_utils.py       # Exclusões de caminhos
├── rules/
│   ├── structure_rules.py
│   ├── pattern_rules.py
│   ├── module_rules.py
│   └── ast_rules.py
├── reporters/
│   ├── console.py
│   └── json.py
└── scorers/
    └── module_score.py
```

### O que avalia

| Regra | Conteúdo |
|--------|-----------|
| Estrutura | `REQUIRED_DIRS` / `REQUIRED_FILES` |
| Módulos | `agent_core/modules/<nome>/` com PAOR (`perceptor`, `analyzer`, `orchestrator`, `responder`) |
| Padrões | Regex (ex.: `pause_orders(` fora de handlers) + sugestões estáticas |
| AST | Chamadas `pause_orders`, condições `env_state` (heurística) |

Penalizações em `sinaplint/engine.py` (`PENALTIES`). Limiar: `MIN_PASS_SCORE` (80).

### Níveis de qualidade (score)

| Intervalo | Rótulo     | Uso típico        |
|-----------|------------|-------------------|
| 90–100    | EXCELENTE  | Alvo de equipe    |
| 80–89     | ACEITÁVEL  | Mínimo para merge |
| &lt; 80   | BLOQUEADO  | CI falha          |

### Comandos (CLI)

**Onde executar:** na raiz do projeto Django, pasta **`Core_SinapUm`** (onde está `sinaplint.py` e `manage.py`).

```bash
cd Core_SinapUm
```

#### Formas de invocação (equivalentes)

| Forma | Descrição |
|-------|-----------|
| `python sinaplint.py check` | Script na raiz de `Core_SinapUm` (recomendado para scripts e CI). |
| `python -m sinaplint check` | Executa o pacote como módulo (útil com `PYTHONPATH` já configurado). |

#### Opções do subcomando `check`

| Opção | Efeito |
|-------|--------|
| `--json` | Imprime **só** o relatório completo em JSON no *stdout* (sem relatório humano). |
| `-o caminho.json` / `--output` | Grava o mesmo JSON no arquivo indicado. Com `--json`, o JSON vai para o arquivo e a mensagem de confirmação para *stderr*; **sem** `--json`, mostra o relatório humano no *stdout* **e** grava o JSON no arquivo (mensagem no *stderr*). |
| `--fail-under N` | Termina com código **1** se `score < N` (por defeito **80**). Útil para CI com limiar mais alto (ex.: `85`). |
| `--root /caminho` | Usa outra pasta como raiz do Core_SinapUm em vez da pasta do pacote `sinaplint`. |
| `--color` / `--no-color` | Forçar ou desativar cores no terminal (usa [colorama](https://pypi.org/project/colorama/) se instalado; respeita `NO_COLOR`). |

#### Exemplos

```bash
cd Core_SinapUm

# Relatório legível no terminal (score, estrutura, padrões, AST, sugestões, módulos)
python sinaplint.py check
python -m sinaplint check

# Só JSON no stdout (para pipes e automação)
python sinaplint.py check --json

# Guardar JSON e ver relatório humano no terminal
python sinaplint.py check -o sinaplint_report.json

# JSON no stdout e cópia em arquivo
python sinaplint.py check --json -o sinaplint_report.json

# Falhar o processo se o score for inferior a 85
python sinaplint.py check --fail-under 85

# Cores ANSI no terminal (útil com colorama instalado: pip install colorama)
python sinaplint.py check --color
```

**Interpretador (`python` vs `python3`):** em muitos ambientes Linux o binário correcto é `python3`. Confirma com `python --version`; se não for Python 3, substitui `python` por `python3` em todos os exemplos acima.

**Códigos de saída:** `0` = dentro do limiar; `1` = score abaixo de `--fail-under`; `2` = erro (ex.: `--root` inválido).

#### O que esperar na saída

| Comando | Comportamento |
|---------|----------------|
| `check` (sem flags) | Relatório humano no *stdout*: título **SinapLint Report**, linha de **Score** `…/100` com qualidade (EXCELENTE / ACEITÁVEL / BLOQUEADO), secções de estrutura, padrões/AST (se houver), sugestões, módulos orbitais, linha separadora final. |
| `check --json` | Apenas JSON completo no *stdout* (adequado para pipes e automação). |
| `check -o arquivo.json` | Relatório humano no *stdout* **e** gravação do JSON no arquivo; mensagem de confirmação no *stderr*. |
| `check --json -o arquivo.json` | JSON no *stdout* **e** cópia no arquivo; confirmação no *stderr*. |
| `check --fail-under N` | Mesmo relatório; processo termina com **1** se `score < N`. |
| `check --color` | Igual ao relatório humano, com sequências de cor (ANSI) nos títulos e score, desde que [colorama](https://pypi.org/project/colorama/) esteja instalado. |

#### Verificação rápida (checklist local)

Após `cd Core_SinapUm`, estes comandos devem completar com exit **0** quando o projeto está conforme (score ≥ limiar):

```bash
python3 sinaplint.py check
python3 -m sinaplint check
python3 sinaplint.py check --json
python3 sinaplint.py check -o sinaplint_report.json   # cria o JSON; mensagem no stderr
python3 sinaplint.py check --fail-under 85
python3 sinaplint.py check --color
```

Se o seu sistema já usa `python` como Python 3, pode trocar `python3` por `python`.

#### `sinaplint fix` (auto-correção)

Aplica correções **conservadoras** apenas nos mesmos caminhos que o `check` (regex / AST), com comentários `# sinaplint-autofix: …` para rever manualmente:

- comentar chamadas diretas a `pause_orders(` (fora de handlers);
- comentar condições `if env_state` (heurística).

**Não** altera `sinaplint/`, `migrations`, `command_engine/handlers/`, nem árvores grandes em `services/`.

```bash
python3 sinaplint.py fix              # grava alterações
python3 sinaplint.py fix --dry-run    # só lista o que alteraria
```

Depois de `fix`, corre `sinaplint check` e revê o diff (`git diff`).

#### `pre-commit` (bloqueio no commit)

Na **raiz do repositório Git** existe `.pre-commit-config.yaml` (monólito em `Core_SinapUm/`). Se a raiz do seu Git for **só** a pasta `Core_SinapUm`, use o arquivo de exemplo `Core_SinapUm/.pre-commit-config.example.yaml` (copia para `.pre-commit-config.yaml` e ajusta `entry`).

```bash
pip install pre-commit
cd /caminho/para/raiz-do-git
pre-commit install
```

Em cada `git commit`, corre o hook **SinapLint Check** (`python3 Core_SinapUm/sinaplint.py check`). Se o score ficar abaixo do limiar por defeito (80), o commit falha.

Opcionalmente pode descomentar o hook **SinapLint Fix** no YAML para rodar `fix` antes do `check` (rever sempre o diff).

#### Outras entradas

| Comando | Nota |
|---------|------|
| `python run_sinaplint.py` | Compatível com o fluxo antigo: equivale a `sinaplint check` (insere o subcomando `check` se faltar). |
| `python utils/framework_validator.py` | Relatório detalhado no mesmo motor SinapLint (útil para scripts legados). |
| `python validate_framework.py` | SinapLint + tentativa de persistir **`ArchitectureScore`** na BD (Django). |

#### Instalação global (opcional)

```bash
cd Core_SinapUm
chmod +x sinaplint.py
ln -sf "$(pwd)/sinaplint.py" /usr/local/bin/sinaplint   # ou outro diretório no PATH
sinaplint check
```

**Django shell:**

```python
from sinaplint.engine import SinapLint, MIN_PASS_SCORE
from pathlib import Path
r = SinapLint(Path(".")).run()
assert r["score"] >= MIN_PASS_SCORE
```

**CI (GitHub Actions):** `.github/workflows/ci.yml` — `pip install -r Core_SinapUm/requirements.txt` e `python Core_SinapUm/sinaplint.py check` (falha o job se o score ficar abaixo do limiar por defeito, 80).

**Persistência:** `validate_framework.py` grava **`ArchitectureScore`** com `details.sinaplint` (payload completo). O **EOC** mostra o último score persistido.

**Admin:** *Scores arquiteturais*.

---

## SinapLint Cloud (API multi-tenant)

Modelos em `app_sinapcore.models.sinaplint_cloud`: `SinapLintTenant` (API key), `SinapLintProject`, `SinapLintAnalysis` (histórico JSON do relatório).

| Método | Caminho | Autenticação |
|--------|---------|--------------|
| `POST` | `/api/sinaplint/v1/analyze/` | Header `X-API-KEY` = chave do tenant (Admin Django) |

Corpo JSON: por exemplo `{"project_id": 1}`. O servidor executa `SinapLint` sobre o código em disco (`settings.BASE_DIR`, pasta **Core_SinapUm**). Cria um registro em `SinapLintAnalysis` com `score` e `result` completos.

**Exemplo (curl):**

```bash
curl -s -X POST "https://seu-dominio/api/sinaplint/v1/analyze/" \
  -H "X-API-KEY: sl_..." \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1}'
```

Após migrações (`manage.py migrate`), crie tenant e projeto no Admin. Em produção: HTTPS, rate limiting e rotação de chaves.

---

## Aprendizado e simulação (serviços)

| Serviço | Ficheiro | Função |
|---------|----------|--------|
| `LearningService` | `services/learning_service.py` | Agrega `SinapCoreLog` por `decision` (contagem, `success_rate`). |
| `SimulationService` | `services/simulation_service.py` | Estima score após remoção hipotética de *issues* (heurística). |

O motor SinapLint inclui **`ai_refactor`**: sugestões heurísticas por issue (`sinaplint/ai_refactor.py`), incluídas no JSON do `check`.

---

## Extensão VS Code (`tools/sinaplint-vscode`)

Pacote mínimo: ao guardar `.py`, corre `python3 sinaplint.py check` na pasta Core_SinapUm configurada (`sinaplint.coreRoot`). Comando **SinapLint: executar check**. Ver `tools/sinaplint-vscode/package.json`.

---

## Roadmap (produto)

- Modo semi-autónomo com aprovação humana.
- Métricas de eficácia por comando.
- IA preditiva apoiada em histórico de logs.
- Simulação de decisões (*dry-run*).

---

## Documentação adicional

- Índice geral em [`docs/README.md`](docs/README.md) (quando existir conteúdo agregado).
- READMEs por app ou serviço nas respectivas pastas (WhatsApp, leads, etc.).

---

## Definição

**Core_SinapUm** é o framework interno que torna o sistema **modular**, **auditável** e **governável**: interpreta o ambiente, decide via PAOR, executa através da camada de comandos e permanece controlável pelo EOC.
