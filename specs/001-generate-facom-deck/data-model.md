# Data Model: Gerar Deck FACOM/UFMS Animado a partir de CONTEXT.md

Deriva as 5 Key Entities de [spec.md](./spec.md) para os artefatos concretos decididos em
[research.md](./research.md). Nenhuma entidade introduz um banco de dados ou serviço — todas
são arquivos versionados dentro da árvore já existente (Constituição Princípio II).

## 1. CONTEXT.md / Contexto da Apresentação

**Onde vive**: entrada fornecida pela pessoa usuária; arquivo `CONTEXT.md` fora ou dentro do
projeto (copiado para a raiz do repositório antes do intake, conforme CONTEXT.md §17.1).

**Formato**: frontmatter YAML + corpo Markdown.

| Campo (frontmatter) | Tipo | Obrigatório | Default se omitido |
| --- | --- | --- | --- |
| `presentation.title` | string | **sim** | — (erro acionável, FR-002) |
| `presentation.language` | string (BCP-47) | não | `pt-BR` |
| `presentation.audience` | string | não | inferido do corpo Markdown; registrado como default aplicado |
| `presentation.objective` | string | não | inferido do corpo Markdown; registrado como default aplicado |
| `presentation.duration_minutes` | number | não | `30` |
| `presentation.slide_count` | number \| `"auto"` | não | `"auto"` |
| `presentation.format` | enum | não | `ppt169` (único suportado nesta slice — Assumption) |
| `brand.profile` | string | não | nenhum perfil de marca (deck genérico) |
| `delivery.animations` | enum: `none`\|`subtle`\|`purposeful`\|`narrative` | não | `none` |
| `delivery.speaker_notes` | boolean | não | `false` |
| `delivery.citations` | boolean | não | `false` |
| `delivery.output_name` | string | não | `<title-slug>.pptx` |
| `quality.mode` | enum | não | `standard` |

**Corpo Markdown**: conteúdo narrativo livre (tese central, conteúdo, evidências); preservado
integralmente, nunca reescrito pelo parser (FR-003).

**Regras de validação** (→ `context.schema.json`, [contracts/](./contracts/)):

- Campo desconhecido no frontmatter → aviso, não erro (Assumption documentada no spec).
- `presentation.title` ausente → erro acionável, geração não inicia.
- `brand.profile` referenciando um perfil sem entrada em `brands_index.json` → erro acionável.
- `presentation.format` diferente de `ppt169` → erro acionável nesta slice (fora de escopo).

## 2. Brief Normalizado

**Onde vive**: `<project_path>/analysis/context_brief.json` (mesma pasta e semântica de
`analysis/*.facts.json` — "fatos extraídos de máquina, não decisões de design").

**Produzido por**: `context_intake.py` (ver [research.md](./research.md) §2–3).

**Campos**:

| Campo | Descrição |
| --- | --- |
| `source_context_path` | caminho do `CONTEXT.md` original, para rastreabilidade |
| `resolved` | objeto com todos os campos do frontmatter já expandidos com os defaults aplicados |
| `defaults_applied` | lista de `{field, default_value, reason}` — nunca vazia silenciosamente quando um default foi usado |
| `warnings` | lista de avisos não bloqueantes (ex.: campo desconhecido) |
| `schema_version` | versão de `context.schema.json` usada na validação |
| `created_at_context_hash` | hash do `CONTEXT.md` de origem, para detectar reprocessamento |

**Relacionamento**: consumido pelo Strategist (Step 4 de `generate-pptx.md`) do mesmo jeito
que `sources/*.facts.json` já é consumido — nunca duplicado dentro de `design_spec.md`.

## 3. Pacote de Marca FACOM/UFMS

**Onde vive**: `skills/ppt-master/templates/brands/facom-ufms/` (segue exatamente o padrão de
`brands/anthropic` e `brands/google`).

```text
skills/ppt-master/templates/brands/facom-ufms/
├── images/                  # logos oficiais baixados uma única vez (grafo_facom.png, etc.)
├── templates/design_spec.md # direção de marca no formato já usado pelas demais marcas
├── brand-policy.yaml        # tokens + regras verificáveis (ver abaixo)
└── provenance.json          # URL/origem, data de captura, condição de uso por asset (FR-013)
```

**`brand-policy.yaml`** (campos mínimos, consumidos por `brand_lint.py`):

