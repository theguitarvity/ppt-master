# CONTEXT.md Animation Presets

> Load when a project was started from a `CONTEXT.md` (via `context_intake.py`) and
> `<project_path>/analysis/context_brief.json` declares a `delivery.animations` value. Maps
> that single value to concrete authoring/export instructions using the mechanisms already
> owned by [`animations.md`](./animations.md) and
> [`customize-animations`](../workflows/stages/customize-animations.md) — this file adds no
> new animation mechanism and edits nothing on its own.

## Mapping

| `delivery.animations` | Page transition | Per-element animation | `animations.json` / customize-animations stage |
|---|---|---|---|
| `none` | `-t none` at export | Leave at default `none` | Do not run; do not author one |
| `subtle` | `-t fade` (export default — no flag needed) | Leave at default `none` | Do not run; a deck that only needs restrained page-to-page movement is done at export time |
| `purposeful` | `-t fade`, or `-t morph` for pages Step 6 explicitly authored as a paired continuous action (see `animations.md` capability menu) | `-a auto` deck-wide, or run `customize-animations` when specific pages need narrative-critical ordering (title first, key evidence second, conclusion last) | Run only when `-a auto`'s canonical entrance policy is not enough for a specific page's narrative beat |
| `narrative` | Same as `purposeful`, plus prefer Morph for any slide-in/flip/camera-push/progressive-reveal moment the content already has (author the two static pages during Step 6 — Morph cannot be added after the fact) | Run `customize-animations` deck-wide, not just `-a auto` — every page with a reveal-worthy sequence gets deliberate order/timing, not only the ones with an obvious default | `animations.json` is expected to exist; when `delivery.speaker_notes`/narration is also enabled, this is the tier that benefits from `narration_animations.json` (see `generate-audio.md`) |

## Rules that apply at every tier above `none`

- **Semantic anchors before sidecar** (`animations.md` hard rule): never invent reveal order
  from page structure alone — derive it from page meaning and, when present,
  `notes/*.md` / narration.
- **Morph is an authoring decision, not an export flag**: a page pair not authored as a
  continuous action during Step 6 cannot gain Morph later by adding `-t morph` — it silently
  degrades to a cross-fade. Decide Morph while `svg_output/` is still being authored, matching
  the tier's guidance above.
- **Validation is unconditional**: regardless of tier, `animation_config.py validate` MUST
  pass before export — FR-009's "sem referências de âncora inexistentes ou conflitantes" is
  enforced by that command, not by this mapping table.
- **`none` is a hard ceiling, not a default to override**: when `delivery.animations: none`,
  no per-element animation and no page transition may be injected even if a lower-level tool
  default would otherwise add one (`svg_to_pptx.py`'s own default transition is `fade` —
  `none` in `CONTEXT.md` means passing `-t none` explicitly, not omitting the flag).
