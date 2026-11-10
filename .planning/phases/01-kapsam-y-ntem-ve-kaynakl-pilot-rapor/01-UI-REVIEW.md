# Phase 1 — UI Review

**Audited:** 2026-11-10  
**Baseline:** Abstract six-pillar standards and locked decisions in 01-CONTEXT.md; no UI-SPEC exists.  
**Release:** `6fd06aa1a6c643ed99b2b1c95f32822d`  
**Screenshots:** Not captured; no server responded on ports 3000, 5173 or 8080. Code-only review; no visual or human accessibility assessment is claimed.

## Pillar Scores

| Pillar | Score | Key finding |
|--------|-------|-------------|
| Copywriting | 2/4 | Internal English status codes and identifiers reach Turkish readers. |
| Visuals | 2/4 | The page title describes only establishment although the page contains a full research report. |
| Color | 3/4 | Required text colors are implemented; rendered contrast and color distribution were not visually tested. |
| Typography | 3/4 | Browser defaults supply hierarchy, but no explicit reading measure or line-height is defined. |
| Spacing | 2/4 | The 70em maximum and default spacing leave long lines and dense repeated records. |
| Experience Design | 2/4 | Missing viewport metadata risks a desktop-scaled layout on actual mobile browsers. |

**Overall: 14/24**

## Top 3 Priority Fixes

1. **Add mobile viewport metadata** — phones may scale the desktop-width page down despite wrapping rules — add `<meta name="viewport" content="width=device-width, initial-scale=1">` and inspect on an actual narrow browser.
2. **Translate reader-facing internal codes** — values such as `eligible` and actor kinds interrupt Turkish reading and obscure meaning — map each status and actor value to a clear Turkish label while preserving the underlying data.
3. **Give the report a truthful heading and readable structure** — the current heading suggests only establishment, and dense repeated records are hard to scan — use a report-wide heading, restrained section spacing and a narrower text measure while retaining every source and finding.

## Detailed Findings

### Pillar 1: Copywriting (2/4)

- **WARNING:** The match and candidate output inserts raw `eligibility`, actor `kind`, candidate `status`, IDs and topic IDs into visible text (`src/rapor.py:125`, `:131`); the released HTML contains 54 occurrences of `eligible`. Translate reader-facing values and avoid exposing technical IDs as primary labels.
- **WARNING:** Repeated `[Kaynak]` links provide little context when links are listed independently by assistive technology (`src/rapor.py:97`, `:114`). Give each an accessible name incorporating the source or claim, retaining concise visible copy.
- **Evidence:** Turkish missing-information labels, “Henüz incelenmedi” and the overlapping-match caveat are present (`src/rapor.py:105`, `:111`, `:152`, `:189`). Financial `None` is rendered as “Bilinmiyor” (`:136`); that branch is not present in this release, so its visual presentation was not checked.

### Pillar 2: Visuals (2/4)

- **WARNING:** `Yeni Parti: kuruluş bilgisi` remains the sole H1 even when another party or comparison is selected (`src/rapor.py:18`, `:84`–`:89`), misrepresenting the scope and selected context. Use an overall report title and identify the selected panel with an appropriate heading.
- **WARNING:** Findings, match records, missing states and source entries rely chiefly on unstyled paragraphs and browser defaults (`src/rapor.py:91`–`:106`, `:111`–`:125`, `:176`–`:182`), making their hierarchy difficult to assess from code. Add modest structural differentiation and inspect it visually.
- **Evidence:** Ten tab controls are generated in the release: nine party tabs and one comparison tab. Source details include the passage, original link and local archive (`src/rapor.py:84`–`:88`, `:176`–`:181`).

### Pillar 3: Color (3/4)

- **WARNING:** The palette uses hard-coded values in one inline CSS rule (`src/rapor.py:17`), with no explicit background or color-scheme control. Verify text and focus contrast under supported browser and system themes; centralize colors if the design grows. No screenshot exists to establish a 60/30/10 distribution.
- **Evidence:** Summary text is `#003366`, quotes are black, and real curly quotation marks surround quotes (`src/rapor.py:17`, `:95`–`:102`, `:118`–`:122`). Provenance remains in attributes; no visible production-type labels are added by these paths. Semantic labels such as “Beyan” remain distinct as required.

### Pillar 4: Typography (3/4)

- **WARNING:** The sole font declaration is generic `sans-serif`; no line-height or intentional type scale is specified (`src/rapor.py:17`). Establish a comfortable body line-height and test Turkish glyphs and headings at browser zoom. Browser defaults provide heading hierarchy, but actual readability requires human inspection.
- **Evidence:** No Tailwind typography classes are used; HTML H1/H2/H3 and paragraph defaults form the current scale (`src/rapor.py:18`, `:90`–`:91`, `:125`).

### Pillar 5: Spacing (2/4)

- **WARNING:** The only explicit layout spacing is `padding:1em` and tab `gap:.3em`, with `max-width:70em` on the entire body (`src/rapor.py:17`). Long prose can span a broad measure, while repeated findings and sources receive no designed separation. Constrain prose width separately and add consistent section/record spacing.
- **WARNING:** Ten long party controls wrap with a small gap (`src/rapor.py:17`, `:84`–`:88`); actual touch target size and wrapped order need narrow-screen inspection. There is no declared spacing scale to compare against.

### Pillar 6: Experience Design (2/4)

- **WARNING:** The document head lacks viewport metadata (`src/rapor.py:16`–`:17`; released HTML lines 1–2). The existing 360px headless window check in `tests/browser_probe.py` does not establish real mobile viewport scaling or human readability. Add viewport metadata and verify on a mobile device or emulation with mobile viewport behavior.
- **WARNING:** The scope link targets a closed `<details>` element (`src/rapor.py:21`); the custom hash handler only explicitly opens `source-` targets (`:201`). Browser behavior for revealing the scope and links to attempts inside it should be checked across supported browsers, and the handler should explicitly reveal the destination if needed.
- **Evidence:** Tab selection, arrow/Home/End keyboard handling, source opening and focus restoration are implemented (`src/rapor.py:196`–`:203`). The supplied browser probe checks click, keyboard, source opening, history/focus and horizontal overflow in a 360px window; this audit did not repeat the suite. The static report has no asynchronous loading, destructive action, or editable submission requiring corresponding states.
- **Limit:** Source accuracy, neutrality, semantic equivalence of quotations and summaries, actual accessibility and human review remain pending; implementation and prior automated tests cannot establish them.

## Files Audited

- `data/current.json` and `data/releases/6fd06aa1a6c643ed99b2b1c95f32822d/index.html`
- `src/rapor.py`, `tests/browser_probe.py`, `README.md`, `AGENTS.md`
- `01-CONTEXT.md` and phase 01 plans and summaries (01–06)

## Kapanış kaydı — 2026-11-10T19:55:29.442929+00:00

Bu tarihsel görsel audit 6fd06aa1 sürümüne ve yalnız kod incelemesine aittir; puanı sonradan yükseltilmedi. `01-UI-FIX.md` yeni renderer 7 düzeltmelerini ve Chromium kanıtlarını açıklar. Kullanıcı mevcut raporun sekiz UAT kontrolünü topluca kabul etti; bu kayıt yeni mobil cihaz veya bağımsız görsel test iddiası değildir.