| Campo | Descrição |
| --- | --- |
| `institutional_color` | `#0088B7` |
| `mark_variants` | `{positive: <asset>, negative: <asset>}` |
| `contrast_threshold_dark_fill_pct` | `40` (acima disso, exigir variante `negative`) |
| `protection_area_ratio` | proporção mínima de área livre ao redor da marca — valor DEVE ser extraído do Manual de Identidade Visual UFMS (CONTEXT.md §4.1), nunca estimado |
| `protection_area_ratio_source` | citação da página/seção do Manual de onde `protection_area_ratio` foi extraído (proveniência do próprio token, não só dos assets — Princípio VIII) |
| `typography.signature` | referência à tipografia oficial (não redistribuída — ver Assumptions do spec) |

**`provenance.json`** (um registro por asset):

| Campo | Descrição |
| --- | --- |
| `asset` | caminho relativo em `images/` |
| `source_url` | URL oficial de origem (CONTEXT.md §4.1) |
| `captured_at` | data ISO de download |
| `usage_condition` | texto da condição de uso/licença aplicável |

**Registro**: uma entrada `"facom-ufms": {...}` adicionada a
`skills/ppt-master/templates/brands/brands_index.json`, no mesmo formato das entradas
existentes.

## 4. Deck FACOM "Palestra Técnica 16:9"

**Onde vive**: `skills/ppt-master/templates/decks/facom-ufms-talk/`, registrado em
`skills/ppt-master/templates/decks/decks_index.json`. Referencia o Pacote de Marca acima sem
duplicar seus tokens (CONTEXT.md §3.6 — "Deck referencia ou incorpora essa autoridade").

## 5. Declaração de Capacidades do Host

**Onde vive**: `skills/ppt-master/adapters/<host_id>/capabilities.json`, validado contra
`skills/ppt-master/templates/schemas/host-capabilities.schema.json` (ver
[contracts/](./contracts/)).

**Instâncias nesta slice**:

| Host | Arquivo | Escopo |
| --- | --- | --- |
| Codex | `skills/ppt-master/adapters/codex/capabilities.json` | Funcional — usado pelo caminho feliz (FR-012, FR-015, FR-016) |
| GitHub Copilot | `skills/ppt-master/adapters/github-copilot/capabilities.json` | Somente interface definida (FR-018) — nenhum adapter funcional |
| Claude Code | *(implícito, sem arquivo novo nesta slice)* | Caminho já funcional preservado sem regressão (FR-012); formalizar seu próprio `capabilities.json` fica para a evolução multimodelo (ver plan.md) |

**Campos** (herdados de CONTEXT.md §7.1, ver contrato completo em
[contracts/host-capabilities.schema.json](./contracts/host-capabilities.schema.json)):
`host_id`, `skill_discovery`, `shell`, `filesystem_read`, `filesystem_write`, `browser`,
`image_generation`, `parallel_agents`, `interactive_confirmation`, `image_inspection`,
`pptx_rendering`.

## 6. Relatório de Conformidade/Entrega

**Onde vive**: `<project_path>/validation/conformance_report.json`, escrito por
`conformance_report.py` (ver [research.md](./research.md) §7–8).

**Campos**:

| Campo | Descrição |
| --- | --- |
| `host_id` | host que executou a geração |
| `capabilities_used` | snapshot da `capabilities.json` efetiva no momento da execução |
| `gates` | lista ordenada de `{name, status: pass\|fail\|skipped, detail}` — um item por gate (schema, SVG, render+contact sheet, OOXML/postflight, overflow, brand lint); `skipped` é usado exclusivamente quando uma capacidade de host declarada em `capabilities.json` está ausente (FR-015), nunca como atalho de conveniência |
| `overall_status` | `pass` somente se **todos** os `gates` tiverem `status: pass`; `skipped` conta como não-passado, igual a `fail`, para este cálculo — caso contrário `blocked` (reflete FR-019 — nenhum PPTX é entregue quando `overall_status != pass`). `detail` de um gate `skipped` DEVE nomear a capacidade ausente, distinguindo-o de uma violação real. |
| `pptx_path` | presente apenas quando `overall_status == pass` |

**Relacionamento com FR-019**: `conformance_report.py` roda os gates que ainda não bloqueiam
`svg_to_pptx.py` (schema, brand lint, render completo) **antes** de invocar a exportação
nativa; se qualquer um falhar, a exportação (Step 7.3) nunca é chamada e nenhum `.pptx` é
gravado.
