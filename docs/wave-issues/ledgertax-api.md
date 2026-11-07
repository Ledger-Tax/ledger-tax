# Wave issues: ledgertax-api

Accounting export, not tax advice.

Drafts of the contributor issues for this repository. Each one is inside the MVP boundary described in `PLAYBOOK.md` section 12: the feature does **not** exist yet (checked against the code on 2026-11-07), and the marker named in each issue exists in the code. Complexity maps to points: Trivial = 100, Medium = 150, High = 200.

Before starting any of them: read `CONTRIBUTING.md` and `README.md`, and run `pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm test && pnpm build`.

---

## api-1: LIFO and average-cost methods

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(api-1)` (`src/costbasis.ts`)

**Background.** Only FIFO exists; any other method is rejected with `unsupported_method`. The method is a request field (`method`) and appears in the report header.

**Acceptance criteria**
- `lifo` and `average` are accepted by `computeCostBasis`, the HTTP API (`openapi.yaml` enum, validation) and the CSV header line.
- A hand-calculated example for each method is added to `docs/EXAMPLE.md` (worked on paper, not copied from program output) and reproduced exactly by tests.
- Proceeds still add up exactly across lots, and partial-lot, loss, zero-cost, uncovered-disposal and missing-price cases are tested for each method.
- Average cost is defined in the docs (per asset, running average, how transfers and fees affect it).
- `src/costbasis.ts` stays readable: share the lot logic rather than copying it.

**Files to touch:** `src/costbasis.ts`, `src/app.ts` (request schema), `openapi.yaml`, `test/costbasis.test.ts`, `docs/EXAMPLE.md`, `README.md`.

---

## api-2: Another export format

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(api-2)` (`src/reports.ts`, the `EXPORT_FORMATS` registry)

**Background.** There are two generic CSVs (`events.csv`, `gains.csv`). Many people need the layout of a specific accounting program or a tax-software import format.

**Acceptance criteria**
- A new format registered in `EXPORT_FORMATS` and selectable through the API (a request field and `openapi.yaml`), documented with the real column specification and a link to the source of that specification.
- The output starts with `Accounting export, not tax advice.` in whatever way the format allows (a comment line, a header note or a field), and says so in the README if the format has no room for it.
- All text that came from the chain or the user is neutralised against formula injection and quoted correctly; tests with memos beginning `=`, `+`, `-`, `@`, quotes, commas, newlines and unicode.
- Error rows and warnings are not silently dropped; if the format cannot show them, they are reported another way and tested.

**Files to touch:** `src/reports.ts`, `src/service.ts`, `src/app.ts`, `openapi.yaml`, `test/reports.test.ts`, `README.md`.

---

## api-3: Postgres history cache

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(api-3)` (`src/cache.ts`)

**Background.** The cache has an in-memory store and a SQLite store behind the `HistoryStore` interface. A shared deployment needs Postgres.

**Acceptance criteria**
- A `PostgresHistoryStore` implementing `HistoryStore` with the same behaviour as the SQLite store (ordered reads, last cursor, whole-transaction appends, namespaces), chosen by configuration (a new environment variable documented in `README.md` and `.env.example`, with an empty value).
- It stores public chain history only. A test proves that no label or price data reaches the database (like the existing SQLite privacy test).
- The new dependency is justified in the pull request; connection strings never appear in logs.
- Tests run without a hosted database (for example against an embedded or containerised Postgres started by the test, or a documented skip when none is available, with the contract tests shared with the other stores).

**Files to touch:** `src/cache.ts` (or a new file), `src/config.ts`, `src/server.ts`, `test/cache.test.ts`, `README.md`, `.env.example`, `package.json`.

---

## api-4: A price-source adapter

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(api-4)` (`src/service.ts`)

**Background.** Prices come only from a CSV the user uploads. A price-source adapter would fill missing prices from an external provider.

**Acceptance criteria**
- An adapter interface (`getPrice(asset, day, currency)`) used by `buildReport` in addition to the uploaded file; the uploaded file wins when both have a price.
- At least one real provider adapter, with its licence terms for caching and redistribution checked and written in the README, or a clearly documented fake used by tests plus the interface, if no provider's terms allow it.
- API keys come only from environment variables listed with empty values in `.env.example`; a key must never be sent to the browser or logged.
- Prices it fetched are never stored with the user's address (the server must not link addresses and personal overlays); tests prove it.
- A missing price is still an error row, never a guess, and the report says which prices came from the provider.

**Files to touch:** `src/service.ts`, `src/prices.ts`, `src/config.ts`, `test/`, `README.md`, `.env.example`.

---

## api-5: OpenAPI examples and an error catalogue

**Complexity:** Trivial (100)  **Marker:** none (docs)

**Background.** `openapi.yaml` has one example. A client author needs more.

**Acceptance criteria**
- Examples for every endpoint and every error code (request and response), taken from real runs against testnet where possible.
- An error catalogue section (or a `docs/ERRORS.md`) saying, for every `error.code`, when it happens and what a client should do.
- The existing test that keeps the spec in step with the code still passes, and checks that every error code has an example.
- No secrets or real addresses in any example.

**Files to touch:** `openapi.yaml`, `docs/ERRORS.md` (new), `test/openapi.test.ts`.
