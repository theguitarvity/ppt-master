# CLI Contract: Gerar Deck FACOM/UFMS Animado a partir de CONTEXT.md

Este projeto é um pacote de skill/workflow (não um serviço), então sua "interface externa" é a
superfície de linha de comando dos scripts em `skills/ppt-master/scripts/`. Este contrato
documenta apenas os comandos **novos** introduzidos por esta feature; nenhum comando existente
muda de assinatura (FR-014).

## `context_intake.py` (novo)

```bash
python3 ${SKILL_DIR}/scripts/context_intake.py <CONTEXT.md> --project-dir <project_path> [--validate-only]
```

| Flag | Obrigatório | Efeito |
| --- | --- | --- |
| `<CONTEXT.md>` | sim | caminho do arquivo de entrada |
| `--project-dir` | sim | diretório do projeto PPT Master (criado via `project_manager.py init` se ausente) |
| `--validate-only` | não | valida e normaliza sem inicializar/importar; usado por `conformance_report.py` |

**Exit codes**: `0` sucesso (com ou sem avisos) · `1` erro de validação de schema (campo
obrigatório ausente ou tipo incorreto, FR-002) · `2` `brand.profile` referenciado não existe em
`brands_index.json`.

**Efeitos colaterais em sucesso** (sem `--validate-only`): grava
`<project_path>/analysis/context_brief.json`; chama `project_manager.py init` e
`import-sources` internamente quando o projeto ainda não existe.

## `brand_lint.py` (novo)

```bash
python3 ${SKILL_DIR}/scripts/brand_lint.py <project_path> --brand-profile facom-ufms
```

**Exit codes**: `0` sem violações · `1` uma ou mais violações conhecidas de marca (cor,
proporção do logo, variante incompatível com o fundo — FR-011).

## `contact_sheet.py` (novo)

```bash
python3 ${SKILL_DIR}/scripts/contact_sheet.py <project_path>
```

Pré-requisito: `visual_review.py` já executado (lê `<project_path>/.preview/*.png`). Escreve
`<project_path>/validation/contact_sheet.png`. **Exit codes**: `0` sucesso · `4` PNGs de
página ausentes (propaga o mesmo código de `visual_review.py` para "falha de renderização de
página").

## `conformance_report.py` (novo)

```bash
python3 ${SKILL_DIR}/scripts/conformance_report.py <project_path> --host codex
```

Orquestra, nesta ordem, os gates que ainda não bloqueiam `svg_to_pptx.py`:
`context_intake.py --validate-only` → `svg_quality_checker.py` → `visual_review.py` +
`contact_sheet.py` → `brand_lint.py`. Escreve
`<project_path>/validation/conformance_report.json` (schema em [data-model.md](../data-model.md)
§6). Se qualquer gate falhar **ou** for marcado `skipped` por ausência de capacidade do host
(`browser: optional` ausente → pula `visual_review.py`/`contact_sheet.py`), **retorna código
de saída não-zero e não invoca `svg_to_pptx.py`** — `skipped` bloqueia a exportação com o mesmo
efeito de `fail`, apenas com `detail` distinto nomeando a capacidade ausente em vez de uma
violação real; implementa o gate rígido decidido na clarificação de 2026-07-27 (FR-019). Em
sucesso (todos os gates `pass`), invoca `svg_to_pptx.py` (Step 7.3 já existente) e inclui seu
`validation/*.report.json` no relatório consolidado.

**Exit codes**: `0` todos os gates + exportação passaram · `10` um ou mais gates pré-exportação
falharam (nenhum PPTX gravado) · `11` `svg_to_pptx.py` falhou após todos os gates pré-exportação
passarem (comportamento herdado, inalterado).

## `capabilities.json` por host (dado, não CLI)

Não é um comando; é lido por `conformance_report.py --host <id>` e por
`context_intake.py` para decidir fallbacks (ex.: `browser: optional` ausente → pular
`visual_review.py`/`contact_sheet.py` e declarar a limitação explicitamente no
`conformance_report.json`, nunca simular sucesso — FR-015). Schema:
[host-capabilities.schema.json](./host-capabilities.schema.json).
