# Vudgio · Change Log (English)

> This is a human-readable ledger of changes, kept for future maintainers and agents.
> Dates, commands, thresholds and check readings are kept verbatim from the Chinese original ([CHANGELOG.md](CHANGELOG.md)); if the two disagree, the Chinese ledger wins.

## 2026-11-20 · Focus visibility; hover vs. focus split (button-state audit)

- Split hover and focus-visible responsibilities so keyboard focus is never signalled by hover styling alone.
- `reviewer-manual` and `acceptance` gained a focus-visibility check; the three-state verdict (pass / fail / insufficient evidence) is unchanged.

## 2026-11-18 · Five volumes rewritten: expression fully localised

- Reason: a line-by-line comparison against an archived external reference showed five volumes still shared substantial wording (materials 100%, style-explorer 97%, workdir 71%, motion 71%, visual-language 68%). Krat rule: criteria stay verbatim, expression is replaced wholesale.
- Method: structure and order may change; numbers and commands do not. Headings renamed to this repo's plain speech (with `references/index.md` and cross-links synced); example blocks and table wording rewritten. No criterion deleted, no threshold changed.
- Reading: offline checks all green; `check_limits.py` within bounds.

## 2026-11-18 · Squircle path script (`squircle_path.mjs`)

- Generates superellipse (G2) corner paths; radius and smoothness are computed live from pixel size.
- Explains why two approaches are unusable: glue-filter blur and `mask: paint()` filling black.

## 2026-11-18 · Exit-code contract, shared layer, copy rewrite

- All six CLI entries follow one rule: `0` pass, `1` criterion failed, `2` usage/input error.
- The three `.mjs` tools share `scripts/_cli.mjs` (`EXIT` / `usageError` / `runMain`); argument parsing stays per-tool.

## 2026-11-18 · Three external pickups (light path, follow-up menu, convention conflict)

- Added the light path (six-line preamble + screenshot-driven edits + one review round + five delivery items).
- Added the optional follow-up menu at delivery time; added the "project already has design conventions — surface the conflict" rule.

## 2026-11-18 · Skeleton, naming and declaration cleanup

- Method axis settled as constraint satisfaction; volume index regrouped by constraint lifecycle.
- Local absolute paths removed from `sources.md`; brand prefix in process identifiers unified to `VUDGIO_*` / `vudgio-*`.

## 2026-11-14 · Architecture v0.31.0 (end-to-end design contractor)

- Four modes, 13 commands, seven-step flow, delivery gate, 58-volume index.

### Addendum · 2026-11-14, third wave (extractive merge + two towers)

- New gate: land `DESIGN.md` (five elements) before step 4; later pages only reference it.
- Two disciplines: a checkable acceptance sentence in the constraint brief; three-state review verdict plus a "what this round did not cover" section (from Quojuta and Huagai).

## I. Why self-maintained, and why not git-tracked here

This directory is maintained locally as its own project and does not follow any upstream version. Cold snapshots go through `snapshot` (mode-skill). Historical directory names are normalised to the current `.vudgio`; original wording lives in cold snapshots for archaeology.

## II. What was changed locally

Local volumes for mobile, B2B, chat interfaces, materials and media were added; vendor sales copy and "full version" recommendation machinery were removed. See [CHANGELOG.md](CHANGELOG.md) for the full per-date ledger with readings.

## III. Rollback and recovery

Restore from the `snapshot` cold archive; do not hand-edit a published `index.html`. Rebuild the product from `index.src.html` before publishing.

## IV. What not to do

Do not run production builds or full test suites as a routine gate; do not let environment noise (auth failures, 404s) block a UI change; do not silently skip the six-state / six-check delivery gate.
