# Research: Gerar Deck FACOM/UFMS Animado a partir de CONTEXT.md

**Input**: [spec.md](./spec.md), [constitution.md](../../.specify/memory/constitution.md), CONTEXT.md §§3–9, 15–16

Todos os itens abaixo eram `NEEDS CLARIFICATION` implícitos no Technical Context até esta
pesquisa; cada um foi resolvido a partir do código e da documentação já existentes no
repositório (não de suposições), para respeitar a Constituição Princípio I (núcleo único) e
FR-014 (não reescrever o motor).

## 1. Linguagem/versão e dependências

- **Decision**: Python 3 (mesmo interpretador já usado por `skills/ppt-master/scripts/`), sem
  fixar uma versão mínima nova; nenhum arquivo `pyproject.toml`/`setup.cfg`/`.python-version`
  existe no repositório hoje, então esta feature não introduz um. Novo código Python segue o
  mesmo padrão "stdlib primeiro, dependência opcional com fallback" já usado em
  `project_specs.py` (`Dependencies: None`) e `svg_quality_checker.py` (parser YAML de
  fallback quando PyYAML está ausente).
- **Rationale**: instalar a skill continua bastando para ter capacidade completa (princípio já
  documentado em `requirements.txt`); adicionar uma dependência obrigatória nova (ex.:
  `jsonschema`) quebraria esse contrato para todos os usuários existentes, não só para o
  caminho FACOM.
- **Alternatives considered**: fixar Python 3.11+ e usar `jsonschema` para validar o
  `CONTEXT.md` — rejeitado porque o projeto inteiro hoje valida schemas JSON à mão
  (`project_specs.py::validate_markdown_schema` lê `design_spec.schema.json` /
  `spec_lock.schema.json` sem a lib `jsonschema`); introduzir uma segunda forma de validação
  quebraria a consistência interna sem necessidade.

## 2. Onde e como validar/normalizar o `CONTEXT.md`

- **Decision**: novo schema `skills/ppt-master/templates/schemas/context.schema.json`, no
  mesmo diretório e mesmo estilo dos schemas já existentes (`design_spec.schema.json`,
  `spec_lock.schema.json`), e um novo módulo `skills/ppt-master/scripts/context_intake.py`
  (nome espelhando `pptx_intake.py`) com uma função `validate_and_normalize(context_md_path)`
  reaproveitando o parser de frontmatter YAML já usado por `register_template.py`
  (PyYAML quando disponível, aviso e fallback manual quando não). A saída normalizada é
  escrita em `<project_path>/analysis/context_brief.json`, ao lado de
  `analysis/*.facts.json`, porque semanticamente é o mesmo tipo de artefato: "fatos extraídos
  de máquina, não decisões de design" (CONTEXT.md §3.3).
- **Rationale**: reaproveita 100% do padrão de schema + parser já validado em produção pelo
  projeto; mantém `CONTEXT.md` como um novo tipo de entrada de Step 1 sem tocar
  `project_manager.py` nem `project_specs.py`.
- **Alternatives considered**: estender `project_manager.py import-sources` para aceitar
  frontmatter YAML diretamente — rejeitado porque misturaria o contrato "fonte de conteúdo"
  (Markdown/PDF/URL) com o contrato "parâmetros operacionais versionados", violando a mesma
  separação que a Constituição Princípio II exige entre artefatos.

## 3. Onde plugar o `CONTEXT.md` no pipeline Generate PPTX existente

- **Decision**: `context_intake.py` é um passo que roda **antes** do Step 1 padrão
  (`generate-pptx.md`): ele (a) valida e normaliza o `CONTEXT.md`, (b) chama
  `project_manager.py init --format ppt169` se o projeto ainda não existir, (c) encaminha o
  corpo Markdown do `CONTEXT.md` para `project_manager.py import-sources` como a fonte
  canônica, e (d) grava `analysis/context_brief.json`. Dali em diante, Step 1–7 de
  `generate-pptx.md` seguem inalterados; o Strategist (Step 4) lê
  `analysis/context_brief.json` do mesmo jeito que já lê `analysis/*.facts.json`.
