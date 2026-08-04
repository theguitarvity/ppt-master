---

description: "Task list for Gerar Deck FACOM/UFMS Animado a partir de CONTEXT.md"
---

# Tasks: Gerar Deck FACOM/UFMS Animado a partir de CONTEXT.md

**Input**: Design documents from `/specs/001-generate-facom-deck/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md),
[data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: Não solicitados explicitamente no spec.md como suíte automatizada formal (o projeto
valida via scripts determinísticos + fixtures — ver Technical Context em plan.md). As tarefas
de US2/US3 abaixo já incluem cenários de verificação executáveis contra fixtures reais, em vez
de uma fase de testes separada.

**Organization**: Tarefas agrupadas por user story para permitir implementação e teste
independentes de cada uma.

**P0 explícito (pedido do usuário)**: as Phases 1–3 abaixo (Setup + Foundational + User Story
1) formam, juntas, a vertical slice executável priorizada — parser de `CONTEXT.md`, assets
oficiais FACOM/UFMS, Brand/Deck FACOM, geração pelo Codex, animações `purposeful`, exportação,
renderização e QA do deck real. Nenhuma tarefa de Setup/Foundational/US1 depende de US2 ou US3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Pacote de skill existente, não app genérico — todos os caminhos são relativos à raiz do
repositório, dentro da árvore já existente `skills/ppt-master/` (ver plan.md § Project
Structure), mais dois diretórios novos e isolados: `skills/ppt-master/adapters/` e
`conformance/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: criar os diretórios e schemas novos que toda tarefa subsequente referencia.

- [X] T001 Create `skills/ppt-master/adapters/codex/` and `skills/ppt-master/adapters/github-copilot/` directories
- [X] T002 [P] Create `conformance/fixtures/facom-talk/` directory in the repository root
- [X] T003 [P] Copy [contracts/context.schema.json](./contracts/context.schema.json) to `skills/ppt-master/templates/schemas/context.schema.json`
- [X] T004 [P] Copy [contracts/host-capabilities.schema.json](./contracts/host-capabilities.schema.json) to `skills/ppt-master/templates/schemas/host-capabilities.schema.json`

**Checkpoint**: diretórios e schemas existem; nenhum código ainda depende deles.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: infraestrutura compartilhada por US1, US2 e US3 — o parser de `CONTEXT.md`, o
Pacote de Marca/Deck FACOM/UFMS, o mapeamento de presets de animação e a declaração de
capacidades do Codex.

**⚠️ CRITICAL**: nenhuma user story pode começar antes desta fase estar completa.

- [X] T005 [P] Download and version official FACOM/UFMS brand assets (grafo_facom.png / UFMS logo — positive and negative variants) from the URLs in CONTEXT.md §4.1 into `skills/ppt-master/templates/brands/facom-ufms/images/`
- [X] T006 [P] Write `skills/ppt-master/templates/brands/facom-ufms/provenance.json` recording `source_url` / `captured_at` / `usage_condition` for every asset added in T005 (data-model.md §3, FR-013)
- [X] T007 Write `skills/ppt-master/templates/brands/facom-ufms/brand-policy.yaml` with `institutional_color: "#0088B7"`, `mark_variants.positive`/`.negative`, `contrast_threshold_dark_fill_pct: 40`, and `typography.signature`; extract the exact `protection_area_ratio` from the Manual de Identidade Visual UFMS PDF (CONTEXT.md §4.1 URL) — never estimate it — and record its page/section as `protection_area_ratio_source` alongside the value (data-model.md §3, Princípio VIII) (depends on T005)
- [X] T008 [P] Write `skills/ppt-master/templates/brands/facom-ufms/templates/design_spec.md` brand direction, following the format already used by `skills/ppt-master/templates/brands/anthropic/templates/design_spec.md` and `.../google/templates/design_spec.md`
- [X] T009 Register a `"facom-ufms"` entry in `skills/ppt-master/templates/brands/brands_index.json` (depends on T005, T006, T007, T008)
- [X] T010 Create the `skills/ppt-master/templates/decks/facom-ufms-talk/` deck workspace referencing the Brand from T009 without duplicating its tokens (CONTEXT.md §3.6) (depends on T009)
- [X] T011 Register a `"facom-ufms-talk"` entry in `skills/ppt-master/templates/decks/decks_index.json` (depends on T010)
- [X] T012 Implement `skills/ppt-master/scripts/context_intake.py`: parse `CONTEXT.md` frontmatter (PyYAML with the manual-fallback pattern already used in `register_template.py`) + body, validate against `context.schema.json` with a hand-rolled validator matching `project_specs.py::validate_markdown_schema`'s style (no `jsonschema` dependency), write `<project_path>/analysis/context_brief.json` (`resolved`, `defaults_applied`, `warnings`, `schema_version`, `created_at_context_hash` per data-model.md §2), and call `project_manager.py init`/`import-sources` when the project does not yet exist (depends on T003)
- [X] T013 [P] Write `skills/ppt-master/references/animation-presets.md` mapping every `delivery.animations` value (`none`, `subtle`, `purposeful`, `narrative`) to a concrete authoring instruction for `workflows/stages/customize-animations.md`, explicitly defining `narrative` (resolves checklist CHK017)
- [X] T014 Write `skills/ppt-master/adapters/codex/capabilities.json` as a versioned adapter file declaring Codex's real capabilities (`host_id`, `skill_discovery`, `shell`, `filesystem_read`, `filesystem_write`, `browser`, `image_generation`, `parallel_agents`, `interactive_confirmation`, `image_inspection`, `pptx_rendering`), validated against `host-capabilities.schema.json` (depends on T004)

