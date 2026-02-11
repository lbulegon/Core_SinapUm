# Regras Gerais — Ecossistema de Prompts

## Propósito

Estabelecer as regras universais aplicáveis a todos os prompts do Core_SinapUm e VitrineZap. Garantir consistência, previsibilidade e governabilidade.

## Escopo

- Prompts de análise, curadoria e decisão
- Prompts de domínio (SKM, Shopper, Keeper)
- Novos prompts criados sob esta governança

## Estrutura mínima obrigatória de um prompt

Todo prompt deve conter:

1. **Título** — Nome claro e único
2. **Propósito** — O que o prompt existe para fazer
3. **Escopo** — Limites do domínio de atuação
4. **O que PODE fazer** — Lista explícita de capacidades
5. **O que NÃO pode fazer** — Lista explícita de restrições
6. **Tipo** — Análise, Curadoria ou Decisão
7. **Versão** — Identificador (ex.: v1.0)

## Contrato de entrada e saída

| Elemento | Exigência |
|----------|-----------|
| **Entrada** | Contexto, dados ou perguntas explícitas; sem suposições implícitas |
| **Saída** | Formato declarado (texto, lista, critérios, trade-offs); sem execução autônoma |
| **Incerteza** | Deve ser declarada quando o prompt não tiver informações suficientes |
| **Validação** | Decisões exigem confirmação humana antes de ação |

## Limites éticos e operacionais

1. **Neutralidade** — Prompts não defendem posições; analisam, organizam ou apresentam alternativas
2. **Transparência** — Hipóteses e suposições devem ser declaradas
3. **Não-substituição** — Humanos mantêm controle sobre decisões finais
4. **Sem promessas prematuras** — Nenhum prompt promete resultados financeiros ou crédito
5. **Preservação relacional** — Prompts não incentivam comportamento que destrói confiança

## Separação entre análise, decisão e execução

| Camada | Função | Quem age |
|--------|--------|----------|
| **Análise** | Avaliar, mapear, explicar | Prompt + humano interpreta |
| **Decisão** | Apresentar trade-offs, critérios, alternativas | Humano decide |
| **Execução** | Implementar, codificar, operar | Código/sistema (fora do escopo dos prompts) |

Prompts não executam código. Prompts não implementam features. Prompts não alteram sistemas.

## Versionamento de prompts

- Formato: `v<major>.<minor>` (ex.: v1.0, v1.1)
- **Major** — Mudança de propósito ou escopo
- **Minor** — Refinamento de linguagem ou critérios sem mudança de propósito
- Histórico deve ser preservado em comentário ou documento anexo

## Prompts como ativos estratégicos

- Prompts são tratados como patrimônio cognitivo
- Alterações devem ser rastreáveis
- Redundância e contradição devem ser evitadas
- Clareza e simplicidade são preferíveis a sofisticação ambígua



Este documento deriva diretamente do Prompt dos Prompts v1.0
e não pode contradizê-lo.
