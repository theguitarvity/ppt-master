---
brand_id: facom-ufms
kind: brand
summary: FACOM/UFMS institutional identity — technical talks, lectures, defenses, seminars, research and extension projects at the Faculdade de Computação, Universidade Federal de Mato Grosso do Sul
primary_color: "#0088B7"
---

# FACOM/UFMS Brand Specification

> Identity-only preset. No SVG page roster — pages are composed freely under these
> constraints. Full verifiable rules (thresholds, protection area, asset provenance) live in
> `../brand-policy.yaml` and `../provenance.json`; `brand_lint.py` enforces them.

## I. Brand Overview

| Property | Value |
|---|---|
| Brand Name | FACOM/UFMS (Faculdade de Computação — Universidade Federal de Mato Grosso do Sul) |
| Use Cases | Palestras técnicas, aulas, defesas, seminários, projetos de pesquisa e extensão |
| Tone | Acadêmico, técnico, direto, institucional sem ser burocrático |
| Sources | Manual de Identidade Visual UFMS (abr. 2026, Resolução nº 493-Coun/UFMS); página de identidade visual FACOM (`https://www.facom.ufms.br/institucional/identidade-visual/`); assets oficiais capturados em 2026-07-27 — ver `../provenance.json` |

## II. Color Scheme

| Role | HEX | Provenance | Notes |
|---|---|---|---|
| primary | `#0088B7` | fact | Cor institucional UFMS oficial (Pantone 116-16U) — Manual p.13 |
| neutral-dark | `#1A1A1A` | approx | Azul profundo/preto para texto sobre superfícies claras |
| bg | `#FFFFFF` | approx | Fundo padrão claro — abaixo do limiar de 40% de preenchimento (Manual p.27) |
| surface | `#F2F7F9` | approx | Superfície levemente azulada para cards, derivada do primary |
| border | `#D6E4E9` | approx | Divisores e bordas discretas |
| muted-text | `#5A6B70` | approx | Texto secundário, legendas de gráfico |

A cor institucional (`primary`) NUNCA recebe destaque de conteúdo (nunca é reaproveitada como
cor de dado/gráfico arbitrário) — CONTEXT.md §4.3. Cor de destaque de conteúdo é derivada por
página conforme a narrativa, nunca aplicada à marca oficial.

## III. Typography

| Role | Family | Weight |
|---|---|---|
| title | `"Futura XBlkCn BT", "Poppins", Arial, sans-serif` | 700 (apenas na assinatura institucional intacta — ver nota) |
| body | `"Inter", "Helvetica Neue", Arial, sans-serif` | 400 |
| slogan | `"Poppins", Arial, sans-serif` | 700 |

> `Futura XBlkCn BT` (personalização institucional) e `Swis721 Cn BT` são tipografias oficiais
> da assinatura UFMS (Manual p.13) e NÃO são redistribuídas neste pacote nem usadas para
> compor texto de corpo/título dos decks gerados — elas só existem, sem alteração, dentro dos
> arquivos de logo oficiais em `../images/`. Texto de corpo e títulos de conteúdo usam a
> hierarquia acadêmica/técnica acima (fontes livres/instaláveis de fallback).

## IV. Logo

O símbolo FACOM e a assinatura UFMS NUNCA são redesenhados por IA; são usados exatamente como
baixados (ver `../provenance.json`), sem distorção.

| File | Form | Usage |
|---|---|---|
| `../images/grafo_facom.png` | Grafo de Petersen (símbolo FACOM: 10 vértices, 15 arestas, número cromático 3) | Motivo estrutural discreto — fundo geométrico, elemento de abertura/encerramento; nunca como decoração repetitiva |
| `../images/facom_logo_full.png` | Logo institucional FACOM completo | Rodapé/assinatura de unidade quando a FACOM precisa de identificação própria além da UFMS |
| `../images/ufms_logo_positivo.png` | Assinatura UFMS — versão positiva/colorida | Fundos claros (≤ 40% de preenchimento — Manual p.27) |
| `../images/ufms_logo_negativo.png` | Assinatura UFMS — versão negativa/branca | Fundos escuros (> 40% de preenchimento) ou sobre imagem complexa sem área neutra (Manual p.28) |

- Seleção positiva/negativa: automática por `brand_lint.py`, conforme `contrast_threshold_dark_fill_pct` em `brand-policy.yaml` — nunca escolhida "a olho" pelo Executor.
- Área de proteção: 3 módulos de grid ao redor da marca (`protection_area_ratio: "3x"` em `brand-policy.yaml`) — não é uma margem arbitrária.
- Sobre imagem complexa: posicionar em área neutra ou usar box branco (Manual p.28); nunca sobrepor o monumento símbolo.
- Convivência de marcas: UFMS à direita/abaixo quando ao lado de marcas internas/externas comuns; UFMS à esquerda/acima quando ao lado de Governo Federal/ministérios (CONTEXT.md §4.2) — aplicável apenas quando o `CONTEXT.md` da palestra declarar co-branding explícito; fora do escopo do MVP quando não declarado.

## V. Voice & Tone

- Formality: acadêmico-técnico, sem jargão de marketing
- Person: nós / vocês (pt-BR), preferindo voz ativa
- Emoji: evitar em conteúdo formal (aula/defesa); aceitável com moderação em seminários informais
- Abbreviations: soletrar por extenso na primeira ocorrência (ex.: "Faculdade de Computação (FACOM)")

## VI. Icon Style

- Preference: stroke, geometria angular discreta ecoando o Grafo de Petersen quando possível

> Convenção de apresentação, não token oficial de marca. Preferir famílias `tabler` ou `lucide`
> stroke quando se encaixarem no deck; manter uma família de ícone consistente por deck.
