---
deck_id: facom-ufms-talk
kind: deck
summary: Palestra técnica FACOM/UFMS 16:9 — aulas, defesas, seminários e projetos de pesquisa e extensão; identidade herdada do brand facom-ufms.
keywords: [facom, ufms, palestra, aula, defesa, seminario, tecnico]
brand_ref: facom-ufms
primary_color: "#0088B7"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
native_structure_mode: structured
replication_mode: standard
page_count: 3
---

# FACOM/UFMS Palestra Técnica — Design Specification

> Três protótipos mínimos (`01_cover.svg`, `02_content.svg`, `03_ending.svg`) cobrem os três
> papéis obrigatórios de FR-007 (abertura/conteúdo/encerramento). `replication_mode: standard`
> — o Strategist de cada projeto pode repetir/reordenar a página de conteúdo conforme o
> `CONTEXT.md`, mantendo a identidade herdada de
> `../../brands/facom-ufms/templates/design_spec.md` (não duplicada aqui — CONTEXT.md §3.6).
> Uma matriz mais ampla de papéis (TOC, capítulo, etc.) fica para uma iteração posterior
> (ver plan.md § Faseamento).

## I. Template Overview

| Application context | Definition |
| --- | --- |
| Recurring presentation family | Palestras técnicas, aulas, defesas de qualificação/dissertação/tese, seminários, apresentações de projetos de pesquisa e extensão da FACOM/UFMS |
| Intended audiences and outcomes | Estudantes, docentes, banca examinadora ou público de seminário; entender o conteúdo técnico apresentado e, quando aplicável, avaliar/discutir a contribuição |
| Delivery and reading assumptions | Apresentação ao vivo conduzida pela pessoa palestrante, com notas do apresentador; slides devem permanecer legíveis para quem consulta depois via `svg_final/`/PPTX exportado |
| Representative narrative/page roles | Abertura (capa institucional), Conteúdo (1+ páginas conforme o `CONTEXT.md`), Encerramento (agradecimentos/contato) — mínimo obrigatório por FR-007; o Strategist decide quantidade e ordem de páginas de Conteúdo por projeto |

## II. Page Roles

| Role | Purpose | Brand elements expected |
| --- | --- | --- |
| Abertura | Título da palestra, nome da pessoa palestrante, afiliação, data | Assinatura UFMS (positiva/negativa conforme fundo), grafo FACOM como motivo estrutural discreto |
| Conteúdo | Uma função narrativa principal por página (CONTEXT.md corpo) | Cor institucional como token de hierarquia, nunca como cor de destaque de dado |
| Encerramento | Agradecimentos, contato, referências/citações quando `delivery.citations: true` | Assinatura UFMS; rodapé institucional configurável (não obrigatório em toda página) |

## III. Color Scheme

Herdado integralmente de `../../brands/facom-ufms/templates/design_spec.md` §II — não
reprojetado aqui.

## IV. Typography

Herdado integralmente de `../../brands/facom-ufms/templates/design_spec.md` §III.

## V. Logo & Brand Application

Herdado integralmente de `../../brands/facom-ufms/templates/design_spec.md` §IV — inclui a
regra de seleção positiva/negativa por contraste e a área de proteção baseada em módulos de
grid (`../../brands/facom-ufms/brand-policy.yaml`).

## VI. Voice & Tone

Herdado de `../../brands/facom-ufms/templates/design_spec.md` §V, com uma adição por contexto
de entrega:

| Delivery context | Tone adjustment |
| --- | --- |
| Aula | Didático, passo a passo, mais texto de apoio por página |
| Defesa | Formal, denso, citações completas quando `delivery.citations: true` |
| Seminário/projeto de pesquisa | Direto, resultado-primeiro, menos texto por página |
