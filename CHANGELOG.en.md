# Vudgio · Change Log (English)

> This file records **capability and criteria changes only**: what a version can do, how it differs from the previous one, and whether a threshold changed meaning.
> Internal archaeology (source relationships, brand history, per-date work logs and review process) is kept in an internal file and is not shipped with the package.

## v0.38.0 · 2026-11-23 — Field layering, boundaries, container widths, long tasks

- `build-recipes.md` form section gains "Field layering: show only what must be filled now": layer by frequency rather than by required-ness; collapsed ≠ hidden (entry visible with the default written out); conditional rows appear on a choice and vanish when the choice reverts; one level only. Acceptance adds: submit on defaults without opening "More options", no gaps or dead grey blocks after reverting, entry still whole at 375px width and 200% font size.
- `build-recipes.md` popovers: follow the trigger with CSS anchor positioning (`position-anchor` / `anchor()` / `position-try-fallbacks`), ⛔ no scroll-listener coordinate math (it lags a frame and visibly shakes while scrolling); unsupported browsers fall back to native `popover` placement or a one-shot `fixed` value, ⛔ never a permanent scroll listener.
- `layout-and-viewport.md` gains two sections: "Width follows the container, not the window" (`container-type` + `@container`; the test is dragging that container narrow-to-wide and watching it reflow itself, ⛔ window breakpoints as the only answer — desktop workbenches have a fixed window and variable panels) and "When a new feature is usable" (Baseline "newly available" ships on desktop with a fallback, ⛔ experimental features as the main path; three questions before adopting, including what the degraded state looks like).
- `motion.md` adds "Every boundary needs a carrier" after full-page transitions: at least one element must survive and visibly become the next beat, ⛔ plain old-out / new-in replacement; a run of motion must end in stillness (100–200ms starting range, a local convention, not a measured optimum); one camera only, and that third rule is for product films and scroll narratives only.
- `motion.md` performance red lines add "Long tasks" and "The pipeline": >50ms on the main thread is a felt stall — split it or move it to a worker; `width` / `top` trigger layout while `transform` / `opacity` stop at compositing, verified with DevTools purple (layout) and green (paint) markers rather than impressions.
- `workdir.md` "Continuing an old project" gains a three-part work record (goal, where it stands, evidence that can be re-checked) and its division of labour with the design log: the log says why a decision was made, the record says where things stand now.

## v0.36.0 · 2026-11-22 — Translated copy, colour area, evidence anchors

- `type-and-polish.md` gains "Translated copy and long strings": widths follow the text, action bars may wrap, key actions are never truncated, and the order is copy → layout → type size last. New **three-way check**: longest real translation + 375px viewport + 200% font size, with no clipped text, no colliding buttons and no horizontal overflow. ⛔ Never accept the source-language string as the test sample.
- `tokens.md` gains "Colour area": roughly 60 primary / 30 secondary / ≤10 accent; two colours near 1:1 means they are fighting to be primary, fixed by area and lightness, not hue. Measured by block or colour-cluster counts, ⛔ never "it looks a bit busy".
- `review-rubric.md` now requires a traceable anchor per finding (file + line, test name, commit or screenshot name); a finding without one counts as insufficient evidence.
- All three are criteria only; no new volume.

## v0.35.0 · 2026-11-22 — Destructive confirmation and scrubbed values

- New section in `interaction-feel.md`, "Destructive confirmation and scrubbed values", with four criteria: hold-to-fill, slide-to-commit, two channels for scrubbed numbers (drag and type), and swipe-to-delete with a way back (commit past the threshold, spring back below it, offer undo after).
- Two hard lines: release means cancel (leaving means nothing happened; ⛔ never wait a beat after release to catch a second press), and the finished state must settle into a static terminal state (⛔ no breathing, pulsing or sweeping afterwards). These four forms are for low-frequency actions only; high-frequency controls get no "effort" gesture.
- `motion.md`: tooltip warmth is shared per group — the first in a group waits ~300ms, siblings open at once, leaving the group resets it (⛔ never time each one separately).
- `components-motion.md`: states with real duration show progress against real elapsed time, end in a static terminal state, and failures stay failed with a reason.
- Acceptance gains one check: release a destructive gesture halfway and it must return to its place with nothing committed.

## v0.34.4 · 2026-11-20 — Validation timing, criteria corrected

- Field state expanded from four to six: `pristine` / `prefilled` / `editing` / `blurred` / `submitted` / `dirty-after-submit`. `blurred` means "lost focus" only — value emptiness no longer splits the state; empty values are judged by the rule layer.
- "Impossible by construction" values (letters in a phone field, 30 February) are handled as **input constraints**: the characters never enter, so there is no error state to show. Rejection must be reversible and explained; ⛔ never swallow the keystroke silently.
- Three easy-to-miss implementation points: skip IME composition (`compositionstart`→`compositionend`); normalise pasted input (full-width, separators, country code) before judging; async validation needs all four — cancel the previous request, compare the response against the **current** value, never treat a failed request as valid, settle before submit.
- Six acceptance items, including IME input and offline.

## v0.34.3 · 2026-11-20 — New volume: validation timing

- Added `references/validation-timing.md`: **when** to raise an error and when to clear it. Format errors on blur, required on blur, cross-field conflicts on the later field, and a full list on submit with focus moved to the first.
- Errors clear per keystroke on that field only. Async validation starts at 400–600ms, with sequence numbers plus cancellation.