- **Rationale**: satisfaz FR-004 e FR-014 (nenhuma rota nova, nenhuma reescrita) — o
  `CONTEXT.md` vira apenas mais uma fonte de entrada estruturada para uma pipeline que já
  existe, exatamente como o Épico 1 do CONTEXT.md pede ("integrar com Step 1 e Step 4 sem
  eliminar gates obrigatórios").
- **Alternatives considered**: transformar `CONTEXT.md` em uma quinta rota de produto —
  explicitamente proibido pela Constituição Princípio III e FR-004.

## 4. Pacote de marca FACOM/UFMS

- **Decision**: seguir o padrão de marca já existente em
  `skills/ppt-master/templates/brands/<chave>/{images/, templates/design_spec.md}` (visto em
  `brands/anthropic`, `brands/google`), adicionando `brands/facom-ufms/` com os assets oficiais
  baixados uma única vez, mais um `provenance.json` (URL, data de captura, condição de uso —
  FR-013) e um `brand-policy.yaml` (cor `#0088B7`, versões positiva/negativa, contraste,
  área de proteção) lido pelo novo `brand_lint.py`. A entrada é registrada em
  `brands/brands_index.json`, igual às marcas existentes. O primeiro Deck reutilizável fica em
  `skills/ppt-master/templates/decks/facom-ufms-talk/`, registrado em `decks/decks_index.json`,
  seguindo CONTEXT.md §3.6 ("deve começar como Deck").
- **Rationale**: zero estrutura nova é inventada — a feature só adiciona uma entrada a um
  catálogo que já existe para outras marcas, o que é a definição operacional de "núcleo único,
  adapters finos" aplicada a dados de marca em vez de código de host.
- **Alternatives considered**: criar uma árvore `packages/brands/facom-ufms/` nova
  (CONTEXT.md §7, direção aspiracional) — rejeitado para o MVP porque o próprio CONTEXT.md
  §7 diz que essa árvore "não é uma obrigação de reestruturação imediata" e o usuário pediu
  explicitamente para preservar a arquitetura existente.

## 5. Brand lint

- **Decision**: novo script `skills/ppt-master/scripts/brand_lint.py`, no mesmo estilo dos
  demais checkers (`svg_quality_checker.py`, `batch_validate.py`): lê `svg_output/` (cor de
  fundo por página, uso de `<image>`/`<use>` de logo) e o `brand-policy.yaml` do Pacote de
  Marca ativo, e falha (`exit != 0`) em qualquer violação conhecida (FR-011): cor
  institucional incorreta, logo redimensionado fora de proporção, versão de marca
  incompatível com o contraste do fundo.
- **Rationale**: não existe hoje nenhum checker de contraste/cor no repositório
  (`svg_quality_checker.py` não tem lógica de cor/contraste) — é capacidade genuinamente nova,
  mas aditiva e isolada em um único arquivo, sem tocar os checkers existentes.
- **Alternatives considered**: embutir as regras de marca dentro de
  `svg_quality_checker.py` — rejeitado porque acopla uma política de uma marca específica a um
  checker de gramática SVG genérico usado por todo projeto/marca, violando Princípio VI
  (marca como política isolada e verificável, não texto/lógica espalhada).

## 6. Renderização de todas as páginas + "contact sheet"

- **Decision**: reaproveitar `skills/ppt-master/scripts/visual_review.py` (renderizador
  Playwright/Chromium já existente, produz PNGs 1280×720 por página em
  `<project>/.preview/`) para a checagem "todas as páginas renderizam" (FR-010), e adicionar
  um script fino `skills/ppt-master/scripts/contact_sheet.py` que usa `Pillow` (já é
  dependência do projeto) para compor um único grid de miniaturas a partir dessas PNGs — sem
  reimplementar renderização.
- **Rationale**: `visual_review.py` já resolve a parte difícil (fontes CJK/fallback, ícones
  inline); reescrever isso seria exatamente o tipo de duplicação que a Constituição Princípio I
  proíbe. `contact_sheet.py` fica pequeno o bastante para não introduzir dependência nova.
- **Alternatives considered**: usar `cairosvg` — já avaliado e rejeitado pelo próprio projeto
  (comentário em `visual_review.py`: sem fallback de fonte para CJK).

## 7. Auditoria OOXML e bloqueio rígido de exportação (Clarification 2026-07-27)

- **Decision**: `svg_to_pptx.py` (Step 7.3 existente) já escreve
  `validation/<project>_<timestamp>.report.json` com status `passed` /
  `passed-with-warnings` cobrindo integridade de pacote/relações OOXML — isso já cobre a
  maior parte de FR-010. O gate rígido decidido na clarificação (FR-019: nenhum PPTX é
  gravado em disco enquanto um gate falhar) é implementado fazendo o novo
  `conformance_report.py` (§8) rodar **antes** de `svg_to_pptx.py` os gates que hoje não
  bloqueiam a exportação nativa (brand lint, render completo, `context.schema.json`), e
  interrompendo a cadeia com um erro claro se qualquer um falhar — sem alterar o
  comportamento interno já validado de `svg_to_pptx.py`.
- **Rationale**: preserva o motor existente (FR-014) e implementa o hard-gate apenas na nova
  camada de orquestração, não dentro dos scripts herdados.
- **Alternatives considered**: modificar `svg_to_pptx.py` para também esperar o brand lint —
  rejeitado; acoplaria um checker específico de marca a um exportador genérico usado por toda
  marca/projeto.

## 8. Relatório único de conformidade

- **Decision**: novo script `skills/ppt-master/scripts/conformance_report.py` que
  **orquestra** (não reimplementa) os checkers existentes e novos — schema
  (`context_intake.py --validate-only`), `svg_quality_checker.py`, `brand_lint.py`,
  `visual_review.py` + `contact_sheet.py`, e o `validation/*.report.json` já produzido por
  `svg_to_pptx.py` — e escreve um `validation/conformance_report.json` único, com host e
  capacidades declaradas (ver §9), resultado por gate, e status geral.
- **Rationale**: US3 do spec pede "um relatório único" sem exigir reimplementar nenhum gate;
  isso é puramente um agregador, minimizando superfície nova de código.
- **Alternatives considered**: nenhuma — é a única opção compatível com FR-014.

## 9. Contrato de capacidades de host e adapter Codex

- **Decision**: novo schema `skills/ppt-master/templates/schemas/host-capabilities.schema.json`
  (campos conforme CONTEXT.md §7.1: `host_id`, `skill_discovery`, `shell`, `filesystem_read`,
  `filesystem_write`, `browser`, `image_generation`, `parallel_agents`,
  `interactive_confirmation`, `image_inspection`, `pptx_rendering`), com um arquivo de dados
  por host em `skills/ppt-master/adapters/<host_id>/capabilities.json`. Para esta slice: apenas
  `skills/ppt-master/adapters/codex/capabilities.json` (funcional) e
  `skills/ppt-master/adapters/github-copilot/capabilities.json` (interface definida, sem
  adapter funcional — FR-018/Assumption). `browser: optional` é o campo mais sensível para
  Codex porque `visual_review.py` depende de Playwright/Chromium; quando ausente, o workflow
  usa o fallback já previsto (pular render automático e declarar a limitação, nunca simular
  sucesso — FR-015).
- **Rationale**: não existe hoje nenhum mecanismo de capacidades no repositório (confirmado por
  busca — nenhuma referência a `host_capabilities` ou schema equivalente); é capacidade
  genuinamente nova exigida pela Constituição Princípio VII, implementada como dado
  declarativo (JSON), não como código condicional espalhado pelos workflows.
- **Alternatives considered**: inferir capacidades dinamicamente em tempo de execução via
  tentativa/erro — rejeitado; a Constituição Princípio VII exige declaração explícita, não
  detecção silenciosa.

## 10. Presets de animação (`none` / `subtle` / `purposeful` / `narrative`)

- **Decision**: os presets **não** viram um novo script determinístico — `animations.json` já é
  autorado por um agente seguindo `workflows/stages/customize-animations.md`, que é
  deliberadamente qualitativo (a criatividade de composição é permitida pela Constituição
  Princípio II). Esta feature adiciona uma pequena tabela de mapeamento em
  `skills/ppt-master/references/animation-presets.md` (nova referência, carregada
  condicionalmente por `customize-animations.md`) que traduz cada valor de
  `delivery.animations` do `CONTEXT.md` normalizado em uma instrução objetiva de autoria
  (`none` → não editar `animations.json`; `purposeful` → aplicar entradas/ênfases/saídas
  ancoradas semanticamente conforme já documentado, sem Morph decorativo não solicitado). A
  validação determinística continua sendo `animation_config.py validate`, já existente.
- **Rationale**: mantém o autoral criativo humano/IA onde já é criativo hoje, e adiciona
  determinismo apenas no mapeamento CONTEXT.md → instrução, que é onde a Constituição exige
  determinismo (roteamento e contratos), não na composição em si.
- **Alternatives considered**: gerar `animations.json` proceduralmente a partir do preset —
  rejeitado; o projeto já modela animação como decisão de design assistida por IA sobre um
  contrato validável, não como geração mecânica, e mudar isso extrapolaria o escopo desta
  slice.

## 11. Fixture de smoke test / palestra real

- **Decision**: a fixture vive em `skills/ppt-master/templates/scaffolds/` **não** — fica em um
  novo diretório de fixtures de conformidade, `conformance/fixtures/facom-talk/CONTEXT.md`
  (nome do caminho já sugerido por CONTEXT.md §7, mas usado aqui apenas como um diretório novo
  e isolado, não como reestruturação do restante do repositório), contendo o `CONTEXT.md` real
  da palestra do mantenedor (ou uma cópia versionada dele) usado por FR-017 e SC-005.
- **Rationale**: isola o artefato de aceitação vivo sem exigir mover nenhuma pasta existente;
  `conformance/` é uma adição, não uma migração.
- **Alternatives considered**: guardar a fixture dentro de `examples/` — rejeitado porque
  `examples/` hoje documenta capacidades gerais do produto, não casos de aceitação de uma
  feature específica; misturar os dois prejudicaria ambos os propósitos.
