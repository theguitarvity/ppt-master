# Quickstart: Gerar um Deck FACOM/UFMS no Codex a partir de um CONTEXT.md

Este é o caminho feliz único e reproduzível exigido por FR-016. Cobre exatamente o cenário
"palestra amanhã": uma pessoa com um `CONTEXT.md` válido chega a um PPTX 16:9 FACOM/UFMS
completo, animado, com notas, sem editar scripts.

## Pré-requisitos

- Repositório clonado com `skills/ppt-master/` presente.
- `pip install -r requirements.txt` executado uma vez (ver raiz do repositório).
- Um `CONTEXT.md` válido na raiz do repositório (frontmatter YAML + corpo Markdown), com
  `brand.profile: facom-ufms` para aplicar a identidade institucional.
- Sessão Codex em modo skills, com `skills/ppt-master/adapters/codex/capabilities.json`
  presente (declarações de capacidade reais desta sessão).

## Exemplo mínimo de `CONTEXT.md`

O único campo obrigatório é `presentation.title`; todo o resto tem default (ver
`skills/ppt-master/templates/schemas/context.schema.json` para o schema completo).

```yaml
---
presentation:
  title: "Título da palestra"
  audience: "Estudantes e docentes da FACOM"
  duration_minutes: 30
brand:
  profile: facom-ufms
delivery:
  animations: purposeful
  speaker_notes: true
---

# Tese central

...conteúdo real da palestra aqui...
```

## Passos

1. **Validar e normalizar o CONTEXT.md**

   ```bash
   python3 skills/ppt-master/scripts/context_intake.py CONTEXT.md --project-dir projects/<slug>
   ```

   Sucesso (`exit 0`) inicializa o projeto via `project_manager.py init` (se `projects/<slug>`
   ainda não existir), importa o corpo Markdown como fonte canônica, e grava
   `analysis/context_brief.json` com todos os defaults aplicados. **O diretório real do
   projeto leva o sufixo padrão do motor** (`projects/<slug>_ppt169_<AAAAMMDD>`) — o comando
   imprime `[OK] .../analysis/context_brief.json written for project: <caminho real>`; use
   esse caminho exato (não `projects/<slug>` literal) em todos os passos seguintes. Um erro de
   schema (`exit 1`) aponta exatamente o campo problemático — corrija o `CONTEXT.md` e rode de
   novo antes de prosseguir.

2. **Executar o pipeline Generate PPTX existente** — Steps 1–7 de
   [`generate-pptx.md`](../../../skills/ppt-master/workflows/generate-pptx.md), sem alteração
   de procedimento. O Strategist (Step 4) lê `analysis/context_brief.json` como leria qualquer
   outro fato extraído; a marca `facom-ufms` (se declarada) direciona o Strategist ao Pacote de
   Marca em `skills/ppt-master/templates/brands/facom-ufms/`. Os gates humanos ⛔ do pipeline
   permanecem — este quickstart não os remove (Constituição Princípio V).

3. **Rodar a suíte de conformidade antes da exportação final**

   ```bash
   python3 skills/ppt-master/scripts/conformance_report.py projects/<slug> --host codex
   ```

   - `exit 0`: todos os gates passaram, `svg_to_pptx.py` já rodou dentro do comando acima, e o
     PPTX final está em `projects/<slug>/exports/`. Leia
     `projects/<slug>/validation/conformance_report.json` para o resumo por gate.
   - `exit 10`: um gate pré-exportação falhou (schema, SVG, render, brand lint) — **nenhum
     PPTX foi gravado** (FR-019). O relatório lista exatamente quais gates falharam; corrija e
     rode novamente.

4. **Revisar** `projects/<slug>/validation/contact_sheet.png` e o PPTX aberto em PowerPoint ou
   LibreOffice antes de apresentar (SC-005 — avaliação humana como apresentação real, não
   apenas arquivo tecnicamente válido).

## Fixture de smoke test

```bash
python3 skills/ppt-master/scripts/context_intake.py conformance/fixtures/facom-talk/CONTEXT.md --project-dir projects/facom-talk-smoke
python3 skills/ppt-master/scripts/conformance_report.py projects/facom-talk-smoke --host codex
```

Usa o `CONTEXT.md` real da palestra do mantenedor (ou uma cópia versionada dele) para verificar
o caminho fim-a-fim sem entrada manual de dados (FR-017).

## Quando `brand.profile` não é declarado

O mesmo caminho funciona sem identidade FACOM/UFMS — `conformance_report.py` simplesmente pula
`brand_lint.py` (nenhuma marca ativa para validar). Isso não faz parte do escopo de aceitação
desta feature, mas confirma que nada no pipeline existente foi bloqueado por esta mudança.