## v0.34.2 · 2026-11-20 — Waiver path for the ambiguous hue band

- When a primary colour and a semantic colour fall inside the 15–40° band, a waiver can be registered: rationale ≥20 characters covering at least two of area / shape / position; the pair then reports `✓` with "N further pairs released by axis change", ⛔ never silently.
- A waiver that matches nothing is reported as a stale waiver. Unregistered pairs still warn.

## v0.34.1 · 2026-11-20 — Hue cap semantics fixed

- 20° is a **per-side endpoint budget** (total travel from lightest to 500), not "5° per step". Reading it as 5°/step cuts compensation by about 90% and collapses the ramp into one hue at different lightness.
- Two fold-point acceptance tests: the endpoint equals `min(natural endpoint, 20)` and the curve bends exactly once at 20; the total span equals `min(natural span, 30)` with one shared coefficient.

## v0.34.0 · 2026-11-20 — Hue capping becomes per-side proportional

- `hue_offset` returns the natural offset only; `ramp_offsets` applies two gates — per-side scaling to `--cap`, then whole-ramp scaling to `--cap-total`. Proportional scaling is order-independent and stable across base colours.
- New "hue stall" criterion: adjacent steps on the same side differing by less than 1° fail.

## v0.33.0 · 2026-11-20 — Hue rotation split into two meanings; palette gate

- Hue rotation now has two distinct meanings — single-side endpoint and adjacent step — ⛔ never one number for both.
- Added `scripts/audit_palette.py` with tests: contrast, cumulative hue travel and hue stall judged together; exit code usable as a delivery gate.

## 2026-11-20 — Focus visibility; hover vs. focus

- Focus must be visible (WCAG 2.4.7). ⛔ Never remove the focus ring for looks — that filters out keyboard and limited-mobility users.
- Hover is for pointers, focus is for keyboards; they do not substitute for each other. Touch paths are covered by focus or a menu. State checklists gained `:focus-visible`.

## 2026-11-18 — Five volumes rewritten

- Materials, style explorer, workdir, motion and visual language were rewritten in structure and wording; criteria and numbers untouched; shared lines dropped below 10%. Cross-references and `references/index.md` synced.

## 2026-11-18 — Squircle path script

- Added `scripts/squircle_path.mjs`: emits G2 corner paths for `clip-path` or SVG, with radius and smoothness computed from actual pixel size. Samples densely per corner, then respaces by arc length so points do not crowd at 45°.
- Two unusable approaches are documented: the `blur+contrast` glue filter blurs content; `mask: paint()` filling black does not clip.

## 2026-11-18 — Exit-code contract and shared layer

- Six CLI entries follow one rule: `0` pass, `1` criterion failed, `2` usage or input error. Runtime failures stay `1`.
- The three `.mjs` tools share `scripts/_cli.mjs` (exit constants, usage error, unified failure mapping); argument parsing stays per tool.

## 2026-11-18 — Light path, follow-up menu, convention conflict

- Added `references/light-path.md` for ordinary one-pager work: a six-line preamble confirmed once, batched screenshots, one review round, five delivery items.
- Delivery may end with 1–3 optional next steps, the first marked "recommended"; skipped for small edits, confirmation stops, and unattended runs.
- When a project already ships `DESIGN.md` or similar conventions, follow the project; state any conflict with these criteria in the delivery note.

## 2026-11-18 — Skeleton, naming and declaration cleanup

- Entry gained a "counter-examples (read first)" block of five, a "when to use / not use" pair, and a criteria ledger mapping tests to hard criteria.
- The volume index moved to `references/index.md` (seven groups); the main file keeps three common entry points.
- Scripts renamed to snake_case, verb + object: `take_shots.mjs`, `chrome_launcher.mjs`, `curate_media.mjs`, `prep_image.mjs`, `clip_audit.js`.

## v0.31.0 · 2026-11-14 — Architecture upgrade: end-to-end design contractor

- Scope widened from design judgement to end-to-end design work: pages, components, motion, design assets; no business logic, APIs or data layers.
- Seven-step flow, 13 Chinese commands, four page types (persuade / operate / read / experience).
- Seven new volumes: `routing`, `craft-floor`, `tokens`, `build-recipes`, `type-and-polish`, `interaction-feel`, `review-rubric`.
- Added `check_contrast.py` (WCAG 4.5 / 3.0 plus perceptual luminance) and `emit_tokens.py` (ramp, saturation compensation, hue cap, grey temperature; writes tokens.css / theme.css / tokens.json / DESIGN.md).

## Rollback and recovery

A cold snapshot is the rollback point; the goal is to restore the one broken file, not the whole directory.

1. Confirm the latest snapshot is usable before editing.
2. For a single broken file, restore **that file**. ⛔ Never overwrite the whole directory — it takes later criteria with it.
3. After restoring, run the suite: `cd tests && python3 -m unittest $(ls test_*.py | sed 's/.py//' | tr '\n' ' ') -q` (the list on disk is authoritative; ⛔ never paste an old string).
4. When two statements conflict, keep the one that explains why. If neither does, delete both.

## Boundaries

- ⛔ No whole-directory restore; `diff` before restoring.
- ⛔ No auto-updater that pulls a new version and overwrites the directory in place, and no scheduled job for one.
- ⛔ This file is not the version source; `version` in `SKILL.md` is.
