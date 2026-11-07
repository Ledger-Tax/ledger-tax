# PLAYBOOK — Stellar Ledger Tax

Read `AGENTS.md` first. Work phases in order, and tasks in order within a phase. A task is done only when its **Done when** holds AND the package check command passes. Update `STATUS.md` after every task.

## 1. Goal and non-goals

**Goal:** a user enters one Stellar address and gets (1) a list of classified events, (2) FIFO realised gains using prices they supply, and (3) CSV downloads, with the ability to relabel any event. Everything is read-only.

**MVP non-goals** (these are the Wave issues, section 12): Soroban contract events, liquidity-pool operations, multiple linked addresses, other cost-basis methods, an external price source, extra export formats.

**Success for the whole project:** on a real address the user owns (or a prepared testnet account), the web app shows classified events with nothing silently dropped, the gains CSV matches a hand-calculated spreadsheet for a small fixture, and every report states "Accounting export, not tax advice."

## 2. Research first (Phase 0, task 0.1)

Write findings, with source links and the date checked, to `docs/RESEARCH.md`. Answer each; assume nothing.

1. **History source (the feasibility question).** What can return the FULL operation and trade history for an arbitrary mainnet account today, for free or at what cost? Check: Horizon's current status and deprecation timeline; Stellar RPC retention (short); public data sets or archives (for example the Stellar public data lake or Hubble); third-party indexers. Record rate limits, pagination and ordering guarantees, and licensing.
2. The exact record shapes returned for: payment, path payment strict send/receive, create account, account merge, manage buy/sell offer, create passive sell offer, change trust, claimable balance create/claim, liquidity pool deposit/withdraw, clawback, set options (home domain), invoke host function. Note which fields give amounts, assets, counterparties, memo and the fee charged.
3. Effects versus operations: which gives reliable amounts for trades and path payments (effects show what actually moved).
4. `@stellar/stellar-sdk`: current version and which client classes exist for the sources found in item 1.
5. Asset decimals: classic assets use 7 decimals; how Soroban token decimals are read.
6. Fees: how the transaction fee is attributed (paid by the source account, fee bumps, sponsored).
7. Decimal handling choice for fiat math (bigint scaled integers versus a small library) and which is allowed.
8. CSV: injection characters and a correct quoting approach.
9. Next.js: current stable major, App Router conventions. OpenAPI-to-TypeScript generator options.

**CHECKPOINT 0 (self-review, no pause).** Write into `STATUS.md`: which history source(s) work, their limits and cost, and whether the scope is feasible. Choose the source yourself (a configurable Horizon base URL is a good default so users can point at a full-history provider) and state the covered range in every report. If no workable source exists, take the reduced scope (for example "last N days" or "bring your own Horizon URL"), log it, and continue. Decide D2 yourself: until core is published, the api uses a `pnpm pack` tarball of core committed inside the api; switch to a semver range at publication.

## 3. Allowed dependencies

Prefer this list. Other dependencies are allowed when needed; follow "Working autonomously" in AGENTS.md and log them in `STATUS.md`.

- **All TypeScript packages:** `typescript`, `vitest`, `eslint` + `typescript-eslint`, `prettier`, `zod`.
- **core:** `@stellar/stellar-sdk`, `tsup` for the dual ESM/CJS build.
- **api:** `ledgertax-core` (per D2), `fastify`, SQLite through Node's built-in `node:sqlite` if stable in the installed Node, else `better-sqlite3` (cache of public history only). Write the CSV writer yourself (needed for injection safety).
- **web:** `next`, `react`, `react-dom`, `@testing-library/react`, `jsdom`, one OpenAPI-to-types generator chosen in research.

## 4. Data model (propose in Phase 1, user signs off)

Amounts are `bigint` in the asset's smallest unit with `decimals` stored beside them. Times are UTC ISO strings plus ledger sequence.

```ts
type AssetId = string; // "native" | "CODE:ISSUER" | "C...contract" (final form decided in research)

type EventType =
  | 'payment_in' | 'payment_out'          // movement of an asset to/from a watched address
  | 'trade'                               // an exchange of one asset for another (offers, path payments)
  | 'fee'                                 // network fee paid by a watched address
  | 'account_funded' | 'account_merged'   // create account, merge
  | 'claimable_claimed'                   // claimable balance claimed
  | 'unknown';                            // anything not understood; never dropped

interface LedgerEvent {
  id: string;                 // stable: `${txHash}:${opIndex}:${leg}`
  txHash: string;
  opIndex: number;
  ledger: number;
  time: string;               // UTC ISO
  type: EventType;
  address: string;            // the watched address this event belongs to
  asset?: AssetId; amount?: bigint; decimals?: number;
  counterAsset?: AssetId; counterAmount?: bigint; counterDecimals?: number; // for trade
  counterparty?: string;
  memo?: string;              // untrusted text
  raw: { source: string; ref: string };   // pointer back to the source record
}

interface Label { eventId: string; label: 'income' | 'disposal' | 'transfer' | 'gift' | 'ignore'; note?: string }

interface HistorySource {
  name: string;
  fetch(address: string, opts: { cursor?: string; limit?: number; since?: string }): AsyncIterable<RawRecord>;
}
```