**Checkpoint**: parser, marca, deck e capacidades do host existem e são independentemente
verificáveis — as user stories podem começar.

---

## Phase 3: User Story 1 - Gerar o deck real da palestra a partir de um único CONTEXT.md (Priority: P1) 🎯 MVP / P0

**Goal**: uma pessoa fornece um `CONTEXT.md` válido e obtém um PPTX 16:9 FACOM/UFMS completo,
animado, com notas, gerado no Codex, sem edição manual de scripts.

**Independent Test**: `CONTEXT.md` com `brand.profile: facom-ufms` e
`delivery.animations: purposeful` → caminho feliz do Codex → PPTX 16:9 aberto, três seções
obrigatórias, marca correta, animações validadas.

### Implementation for User Story 1

- [X] T015 [US1] Implement `skills/ppt-master/scripts/brand_lint.py`: (a) pre-flight — verify every asset path named in the active `brand-policy.yaml`/`provenance.json` exists on disk, failing clearly (never substituting) when one is missing (FR-006, Edge Case); (b) read `<project_path>/svg_output/` plus `brand-policy.yaml` and exit non-zero on any known usage violation (institutional color, logo proportion, positive/negative variant vs. background contrast — FR-011) (depends on T007)
- [X] T016 [P] [US1] Implement `skills/ppt-master/scripts/contact_sheet.py`: tile `<project_path>/.preview/*.png` (produced by the existing `visual_review.py`) into a single `<project_path>/validation/contact_sheet.png` grid using `Pillow`, defining the exact grid/thumbnail size (resolves checklist CHK022)
- [X] T017 [US1] Implement `skills/ppt-master/scripts/conformance_report.py`: read `skills/ppt-master/adapters/<host_id>/capabilities.json` first; when `browser` is not `true`, skip `visual_review.py`/`contact_sheet.py` and write an explicit `{name: "render", status: "skipped", detail: "browser capability unavailable on <host_id>"}` gate entry — never a silent omission (FR-015, Constituição Princípio VII); a `skipped` status counts as **not passed** for `overall_status` — identical blocking effect to `fail`, distinguished only by `detail` naming the missing capability rather than a violation (FR-019, data-model.md §6); otherwise orchestrate, in order, `context_intake.py --validate-only` → `svg_quality_checker.py` → `visual_review.py` + `contact_sheet.py` → `brand_lint.py`; on any gate failure or skip, exit non-zero **without invoking `svg_to_pptx.py`** (FR-019 hard gate); on success (all gates `pass`), invoke `svg_to_pptx.py` (existing Step 7.3) and merge its `validation/*.report.json` into `<project_path>/validation/conformance_report.json` per data-model.md §6 (depends on T012, T014, T015, T016)
- [X] T018 [US1] Add `context_intake.py` / `brand_lint.py` / `contact_sheet.py` / `conformance_report.py` entries to the AGENTS.md Command Quick Reference and cross-link [quickstart.md](./quickstart.md) as the single documented Codex happy path (FR-016) (depends on T012, T017)
- [ ] T019 [US1] Populate `conformance/fixtures/facom-talk/CONTEXT.md` with the maintainer's real talk content (`presentation.title`, `.audience`, `.objective`, `.duration_minutes`, `brand.profile: facom-ufms`, `delivery.animations: purposeful`, `delivery.speaker_notes: true`) (depends on T002)
- [ ] T020 [US1] Run the [quickstart.md](./quickstart.md) happy path end-to-end against `conformance/fixtures/facom-talk/CONTEXT.md` on the Codex host, producing `projects/facom-talk-smoke/` with a passing `exports/*.pptx` (depends on T014, T017, T019)
- [ ] T021 [US1] Verify spec.md User Story 1 Acceptance Scenarios 1–5 against the T020 output: three required sections present, speaker notes present, `purposeful` animations pass validation, a `delivery.animations: none` rerun injects zero motion, a deliberately broken copy of the fixture (e.g., forced overflow) proves the hard gate blocks export with zero PPTX written, and `analysis/context_brief.json` plus any `image_sources.json`/`*.facts.json` produced collectively satisfy SC-007 (every external image/claim/asset has origin, capture date, and usage condition recorded) (depends on T020)
- [X] T022 [US1] Run the existing `generate-pptx.md` happy path on the **Claude Code** host against the pre-existing `examples/ppt169_attention_is_all_you_need/` project and confirm it completes with unchanged behavior — the scripts added in this feature must be inert when unused, satisfying the "sem regressão" clause of FR-012 (depends on T012, T015, T016, T017)
- [ ] T023 [US1] Present the T020/T021 PPTX to the mantenedor for an explicit go/no-go review as a real presentation, not just a technically valid file, and record the decision — closes SC-005 (depends on T021)
- [X] T024 [US1] Have a fresh reviewer (a person or an agent session with no prior context on this feature) follow only [quickstart.md](./quickstart.md), with a new `CONTEXT.md`, to reproduce a working FACOM/UFMS deck, confirming zero undocumented steps were needed — closes SC-006 (depends on T018)

