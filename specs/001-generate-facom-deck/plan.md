# Implementation Plan: Gerar Deck FACOM/UFMS Animado a partir de CONTEXT.md

**Branch**: `001-generate-facom-deck` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-generate-facom-deck/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Uma pessoa fornece um único `CONTEXT.md` (frontmatter YAML + corpo Markdown); um novo passo de
intake (`context_intake.py`) valida, normaliza e encaminha esse conteúdo para o pipeline
Generate PPTX **já existente** (`generate-pptx.md` Steps 1–7), sem alterá-lo. Quando
`brand.profile: facom-ufms` está declarado, o Strategist aplica um novo Pacote de Marca e Deck
FACOM/UFMS adicionados ao catálogo `templates/brands/` / `templates/decks/` já existente. Uma
nova camada fina de orquestração (`conformance_report.py`) roda os gates de qualidade — schema,
SVG, render completo + contact sheet, brand lint — **antes** de invocar o exportador nativo já
existente (`svg_to_pptx.py`); se qualquer gate falhar, nenhum PPTX é gravado (gate rígido,
decidido na clarificação de 2026-07-27). O primeiro host é Codex, declarado via um novo
contrato de capacidades de host (`host-capabilities.schema.json` + `adapters/codex/`); GitHub
Copilot recebe apenas a mesma declaração de interface, sem adapter funcional; Claude Code
permanece funcional sem nenhuma mudança. Toda a capacidade nova é aditiva dentro da árvore
`skills/ppt-master/` já existente — nenhum script, workflow ou rota do motor atual é
reescrito (Constituição Princípio I, III, IV; FR-014).

## Technical Context

**Language/Version**: Python 3 (mesmo interpretador de `skills/ppt-master/scripts/`; nenhuma
versão mínima nova é fixada — o repositório não fixa uma hoje). Ver [research.md](./research.md) §1.

**Primary Dependencies**: nenhuma dependência Python nova e obrigatória. Reaproveita
`PyYAML` (já opcional, com fallback existente), `Pillow` (já dependência, usado pelo novo
`contact_sheet.py`), `python-pptx` (via `svg_to_pptx.py`, inalterado), e o backend
Playwright/Chromium já usado por `visual_review.py`. Ver [research.md](./research.md) §1, §6.

**Storage**: arquivos versionados dentro do projeto/skill — `analysis/context_brief.json`,
`validation/conformance_report.json`, `templates/brands/facom-ufms/`,
`templates/decks/facom-ufms-talk/`, `adapters/<host>/capabilities.json`. Sem banco de dados
ou serviço externo persistente.

**Testing**: sem suíte de testes automatizados formal no repositório hoje (o projeto valida via
scripts determinísticos — `svg_quality_checker.py`, `batch_validate.py`, `project_manager.py
validate` — e fixtures de smoke test, não `pytest`). Esta feature segue o mesmo padrão: adiciona
`conformance_report.py` como validação executável e uma fixture de smoke test
(`conformance/fixtures/facom-talk/`) em vez de introduzir um framework de testes novo — AGENTS.md
já proíbe assumir convenções genéricas como `tests/` obrigatório para este repositório.

**Target Platform**: CLI/skill local, invocada por um agente de IA dentro de um host de chat
(Codex nesta slice); macOS/Linux/Windows conforme os scripts Python já suportados.

**Project Type**: pacote de workflow/skill (não app, não serviço) — Compatibility Boundary do
AGENTS.md.

**Performance Goals**: sem meta de latência formal nesta slice (Assumption do spec.md); o
critério de sucesso é conclusão correta e sem intervenção manual (SC-001), não velocidade.

**Constraints**: FR-014 (nenhuma reescrita do motor existente); FR-019 (gate rígido — nenhum
PPTX gravado enquanto um gate falhar); offline-capable para geração em si, uma vez que os
assets de marca já estejam baixados localmente (Assumption do spec.md).