Public functions of core (names are proposals until checkpoint 1):
`classifyRecord(record, ctx) -> LedgerEvent[]`, `classifyAccount(source, address, opts) -> AsyncIterable<LedgerEvent>`, `isLikelySecretKey(input) -> boolean`, `parseStellarAddress(input) -> Result`.

Rules: a record produces zero or more events, never silently none. Unknown operations produce `unknown`. Fees are separate `fee` events. Labels overlay events and never mutate them.

Cost basis (api): per-asset lots in time order. A `trade` disposes of the sold asset and acquires the bought asset. A `Label` of `disposal` makes a `payment_out` a disposal; `income` makes a `payment_in` an acquisition at the supplied price; `transfer`/`ignore` creates no gain. Prices come from the user CSV (columns: `asset,date,price,currency`). Missing price for a needed date is an error row in the report, not a guess.

Reports: `events.csv` (all events with labels) and `gains.csv` (acquired date, disposed date, asset, quantity, proceeds, cost basis, gain, holding days, currency, event ids). Both start with a comment line "Accounting export, not tax advice."

## Phase 0: Bootstrap

**0.1 Toolchain + research.** Re-check `STATUS.md`'s table (`git --version`, `node --version`, `pnpm --version` in a NEW terminal). If pnpm is missing, try `corepack enable`; if that fails with a permission error use `npm i -g pnpm`; if that also fails use `npx pnpm`. Confirm with `pnpm --version`. Write `docs/RESEARCH.md` (section 2). *Done when:* all 9 items answered with links, STATUS environment table updated. Then checkpoint 0.

**0.2 Repo + skeleton.** `git init` in this folder (new repo, no history to touch). Create the three folders with a minimal buildable skeleton each, a per-package `README.md` (what it is, "Accounting export, not tax advice", how to check), `LICENSE` (MIT unless the user says otherwise), `.env.example` where needed, and a per-package CI workflow `.github/workflows/<package>.yml` that runs that package's checks only when its folder changes.
*Done when:* each package's check command passes on its skeleton, each has its own lockfile. *Commits:* one per package, root files `chore(meta)`.

## Phase 1: Core (`ledgertax-core`)

**1.1 Input safety.** `parseStellarAddress`, `isLikelySecretKey`. *Done when:* tests for valid public key, muxed address (if supported per research), garbage, and a secret-key-shaped string (rejected and never echoed in the error message).

**1.2 Types and source interface.** Implement section 4's types and the `HistorySource` interface; add a `FixtureSource` that reads recorded records from disk for tests. *Done when:* typechecks, fixture source tested.

**1.3 Fixtures.** Create testnet accounts (public keys only recorded), perform each operation type once (script the steps in `docs/FIXTURES.md`; never print secrets), record the source responses into `test/fixtures/`. Where an operation type cannot be produced on testnet, build a synthetic record shaped like the documented one and mark it `synthetic` in its filename. *Done when:* a fixture exists for every type in the MVP list plus `unknown`.

**1.4 Classifiers, one per operation family.** Payments (in/out, self-payment), create account/merge, path payments (both directions), manage offers (filled amounts from trades/effects), claimable balance claim, fees. Everything else becomes `unknown`. Mark `// WAVE-ISSUE(core-1)` at the liquidity-pool branch, `// WAVE-ISSUE(core-2)` at the invoke-host-function branch.
*Done when:* a test per family from its fixture (happy path) plus: operation in a failed transaction (no events except the fee), unknown operation type, missing field in a record (typed error, no crash), duplicate record (idempotent ids).

**1.5 `classifyAccount`.** Streams through the source, handles pagination and resume cursor, never loads the whole history in memory. Mark `// WAVE-ISSUE(core-3)` where multi-address support plugs in. *Done when:* tests with a multi-page fixture source, a source that errors mid-stream (error surfaces with the cursor so the caller can resume), and an empty account.

