# Wave issues: ledgertax-web

Accounting export, not tax advice.

Drafts of the contributor issues for this repository. Each one is inside the MVP boundary described in `PLAYBOOK.md` section 12: the feature does **not** exist yet (checked against the code on 2026-11-07), and the marker named in each issue exists in the code. Complexity maps to points: Trivial = 100, Medium = 150, High = 200.

Before starting any of them: read `CONTRIBUTING.md` and `README.md`, and run `pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm test && pnpm build`. A running `ledgertax-api` is useful for trying changes by hand.

---

## web-1: Bulk relabel

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(web-1)` (`components/EventsView.tsx`)

**Background.** Labels are set one event at a time. A history with hundreds of payments needs a faster way.

**Acceptance criteria**
- The user can select several events (checkboxes with accessible names, a "select all shown" control that respects the type filter, keyboard operable) and apply one label to all of them, or clear their labels.
- Only labels that fit every selected event are offered (the existing `labelChoices` rules); mixed selections say why a label is not available.
- Changes go through the existing `LabelStore` (browser only) and work without storage.
- The state is announced to screen readers (for example "12 events selected", "label applied to 12 events") through a live region.
- Tests: the happy path (select several, apply, labels shown and stored) and failure paths (mixed event kinds, nothing selected, storage unavailable).

**Files to touch:** `components/EventsView.tsx`, `components/Workbench.tsx`, `lib/label-choices.ts`, `lib/labels-store.ts` (if needed), `test/`.

---

## web-2: Report preview with totals by year

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(web-2)` (`components/ReportView.tsx`)

**Background.** The report shows a plain gains table and one overall total. People file by year, so totals per year (and per asset) are needed before downloading.

**Acceptance criteria**
- A summary table with, per calendar year of the disposal date (UTC): the number of rows, proceeds, cost and gain, plus a clearly separate line for the rows that could not be calculated in that year.
- Sums are computed without floating point (parse the API's decimal strings with integers or BigInt) and match the totals in `gains.csv`; a test proves it on a fixture report, including negative gains and a year with only error rows.
- The preview states that error rows are not in the totals, and carries "Accounting export, not tax advice."
- Keyboard and screen-reader friendly (captioned table, scoped headers); colours from the CSS variables only.
- Empty and error states are unchanged or better.

**Files to touch:** `components/ReportView.tsx` (or a new component), `lib/` (a small summing helper), `test/`.

---

## web-3: Improve empty and error states

**Complexity:** Trivial (100)  **Marker:** none

**Background.** Basic loading, empty and error states exist for every view, but the wording is generic.

**Acceptance criteria**
- Each API error code (`openapi/openapi.yaml`) maps to a plain-language message with a suggested next step (for example `history_too_large`: narrow the range; `account_not_found`: check the address and the network).
- The empty state for an address explains the likely reasons (new account, history older than the server keeps) and the error state never shows raw technical text.
- No behaviour or layout regressions: existing tests pass; add a test per mapped error code.

**Files to touch:** `lib/api.ts` or a new `lib/messages.ts`, `components/EventsView.tsx`, `components/PricesPanel.tsx`, `test/`.

---

## web-4: Accessibility audit and fixes

**Complexity:** Medium (150)  **Marker:** none

**Background.** The app has automated checks (accessible names, tab order attributes, contrast of the tokens) and a Tab-key check in one browser, but no complete audit by a person using a keyboard and a screen reader.

**Acceptance criteria**
- A written audit (`docs/ACCESSIBILITY.md`) of the whole flow with a keyboard only and with at least one screen reader (name it and its version), listing each finding with its severity, the WCAG criterion and whether it was fixed.
- Fixes for the findings, with tests where a test can catch a regression.
- Focus management is checked after each state change (loading finished, error shown, report ready); fix where focus is lost.
- Text zoom to 200 % and a narrow phone width are checked and any breakage fixed.
- The audit states honestly what was not tested.

**Files to touch:** `components/`, `app/globals.css`, `test/a11y.test.tsx`, `docs/ACCESSIBILITY.md` (new).