**Scale/Scope**: um único operador (o mantenedor) gerando um deck por vez; um host funcional
(Codex) + um host preservado (Claude Code) + uma interface apenas declarada (GitHub Copilot).
Sem requisito de concorrência/múltiplos usuários simultâneos nesta slice.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Princípio | Como esta feature cumpre | Status |
| --- | --- | --- | --- |
| I | Núcleo único, adapters finos | Todo código novo entra em `skills/ppt-master/scripts/` e `templates/`, compartilhado por todos os hosts; `adapters/<host>/capabilities.json` é dado declarativo, não lógica de domínio | PASS |
| II | Artefatos e contratos determinísticos acima do modelo | `context.schema.json`, `host-capabilities.schema.json`, `context_brief.json` e `conformance_report.json` são os contratos; roteamento/validação/export permanecem determinísticos, só a composição de `animations.json` permanece criativa (já era) | PASS |
| III | Preservação das quatro rotas | `CONTEXT.md` só alimenta a rota Generate PPTX já existente como novo Step 1; nenhuma quinta rota é criada; FR-004 | PASS |
| IV | SVG canônico restrito como IR | Inalterado — `context_intake.py` só produz `analysis/context_brief.json`, nunca toca `svg_output/` diretamente | PASS |
| V | Fidelidade/editabilidade/validação antes de velocidade | FR-019 (gate rígido) é exatamente esta cláusula aplicada à exportação | PASS |
| VI | Marca como política verificável | `brand-policy.yaml` + `provenance.json` + `brand_lint.py` novo — nunca texto solto em prompt | PASS |
| VII | Degradação explícita por capacidade | `host-capabilities.schema.json` + `capabilities.json` por host; fallback declarado quando `browser` está ausente (pula render, nunca simula sucesso) | PASS |
| VIII | Proveniência de fontes e assets | `provenance.json` do Pacote de Marca; reaproveita o padrão já existente de `*.facts.json`/`image_sources.json` | PASS |
| IX | Paridade sem identidade byte a byte | Fora do escopo de implementação desta slice além de preservar Claude funcional; nenhuma alegação de paridade Codex/Copilot é feita aqui | PASS (escopo reduzido, não violação) |
| X | Entrega incremental ancorada na palestra real | `conformance/fixtures/facom-talk/CONTEXT.md` é a fixture de aceitação viva (FR-017, SC-005) | PASS |
| Quality Gates | 7 gates obrigatórios | Todos mapeados: schema→`context_intake.py`; SVG→`svg_quality_checker.py` (existente); render→`visual_review.py`+`contact_sheet.py`; OOXML→`svg_to_pptx.py` postflight (existente); overflow→já coberto por `svg_quality_checker.py`; brand lint→`brand_lint.py` novo; documentação→`quickstart.md` | PASS |
| Fronteiras não negociáveis | 8 itens | Nenhum item violado — sem SaaS, sem SVG arbitrário, sem refill cego, sem gráfico nativo por padrão, sem reescrita do motor, Executor não repesquisa material do Strategist, sem terceira cópia da skill | PASS |