**1.6 Docs and package.** `docs/CLASSIFICATION.md`: each event type, which operations produce it, what is NOT classified. README with install and usage. Dual ESM/CJS build verified by a test that imports both.
*Done when:* the full check passes.

**CHECKPOINT 1 (self-review, no pause).** Record the final data model, `docs/CLASSIFICATION.md` and the check output in `STATUS.md`, then continue to Phase 2. Later phases may change event types or report columns if they prove it necessary: update every consumer, test and doc together and log the decision.

## Phase 2: API (`ledgertax-api`)

**2.1 Bring in core** per decision D2 (semver range, or the committed tarball). Document how to refresh it. *Done when:* the package builds standalone from a clean clone.

**2.2 Money and prices.** Scaled-integer decimal helper per research item 7. Price CSV parser with strict validation (header, dates, decimals, currency), returning row-numbered errors. *Done when:* tests for valid file, bad header, bad date, negative price, duplicate rows, huge file rejected by size limit.

**2.3 Cost basis (FIFO).** Lots per asset, partial lot consumption, trades, labels per section 4. Mark `// WAVE-ISSUE(api-1)` where other methods plug in. *Done when:* tests against a hand-calculated example kept in `docs/EXAMPLE.md` (full partial-lot case, a loss, a zero-cost income lot, disposal exceeding held quantity reported as an error row, missing price reported).

**2.4 Report writers.** `events.csv` and `gains.csv` with the disclaimer line, correct quoting, formula-injection neutralization. Mark `// WAVE-ISSUE(api-2)` at the export-format registry. *Done when:* tests with memos beginning `=`, `+`, `-`, `@`, quotes, commas, newlines, and unicode.

**2.5 History cache (public data only).** SQLite cache of raw history per address and source with a cursor. No labels, no prices. Behind a store interface. Mark `// WAVE-ISSUE(api-3)` for another store. *Done when:* tests for resume after restart, and a test proving that no label or price data is written.

**2.6 HTTP API.** `POST /reports` (address, optional price CSV, optional labels, method, currency), `GET /events?address=`, `GET /health`. Reject secret-key-shaped input, validate everything, enforce body size and history limits, rate limiting per IP, typed error responses, CORS configurable. Streaming or job-based response for long histories (choose in the design, document it). Write `openapi.yaml`. Mark `// WAVE-ISSUE(api-4)` at the price-source adapter point.
*Done when:* endpoint tests for success, invalid address, secret-key-shaped input, oversize body, source failure mid-stream.

**2.7 Docs.** README: run it, env vars, limits, privacy behavior, what is not covered. Checks pass.

## Phase 3: Web (`ledgertax-web`)

**3.1 Skeleton + tokens.** Next.js App Router, CSS-variable theme (light and dark), layout, a typed client for the api generated from `openapi.yaml` and committed. Api URL from env.
**3.2 Address entry.** One address field with inline validation; secret-key-shaped input shows a plain-language warning and is never sent or stored; a visible disclaimer.
**3.3 Events view.** Table with loading, empty and error states, progress for long histories, filter by type, `unknown` events visibly flagged.
**3.4 Labels.** Relabel an event (income, disposal, transfer, gift, ignore) with keyboard support; labels stored only in the browser (localStorage or IndexedDB, wrapped in try/catch, app works without it). Mark `// WAVE-ISSUE(web-1)` where bulk relabel plugs in.
**3.5 Prices and reports.** Upload a price CSV (validated, row errors shown), choose currency, generate the report, download the two CSVs, preview of the gains table. Mark `// WAVE-ISSUE(web-2)` at the report preview.
**3.6 Quality.** Keyboard-only walkthrough, labels on every control, contrast from tokens, component tests for the address form and label flow.
*Done when (each task):* tests for the happy path and an error path; checks pass. *Phase done when:* a manual walkthrough against the real api is recorded in `docs/DEMO.md`.

## Phase 4: Integration and honesty

**4.1 End-to-end run** with a testnet fixture account and then, if the user has listed a public address in `docs/USER_INPUT.md`, with that address too (skip this if the file does not exist). Compare `gains.csv` to a spreadsheet calculation of the same small history and record the match.
**4.2 `docs/DEMO.md`** with steps, screenshots without personal data, and known issues.
**4.3 Honesty pass.** Re-read every README and report header against what is actually tested; remove anything aspirational. Confirm the disclaimer is in each README and each CSV.

**CHECKPOINT 2 (self-review, no pause).** Confirm the demo passed, list known issues in `docs/DEMO.md`, and continue.

## Phase 5: Wave readiness

