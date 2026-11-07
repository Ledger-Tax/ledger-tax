# Wave issues: ledgertax-core

Accounting export, not tax advice.

Drafts of the contributor issues for this repository. Each one is inside the MVP boundary described in `PLAYBOOK.md` section 12: the feature does **not** exist yet (checked against the code on 2026-11-07), and the marker named in each issue exists in the code. Complexity maps to points: Trivial = 100, Medium = 150, High = 200.

Before starting any of them: read `CONTRIBUTING.md`, `docs/CLASSIFICATION.md` and `docs/FIXTURES.md`, and run `pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm test && pnpm build`.

---

## core-1: Liquidity pool deposit, withdraw and trade classifier

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(core-1)` (`src/classify/unknown.ts`, two places)

**Background.** Today `liquidity_pool_deposit`, `liquidity_pool_withdraw` and `liquidity_pool_trade` effects all become `unknown` events with no amounts. The recorded fixtures contain a real pool deposit (`test/fixtures/`), and its operation record has `reserves_deposited` and `shares_received`.

**Acceptance criteria**
- A deposit and a withdraw by the watched address produce events with the amounts of both reserve assets and the pool shares, using the existing event types where they fit or one new, documented type (changing the event types needs a maintainer's agreement in the issue first).
- A `liquidity_pool_trade` effect of the address produces a `trade` event with the right asset, amount, counter asset and counter amount.
- Operations in failed transactions still produce only the fee.
- `docs/CLASSIFICATION.md` is updated: what is now classified and what is still `unknown`.
- Tests: the recorded deposit fixture (happy path); a record with a missing reserve amount (typed `MalformedRecordError`); a withdraw (record a new testnet fixture with `pnpm fixtures:record` or add a clearly named synthetic one).
- The "reconciliation" test in `test/classify.test.ts` no longer needs the by-hand pool adjustment.

**Files to touch:** `src/classify/` (new `pool.ts`, `index.ts`, `unknown.ts`), `test/classify.test.ts`, `docs/CLASSIFICATION.md`, possibly `scripts/record-fixtures.ts`.

---

## core-2: Soroban `invoke_host_function` events

**Complexity:** High (200)  **Marker:** `WAVE-ISSUE(core-2)` (`src/classify/unknown.ts`)

**Background.** Calls to Soroban contracts become `unknown` events. Token movements inside them are visible in the operation's `asset_balance_changes` (Horizon) and in contract events. Soroban token decimals are read with the SEP-41 `decimals()` function, so amounts cannot assume 7 decimals.

**Acceptance criteria**
- An `invoke_host_function` whose `asset_balance_changes` move assets of the watched address produces payment or trade events with correct amounts and the decimals of each asset.
- A call that moves nothing for the address stays `unknown`.
- Contract asset ids (`C...`) are accepted wherever an `AssetId` is.
- The decimals source is injectable and failures are a typed error, not a crash. No network calls in tests.
- Documentation states exactly which contract interactions are understood.
- Tests: success and failure paths with fixture records (a testnet fixture, or a documented synthetic one marked `synthetic` in its file name).

**Files to touch:** `src/classify/` (new `invoke.ts`), `src/classify/common.ts` (asset id forms), `test/`, `docs/CLASSIFICATION.md`, `docs/FIXTURES.md`.

---

## core-3: Several linked addresses

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(core-3)` (`src/classify-account.ts`, `src/classify/index.ts`)

**Background.** One address is classified at a time, so a transfer between two of a person's own wallets shows as a payment out of one and a payment in of the other. That is neither a sale nor income.

**Acceptance criteria**
- A way to classify a set of linked addresses together (a documented new function or option) that marks payments between them as transfers between own wallets, and does not report them as income or disposals.
- Event ids stay unique across addresses (they currently omit the address; decide and document how).
- Single-address behaviour and existing tests are unchanged.
- Tests: two fixture accounts that pay each other (the recorded fixtures have `W` and the merged account), a transaction touching only one of the addresses, and invalid addresses in the set (typed errors, secret-key-shaped input rejected).
- `docs/CLASSIFICATION.md` explains the new behaviour.

**Files to touch:** `src/classify/index.ts`, `src/classify-account.ts`, `src/types.ts` (only with agreement), `test/`, `docs/CLASSIFICATION.md`.

---

## core-4: Fixture library from more testnet accounts

**Complexity:** Trivial (100)  **Marker:** none (tests)

**Background.** There is one fixture per operation type from one recording run.

**Acceptance criteria**
- Run `pnpm fixtures:record` again (it creates throwaway testnet accounts in memory and prints no secrets) and add the new fixture files and manifest entries, or extend the script with another scenario (for example a failed offer, a sponsored account, an operation with several operations in one transaction).
- Existing tests still pass; add a test that proves each new fixture loads and classifies (no `MalformedRecordError`) and that the reconciliation-style balance check holds where possible.
- `docs/FIXTURES.md` lists what the new fixtures cover.
- No secret keys anywhere in the diff.

**Files to touch:** `test/fixtures/`, `scripts/record-fixtures.ts` (optional), `test/fixtures.test.ts`, `docs/FIXTURES.md`.

---

## core-5: A second `HistorySource` adapter

**Complexity:** Medium (150)  **Marker:** `WAVE-ISSUE(core-5)` (`src/types.ts`, `src/horizon-source.ts`)

**Background.** `HorizonSource` is the only network source. The public SDF Horizon keeps about one year of history, so a source with full history (for example another Horizon provider, or a data lake export) would make reports complete.

**Acceptance criteria**
- A new class implementing `HistorySource` that yields records in the shape the classifiers expect (transaction record first, then its operations, then its effects, oldest first), including maker-side fills, with a resume cursor.
- Configuration comes from constructor options (no hardcoded endpoints, no API keys in the repository).
- Tests use recorded or fake responses only; no live network in the suite.
- It reports which range it covers, like `HorizonSource.coverage()`.
- README states which provider it targets and its limits.

**Files to touch:** `src/` (new source file), `src/index.ts`, `test/`, `README.md`.