**Checkpoint**: User Story 1 é funcional e testável de forma independente — este é o
incremento P0 que o usuário pediu para priorizar.

---

## Phase 4: User Story 2 - Corrigir um CONTEXT.md incompleto ou ambíguo antes de gerar (Priority: P2)

**Goal**: mensagens de erro acionáveis e defaults documentados quando o `CONTEXT.md` está
incompleto ou ambíguo.

**Independent Test**: `CONTEXT.md` com campo obrigatório ausente e campo de tipo incorreto →
mensagens de erro apontam os campos exatos; `CONTEXT.md` mínimo válido → prossegue sem
intervenção, com defaults registrados.

### Implementation for User Story 2

- [ ] T025 [P] [US2] Create three negative `CONTEXT.md` fixtures under `conformance/fixtures/context-validation/` — missing `presentation.title`, wrong type for `presentation.duration_minutes`, and an unknown frontmatter field (depends on T012)
- [ ] T026 [US2] Run `context_intake.py` against each T025 fixture and confirm the error/warning message names the exact offending field and the expected type/value (FR-002, Acceptance Scenario US2.1 and US2.3) (depends on T025)
- [ ] T027 [US2] Run `context_intake.py` against a minimal-but-valid `CONTEXT.md` (title only) and confirm `analysis/context_brief.json`'s `defaults_applied` lists every default used, matching data-model.md §2 (FR-003, Acceptance Scenario US2.2) (depends on T012)
- [ ] T028 [US2] Document the three validation fixtures and their expected outcomes in `conformance/fixtures/context-validation/README.md` (depends on T026, T027)

**Checkpoint**: User Stories 1 e 2 funcionam de forma independente.

---

## Phase 5: User Story 3 - Obter um relatório único de conformidade sobre o deck gerado (Priority: P3)

**Goal**: um relatório único consolidando todos os gates de qualidade, com host e capacidades
declaradas.

**Independent Test**: rodar a suíte de conformidade sobre um deck já gerado pela User Story 1;
o relatório único enumera cada gate.

### Implementation for User Story 3