For each of the three packages:
- `CONTRIBUTING.md` (setup, check command, commit style, how to claim an issue), `SECURITY.md` (how to report, the read-only guarantee), issue templates, PR template, `CODE_OF_CONDUCT.md`.
- Draft the issues from section 12 into `docs/wave-issues/<package>.md`: title, background, acceptance criteria, files to touch, the `WAVE-ISSUE(...)` marker to search for, complexity. Confirm every marker exists (`git grep "WAVE-ISSUE"`) and that each issue's feature does NOT already exist.
- Architecture diagram in the root README.

Then write `docs/WAVE_APPLICATION.md`: a checklist for the user (you do not apply yourself): README, passing CI, license, 4–6 scoped issues, clear scope per repo. Remind the user that a rejected repo cannot be re-applied, and that application limits may apply per cycle.

## Phase 6: Release (prepare everything, then hand over)

Publishing and deploying need the user's accounts, so prepare all of it and stop at the hand-over.

**6.1 Publish-ready.** For core (and the api if useful): correct `package.json` metadata, `files`, license, `exports`; `pnpm pack` and `npm publish --dry-run` pass; a changelog; the README install section. Switch the api from the tarball to a semver range only once core is really published.
**6.2 Deploy-ready.** Container-free deployment instructions for the api and web app for a host the user can pick (document env vars, rate limits, cache location, costs); production build verified locally; health checks.
**6.3 Hand-over.** Write `docs/USER_ACTIONS.md`: choose the npm scope and package name and run `npm login`, the exact publish commands in order, the hosting account steps and env vars to set, optional price-provider keys (not needed for the MVP), and the sentence to tell the agent when ready ("publish and deploy"). Then stop with a short summary.
**After the user says go:** publish in order, switch the api to the semver range, redeploy, update every README's status to what is true. Do not ask at each step; stop and report if something fails.

## 11. Definition of done (every task)
1. Acceptance criteria met. 2. Package check command passes (paste the summary). 3. No secrets committed, no personal data in fixtures. 4. Docs match behavior and carry the disclaimer. 5. `STATUS.md` updated. 6. One package per commit, Conventional Commits.

## 12. Wave issues (build up to the boundary, not past it)

Complexity maps to Wave points: Trivial = 100, Medium = 150, High = 200.

### ledgertax-core
| ID | Complexity | Issue | Boundary: the MVP has | Marker |
|---|---|---|---|---|
| core-1 | Medium | Liquidity-pool deposit/withdraw classifier | Becomes `unknown` | `WAVE-ISSUE(core-1)` |
| core-2 | High | Soroban invoke-host-function events | Becomes `unknown` | `WAVE-ISSUE(core-2)` |
| core-3 | Medium | Multiple linked addresses (own-wallet transfers are not trades) | One address | `WAVE-ISSUE(core-3)` |
| core-4 | Trivial | Fixture library from more testnet accounts | One fixture per type | n/a (tests) |
| core-5 | Medium | A second `HistorySource` adapter | One source | `WAVE-ISSUE(core-5)` |

### ledgertax-api
| ID | Complexity | Issue | Boundary | Marker |
|---|---|---|---|---|
| api-1 | Medium | LIFO and average-cost methods | FIFO only | `WAVE-ISSUE(api-1)` |
| api-2 | Medium | Another export format | Two generic CSVs | `WAVE-ISSUE(api-2)` |
| api-3 | Medium | Postgres cache store | SQLite behind an interface | `WAVE-ISSUE(api-3)` |
| api-4 | Medium | Price-source adapter (replacing the CSV) | User CSV only | `WAVE-ISSUE(api-4)` |
| api-5 | Trivial | OpenAPI examples and error catalogue | Spec exists, few examples | n/a (docs) |

### ledgertax-web
| ID | Complexity | Issue | Boundary | Marker |
|---|---|---|---|---|
| web-1 | Medium | Bulk relabel | One event at a time | `WAVE-ISSUE(web-1)` |
| web-2 | Medium | Report preview with totals by year | Plain gains table | `WAVE-ISSUE(web-2)` |
| web-3 | Trivial | Improve empty and error states | Basic states exist | n/a |
| web-4 | Medium | Accessibility audit and fixes | One keyboard walkthrough | n/a |

## 13. Risks to state honestly in the docs
- This is not tax advice, and classification can be wrong. `unknown` is shown, never hidden.
- History completeness depends on the data source and its limits. Say which source and range a report used.
- Prices are user-supplied in the MVP; a wrong price gives a wrong result.
- The tool reads public data. Telling it an address tells the operator which address you are interested in; say what the hosted version logs.