**Resultado**: nenhuma violação. [Complexity Tracking](#complexity-tracking) permanece vazio.

## Project Structure

### Documentation (this feature)

```text
specs/001-generate-facom-deck/
├── plan.md                          # This file
├── research.md                      # Phase 0 output
├── data-model.md                    # Phase 1 output
├── quickstart.md                    # Phase 1 output
├── contracts/
│   ├── context.schema.json
│   ├── host-capabilities.schema.json
│   └── cli-contract.md
├── checklists/requirements.md       # /speckit-specify output, re-validated by /speckit-clarify
└── tasks.md                         # Phase 2 output (/speckit-tasks command — NOT created by /speckit-plan)
```

### Source Code (repository root)

Nenhuma opção de template genérico (single project / web app / mobile) se aplica — este é um
pacote de skill existente. A estrutura abaixo é a árvore real de `skills/ppt-master/`, com as
adições desta feature marcadas `# NOVO`.

```text
skills/ppt-master/
├── scripts/
│   ├── context_intake.py            # NOVO — valida/normaliza CONTEXT.md, chama project_manager.py
│   ├── brand_lint.py                # NOVO — checa brand-policy.yaml contra svg_output/
│   ├── contact_sheet.py             # NOVO — compõe .preview/*.png em um grid único
│   ├── conformance_report.py        # NOVO — orquestra os gates + gate rígido (FR-019)
│   ├── project_manager.py           # inalterado — chamado por context_intake.py
│   ├── svg_quality_checker.py       # inalterado — reaproveitado
│   ├── visual_review.py             # inalterado — reaproveitado
│   └── svg_to_pptx.py               # inalterado — chamado por conformance_report.py em sucesso
├── templates/
│   ├── schemas/
│   │   ├── context.schema.json              # NOVO
│   │   ├── host-capabilities.schema.json    # NOVO
│   │   ├── design_spec.schema.json          # inalterado
│   │   └── spec_lock.schema.json            # inalterado
│   ├── brands/
│   │   ├── facom-ufms/                      # NOVO — images/, templates/design_spec.md,
│   │   │                                    #        brand-policy.yaml, provenance.json
│   │   └── brands_index.json                # +1 entrada
│   └── decks/
│       ├── facom-ufms-talk/                 # NOVO
│       └── decks_index.json                 # +1 entrada
├── adapters/                                # NOVO diretório
│   ├── codex/capabilities.json              # NOVO — funcional
│   └── github-copilot/capabilities.json     # NOVO — interface apenas (FR-018)
└── references/
    └── animation-presets.md                 # NOVO — mapeamento delivery.animations → autoria

conformance/                                 # NOVO diretório, isolado (research.md §11)
└── fixtures/facom-talk/CONTEXT.md           # NOVO — fixture de aceitação viva (FR-017)
```

**Structure Decision**: manter 100% a árvore `skills/ppt-master/` já existente (AGENTS.md
Compatibility Boundary + FR-014); toda capacidade nova entra como arquivos adicionais nos
diretórios `scripts/`, `templates/schemas/`, `templates/brands/`, `templates/decks/`, mais dois
diretórios novos e isolados — `skills/ppt-master/adapters/` (contrato de capacidade por host,
Épico 2) e `conformance/` na raiz do repositório (fixtures de aceitação, Épico 0/7). A árvore
aspiracional `packages/{core,brands,adapters}/` do CONTEXT.md §7 **não** é adotada nesta slice
— ver Faseamento abaixo.

## Faseamento: P0 (Hoje) vs. Evolução Multimodelo Posterior

| Área | P0 — obrigatório nesta slice | Evolução multimodelo — explicitamente adiado |
| --- | --- | --- |
| **Parser CONTEXT.md** | `context.schema.json` + `context_intake.py` completos e ligados ao Step 1/4 existente | Suporte a múltiplos formatos de tela além de `ppt169` (Assumption do spec) |
| **Brand/Deck FACOM** | `templates/brands/facom-ufms/` + `templates/decks/facom-ufms-talk/` com assets oficiais, `brand-policy.yaml`, `provenance.json`, registrados nos índices existentes | Matriz extensa de Decks FACOM (aula, defesa, relatório — CONTEXT.md §8.2); regras completas de co-branding com marcas externas |
| **Adapter Codex** | `adapters/codex/capabilities.json` funcional; `quickstart.md` único caminho feliz Codex | `adapters/claude-code/capabilities.json` formalizado; adapter GitHub Copilot **funcional** (FR-018 — só interface nesta slice); reestruturação para `packages/adapters/` |
| **Animações** | `animation-presets.md` mapeando `none/subtle/purposeful/narrative`; validação via `animation_config.py` já existente | Áudio/vídeo como caminho padrão (Assumption do spec, CONTEXT.md §8.2) |
| **QA** | `brand_lint.py`, `contact_sheet.py`, `conformance_report.py` com gate rígido (FR-019) | Golden tests visuais multi-renderizador; execução paralela de revisão visual em todos os hosts; CI dedicado |
| **Palestra real como fixture** | `conformance/fixtures/facom-talk/CONTEXT.md` com o conteúdo real do mantenedor (FR-017, SC-005) | Paridade de resultados testada entre Codex/Copilot/Claude sobre a mesma fixture (Princípio IX) |

Nenhum item da coluna direita é necessário para o Definition of Done desta slice (CONTEXT.md
§18); eles ficam registrados aqui para que uma feature futura os retome sem precisar
redescobrir o escopo.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Vazio — nenhuma violação da Constituição foi identificada nesta slice (ver Constitution Check
acima).