- [ ] T029 [P] [US3] Extend `conformance_report.py` to also print a human-readable per-gate pass/fail summary to stdout, in addition to writing `validation/conformance_report.json` (depends on T017)
- [ ] T030 [US3] Run `conformance_report.py` against a deck with a deliberately introduced brand violation (e.g., distorted logo proportion) and confirm the report names the specific violation (Acceptance Scenario US3.2) (depends on T017, T029)
- [ ] T031 [US3] Run `conformance_report.py` against the T020 passing deck and confirm the report enumerates all gates with `host_id` and `capabilities_used` populated per data-model.md §6 (Acceptance Scenario US3.1) (depends on T020, T029)

**Checkpoint**: todas as três user stories funcionam de forma independente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: itens exigidos pelo spec que não pertencem ao teste independente de nenhuma story
específica.

- [ ] T032 [P] Write `skills/ppt-master/adapters/github-copilot/capabilities.json` declaring only the capability interface, with a `notes` field stating no functional Copilot adapter exists yet (FR-018)
- [ ] T033 [P] Verify `skills/ppt-master/requirements.txt` / `skills/ppt-master/scripts/requirements.txt` already document `PyYAML` (optional) and `Pillow` sufficiently for `context_intake.py` and `contact_sheet.py`; add a comment only if a gap is found — no new hard dependency (research.md §1)
- [ ] T034 Update AGENTS.md Command Quick Reference with `context_intake.py`, `brand_lint.py`, `contact_sheet.py`, and `conformance_report.py`, following `docs/rules/prompt-style.md` conventions (depends on T012, T015, T016, T017)
- [ ] T035 Re-check delivery checklist items CHK001, CHK017, CHK022, CHK025, CHK029 in [checklists/delivery.md](./checklists/delivery.md), and confirm the `/speckit-analyze` findings G1–G6, U1–U3, I1–I2, and C1 (all three 2026-07-27 passes) are all closed by T007, T014, T015, T017, T021, T022, T023, T024, and the spec.md/data-model.md updates, against the implemented code — mark each resolved or note the remaining gap (depends on T012, T013, T014, T015, T016, T017, T021, T022, T023, T024, T032)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode começar imediatamente.
- **Foundational (Phase 2)**: depende de Setup — bloqueia todas as user stories.
- **User Story 1 (Phase 3)**: depende só de Foundational. É o P0 solicitado.
- **User Story 2 (Phase 4)**: depende só de Foundational (T012); não depende de US1, mas reusa a mesma fixture de diretório criada em Setup.
- **User Story 3 (Phase 5)**: depende de Foundational (T017 é construído em US1, então na prática Phase 5 só começa depois de T017 existir); T031 especificamente também consome a saída de T020 (US1).
- **Polish (Phase 6)**: depende de todas as stories desejadas estarem completas.

### User Story Dependencies

- **US1 (P1)**: nenhuma dependência de outra story — é o incremento P0 autossuficiente (agora inclui T022 verificação de não-regressão no Claude Code e T023 sign-off do mantenedor).
- **US2 (P2)**: nenhuma dependência funcional de US1 (ambas usam `context_intake.py` da Fase 2, mas exercitam ramos diferentes — sucesso vs. erro).
- **US3 (P3)**: depende do script `conformance_report.py` já existir (construído em US1, T017) e, para T031 especificamente, de um deck já gerado por US1 (T020).

### Within Each User Story

- Modelos/scripts antes de execução end-to-end.
- Execução end-to-end antes de verificação de Acceptance Scenarios.
- Story completa antes de avançar para a próxima prioridade (embora US1→US2→US3 sejam
  tecnicamente paralelizáveis após a Fase 2, exceto T031).

### Parallel Opportunities

- Todas as tarefas `[P]` da Fase 1 (T002–T004) em paralelo.
- Na Fase 2: T005, T006, T008, T013 em paralelo entre si (arquivos distintos, sem dependência
  entre eles); T007 depende de T005; T009 depende de T005–T008; T012 depende só de T003; T014
  depende só de T004.
- Na Fase 3: T016 em paralelo com T015 (arquivos distintos); T017 depende de ambos e de T014
  (leitura de `capabilities.json`); T022 depende de T012/T015/T016/T017 mas não de T019/T020/T021
  (roda contra um projeto Claude Code separado, não contra a fixture facom-talk); T023 depende
  só de T021.
