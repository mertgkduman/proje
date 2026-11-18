## Deferred Items

- Preserve the renderer 25 producer and its assets before extending the report for additional practice cases in 04-02, so the 04-01 immutable tracer remains reproducible.
  status: resolved
  Renderer 25 was frozen as `src/rapor_v25.py`; its CSS24 remains unchanged. The active renderer now uses version 26.
- Before 04-02 changes the active renderer, freeze the then-current renderer 26 and preserve its CSS and dispatch, with byte-reproduction coverage; retain the historical 16 and 24 stylesheet checks.
  status: open
- Replace the Çeşme-specific missing-result wording when 04-02 renders other event types; do not imply their results concern a congress.
  status: open
- Extend the tracer contribution validator in 04-02 to represent individually sourced MP activity as individual activity, without treating it as the party's institutional position.
  status: open
- The pre-existing `test_new_stylesheet_preserves_historical_style` expects `rapor_v16.css` although the baseline renderer already uses `rapor_v24.css`; the required comparison regression therefore fails before this plan's changes.
  status: resolved
  Resolved in 7d9ba91: the regression separately checks the frozen renderer 16 and 24 producers and styles, and the current renderer 25 style.