- Na Fase 4: T025 pode rodar em paralelo com qualquer tarefa da Fase 3 depois que T012 (Fase 2)
  estiver pronto.
- Na Fase 5: T029 depende de T017; T030/T031 sequenciais depois de T029.
- Na Fase 6: T032 e T033 em paralelo; T034 e T035 sequenciais no final.

---

## Parallel Example: Foundational Phase

```bash
# Depois de T003/T004 (Setup) completos, disparar em paralelo:
Task: "Download official FACOM/UFMS brand assets into skills/ppt-master/templates/brands/facom-ufms/images/ (T005)"
Task: "Write skills/ppt-master/templates/brands/facom-ufms/templates/design_spec.md (T008)"
Task: "Write skills/ppt-master/references/animation-presets.md (T013)"
```

---

## Implementation Strategy

### P0 primeiro (Setup + Foundational + User Story 1)

1. Completar Fase 1: Setup.
2. Completar Fase 2: Foundational (CRÍTICO — bloqueia todas as stories).
3. Completar Fase 3: User Story 1.
4. **PARAR e VALIDAR**: rodar `quickstart.md` contra `conformance/fixtures/facom-talk/CONTEXT.md`
   real e revisar o PPTX resultante como uma apresentação de verdade (SC-005, T023), confirmar a
   não-regressão no Claude Code (FR-012, T022), e ter alguém sem contexto prévio reproduzir o
   caminho só a partir do `quickstart.md` (SC-006, T024) — não apenas gerar um arquivo
   tecnicamente válido.
5. Esse é o ponto de entrega "palestra amanhã" — tudo que vem depois é incremento, não bloqueio.

### Entrega Incremental

1. Setup e Foundational → base pronta.
2. Somar User Story 1 → testar de forma independente → **deck real gerado (MVP/P0)**.
3. Somar User Story 2 → testar de forma independente → mensagens de erro acionáveis.
4. Somar User Story 3 → testar de forma independente → relatório único de conformidade.
5. Somar Polish → Copilot interface-only, documentação, checklist reconciliado.

---

## Notes

- `[P]` = arquivos diferentes, sem dependência entre as tarefas.
- Rótulo `[Story]` mapeia a tarefa à user story correspondente para rastreabilidade.
- Nenhum script existente do motor (`svg_to_pptx.py`, `svg_quality_checker.py`,
  `visual_review.py`, `project_manager.py`) é modificado por nenhuma tarefa acima — apenas
  chamado (FR-014).
- T013, T016 e T017 resolvem diretamente os gaps CHK017, CHK022 e CHK025/CHK029 encontrados em
  [checklists/delivery.md](./checklists/delivery.md); T035 fecha o ciclo verificando isso.
- T007 (fonte da `protection_area_ratio`), T015 (pre-flight de assets ausentes), T017 (fallback
  por capacidade), T021/T023 (SC-005/SC-007) e T022 (não-regressão no Claude Code) resolvem os
  achados U1, G1, G2, G3, G4 e G5 da primeira passagem `/speckit-analyze` de 2026-07-27; a
  entidade "Deck FACOM" (I1) foi adicionada a spec.md Key Entities na mesma passagem.
- T024 (SC-006, revisão com olhos frescos de `quickstart.md`) e o nome concreto de fixture em
  T022 (`examples/ppt169_attention_is_all_you_need/`) resolvem G6 e U2, achados na segunda
  passagem `/speckit-analyze` do mesmo dia — a primeira passagem só fechou 2 das 3 lacunas de
  Success Criteria (SC-005 e SC-007), deixando SC-006 aberto até esta correção.
- A terceira passagem `/speckit-analyze` do mesmo dia encontrou uma ambiguidade real deixada
  pela correção de T017 na segunda passagem: um gate `skipped` por capacidade ausente não tinha
  semântica de bloqueio definida. Resolvido em FR-019 (spec.md), data-model.md §6 e
  cli-contract.md — `skipped` agora bloqueia a exportação com o mesmo efeito de `fail` (C1/I2);
  T014 também teve a redação "for this session" corrigida para refletir que `capabilities.json`
  é um arquivo de adapter versionado, não uma declaração por sessão (U3).
- Evitar: tarefas vagas, conflito no mesmo arquivo entre tarefas `[P]`, dependências entre
  stories que quebrem a independência de US1.
