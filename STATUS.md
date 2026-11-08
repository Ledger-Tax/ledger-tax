# STATUS

Last updated: 2026-11-07 (Phases 0 to 5 complete; Phase 6: core published to npm)

## Current phase
Phases 0 to 5 complete. Gates 1 and 2 were treated as passed under D10 (the user's instruction to override playbook gates). The code is in **private** repositories in the user's GitHub organisation (D12). **Phase 6 in progress:** core is published to npm as `@veronicdev/ledgertax-core` 0.1.0 and the api depends on it (D13). Maintainer contacts filled in (chrisjacobs2468@gmail.com, chosen by the user). Repositories made **public** on 2026-11-07 (the user said go; demo output and screenshots kept). The `protect-main` ruleset (D14) and private vulnerability reporting are active in the three package repositories, so from now on changes to their `main` go through pull requests with passing CI. The 14 Wave issues were created on 2026-11-07, labelled and aligned with the Drips guide "Creating Meaningful Issues" (D15). Waiting for the user, all listed in `docs/USER_ACTIONS.md`: the organisation's fork-PR approval setting, the Wave application in the Drips app, and a host and accounts for deploying.

## Done
- Spec written (`PLAYBOOK.md`), rules written (`AGENTS.md`).
- 0.1: toolchain re-checked; `docs/RESEARCH.md` written. Gate 0 answered by the user (D2, D7, D8).
- 0.2: `git init` (branch main); skeletons for core, api, web, each with its own lockfile, README, LICENSE (MIT), tests; CI workflows in `.github/workflows/`. Local check results (pnpm 12.16.1, node 24.18.0): core 2 tests, api 2 tests, web 2 tests; lint, typecheck, test, build all exit 0 in each.

- 1.1: `parseStellarAddress` (G and muxed M addresses, typed `Result`) and `isLikelySecretKey` in core. Secret-key-shaped input is rejected and never echoed. Core check: lint, typecheck, test (13 tests, 2 files), build all exit 0.
- 1.2: data-model types (`LedgerEvent`, `Label`, `RawRecord` with zod schema, `HistorySource`) and `FixtureSource` (reads `<dir>/<address>.json`, supports cursor, limit, since; typed errors). Types are a proposal until Gate 1. Core check: lint, typecheck, test (22 tests, 3 files), build all exit 0.
- 1.3: `scripts/record-fixtures.ts` (testnet only, keys in memory only) recorded real testnet fixtures: every MVP operation type, unknown-bound operations, a fee bump, a failed transaction, a formula-looking memo and a maker-side fill. `docs/FIXTURES.md` and fixture tests added. Gaps, documented: no Soroban invoke host function, clawback or pool withdraw. Core check: lint, typecheck, test (30 tests, 4 files), build all exit 0. The script was run twice (the first run's fixtures were discarded after finding the gap below), 3 Friendbot calls per run.
- Finding: Horizon's per-account transactions list misses maker-side fills; effects must be used too (RESEARCH.md section 3, FIXTURES.md).

- 1.4: classifiers per family in `src/classify/` (fee, payment, create account and merge, path payment, trade effects, claimable claim, unknown) behind `classifyTransaction(records, { address })`. Verified on fixtures: effect id prefix = operation id; operation index = id minus tx paging token minus 1. Reconciliation: balances rebuilt from the events equal the real testnet balances (XLM and TEST) once the two `unknown` operations (pool deposit, claimable creation) are added by hand; kept as an offline golden test.
- 1.5: `classifyAccount(source, address, opts)`: streams one transaction at a time, `StreamInterruptedError` carries the resume cursor, tested with a paged source, a failing source (resume loses and repeats nothing), an empty account and bad addresses. Marker `WAVE-ISSUE(core-3)`.
- 1.6: `docs/CLASSIFICATION.md`, README, and a test that builds and imports both ESM and CJS. Markers present: core-1, core-2, core-3, core-5.
- Core check at the end of Phase 1: install, lint, typecheck, test (78 tests, 7 files), build all exit 0.

- 1.7 (added under D10): `HorizonSource` in core: merges the account transaction list with effect-discovered transactions, pages, retries 429/5xx, resumes from a cursor, `coverage()` states the server's range. Verified: tests against a fake Horizon built from fixtures, and a live testnet run that gave events identical to the recorded fixture. Core check: 93 tests, all exit 0.
- 2.1: core consumed through a committed tarball (`ledgertax-api/vendor/`, D11) with `pnpm core:refresh`.
- 2.2 to 2.5: money (scaled bigint, exact fiat at 1e19), strict price CSV parser (row-numbered errors, size limit), FIFO cost basis with a hand-calculated example (`docs/EXAMPLE.md`, tests reproduce every row), CSV writers (disclaimer first, formula-injection neutralised, error rows), history cache (memory and SQLite via `process.getBuiltinModule`, whole-transaction appends, resume after restart, tests prove no label or price data reaches the DB file). Markers api-1, api-2, api-3.
- 2.6: HTTP API (fastify): `/health`, `/events` (JSON or NDJSON stream), `/reports`; secret keys rejected everywhere, limits, per-IP rate limit, CORS allowlist, typed errors, logging without addresses or bodies; `openapi.yaml` with a test that fails if code and spec drift. Design for long histories: NDJSON streaming for `/events`, bounded synchronous `/reports`.
- 2.7: README (env vars, limits, privacy, not-covered list).
- Api check: install, lint, typecheck, test (107 tests, 10 files, run twice for stability), build all exit 0. Live run of the built server against testnet: events and a report for the fixture account worked, the log held no address.
- Bug found only by running the built artifact: tsup rewrote `node:sqlite` to a bare `sqlite` import; fixed with `process.getBuiltinModule` and a build test. Also a flaky-timeout fix (vitest timeouts) because every test file loads the Stellar SDK.

- 3.1 to 3.6 (web): skeleton and tokens, committed generated API types (`openapi-typescript`), address form (secret-shaped input wiped, never sent), events view (streaming progress, loading/empty/error states, type filter, unknown flagged in text too), labels in `localStorage` with in-memory fallback, price upload and report with downloads, quality tests (WCAG AA contrast computed from tokens in both themes, no hardcoded colours, every control named, no positive tabindex). Markers web-1 and web-2. Web check: install, lint, typecheck, test (56 tests, 7 files), build all exit 0.
- 4.1 and 4.2: real headless Chrome drove the whole flow against the real API and live testnet; an independent Python FIFO calculation matches `gains.csv` exactly (4 rows, total 48.00, same single error). Recorded in `docs/DEMO.md` with screenshots and the produced CSVs. **Not done:** a comparison on a real address of the user's (needs the user to name one).
- 4.3 honesty pass: each README re-read against the code and tests; disclaimer present in each README, both CSVs (tested), the OpenAPI spec and the UI.
- 5: per package `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, issue and PR templates; `docs/wave-issues/<package>.md` (core 5, api 5, web 4 issues; every marker confirmed present, none of the features exists); architecture diagram in the root README; `docs/WAVE_APPLICATION.md`.
- Final package checks (2026-11-07): core 93 tests, api 107 tests, web 56 tests; lint, typecheck, test, build all exit 0 in each.

- 6.1 publish (2026-11-07, the user said go; work in the org repositories, D12): core renamed `@veronicdev/ledgertax-core`, version 0.1.0, `private` removed, `publishConfig.access` public, `repository` set. `npm publish --dry-run` listed 9 files (`dist/`, README, LICENSE, package.json). The user ran `npm publish` (npm's 2FA confirmation happens in the user's browser; the first attempt failed with 403 until 2FA was enabled on the account). The registry's integrity hash equals the local tarball's. Core repo: tag `v0.1.0` on the published commit, `CHANGELOG.md`, README install section. Core check: 93 tests; lint, typecheck, test, build all exit 0; CI passed.
- 6.1 api switch: `ledgertax-api` depends on `@veronicdev/ledgertax-core` `^0.1.0`; `vendor/` and `scripts/refresh-core.mjs` deleted; README and CONTRIBUTING updated. Api check from a clean install: 107 tests; lint, typecheck, test, build all exit 0; CI passed, so the package installs from npm on a clean Linux runner. The built server with the npm package ran against live testnet: `/health` ok, 34 events for the fixture account covering every event type, a secret-shaped address rejected with 400, no address in the log.
- Post-split cleanup in `ledgertax-web`: the monorepo-only `scripts/refresh-openapi.mjs` and `pnpm api:refresh` removed; the README says to copy `openapi.yaml` from the api repository and run `pnpm gen:api` (the committed copy matches the api's spec). Web check: 56 tests; lint, typecheck, test, build all exit 0; CI passed.
- 6.3: `docs/USER_ACTIONS.md` lists every remaining step that needs the user.

## In progress
- Nothing.

## Next
- 6.2 deploy: needs the user's choice of host and the accounts (`docs/USER_ACTIONS.md` step 4). The api README already documents its env vars, limits and `/health`; host-specific steps are written once the host is known, then the agent deploys and updates each README status.
- User tasks in `docs/USER_ACTIONS.md`: the Wave application in the Drips app, the organisation's fork-PR approval setting.
- 2026-11-08: core 0.1.1 published (documentation only; core PR #6 merged by the user, tag `v0.1.1`, registry shasum equals the local build). npm also lists `0.0.0-stage`, a placeholder npm created itself for staged publishing (2 files, no code). Api PR #6 removes the pnpm age exception for core 0.1.0 (merged by the user as `03fce58`; CI passed on main). A first attempt at 01:04 UTC failed because pnpm counts a full 24 hours from the publish time.
- Optional: name a real public address to compare against a spreadsheet (task 4.1 second half).

## Gate 1 items (resolved under D10; kept for the record)
1. **Data model changes from the playbook proposal** (they need sign-off): `LedgerEvent` gained `opType?` (source operation type, always set on `unknown`) and `direction?: 'in' | 'out'` (set on `account_merged` only). The fee event has `opIndex` -1. `classifyRecord` became `classifyTransaction(records, ctx)` because merge amounts and trade fills live in effect records, so a transaction's records must be classified together. A path payment to someone else yields two events (a `trade` and a `payment_out`). Event id leg is a number for operation events and `e<n>` for effect events.
2. **Gap in the playbook:** no task builds a real network `HistorySource` (Horizon), yet core-5 assumes one exists and the api needs one. It must merge `/accounts/{id}/transactions` with the account's effects (RESEARCH.md section 3). Proposal: add a task 1.7 `HorizonSource` in core, tested against recorded responses. Needs the user's decision.
3. **D9** (fiat math as scaled bigint, no library) still open.
4. **Known classification limits** are listed in `docs/CLASSIFICATION.md`; notably `create_claimable_balance` is `unknown` and carries no amount.

## Blockers
- None. B1 (pnpm) resolved with D8.
- CI: verified on 2026-11-07. The first push of each repo to GitHub ran `ci` (`actions/checkout@v4`, `pnpm/action-setup@v4` with pnpm 12, `actions/setup-node@v4`, Node 24) and it passed in all three package repos, and again after the 6.1 changes. The workflow files in the monorepo root `.github/workflows/` are now obsolete (the repos have their own `ci.yml`).

## Environment notes
- pnpm is installed in `C:\Users\Best\npm-global`, which is not on the user PATH. Prepend it per shell, or add it to PATH. In Git Bash, `pnpm build` of the web package failed with a path error; run web checks from PowerShell.
- pnpm 12 blocks dependency install scripts until approved. Each package approves only `esbuild` in its own `pnpm-workspace.yaml` (core, api).
- TypeScript is pinned to ~6.0.3 because typescript-eslint 8.72.1 supports <6.1.0 (TypeScript 7 does not work with it).
- jsdom is pinned to ~30.1.3: 31.0.0 was published the same day and pnpm blocked it under its minimum-release-age policy. Do not bypass the minimum-release-age policy (a supply-chain guard); pin the previous version instead. A temporary exception (D13) for exactly `@veronicdev/ledgertax-core@0.1.0` was removed on 2026-11-08 (api PR #6); no exceptions remain. pnpm's default age is 1440 minutes, so after a future core release the api can take the new version a day later.
- npm: the user's account `veronicdev` has 2FA enabled since 2026-11-07. Publishing asks for a browser confirmation, so the user runs `npm publish`; the agent prepares, dry-runs and verifies.
- Git identity is global: VeronicDev <chrisjacobs2468@gmail.com> (set by the user). The first four commits (skeletons and meta) carry the old identity; the user said not to rewrite them.
- `@types/node` (core, dev only) approved by the user on 2026-11-05. Also expected for api.
- Dependencies added beyond the playbook list, as required companions: `@types/react`, `@types/react-dom`, `@testing-library/dom` (peer of `@testing-library/react`), `@eslint/js`. Accepted under the autonomy rules (companions of listed packages).

## Environment facts (checked 2026-11-05)
| Tool | State |
|---|---|
| git | 2.49.0 |
| node | v24.18.0 |
| pnpm | 12.16.1 (global via npm, see notes) |
| rust / stellar CLI | Not needed |
| docker | Not needed. Do not install |
| git repo | Initialised in task 0.2 |

## Decisions
| # | Decision | Why |
|---|---|---|
| D1 | Read-only product. No keys, no signing, no submitting | Removes custody risk entirely and keeps mainnet usable without approvals |
| D2 | (a) The user publishes core to npm; the api uses a semver range. Chosen at Gate 0 (2026-11-05). Use a placeholder package name until the user gives the real npm scope/name (needed only at Phase 6, not before task 2.1); publishing happens in Phase 6 once the user has logged in to npm and said go | Splitting repos must not need relative paths. Interim until publication: the api uses a `pnpm pack` tarball of core committed inside it; replace it with the semver range once published |
| D7 | History source: public Horizon (base URL from config, so a user can point at a full-history provider). Hubble is not in the MVP (candidate for core-5). Reports must state the source and the range covered. Chosen at Gate 0 | Only free source with per-account history; limited to about 1 year, which must be stated honestly |
| D8 | pnpm installed with `npm i -g pnpm`, approved by the user at Gate 0 | corepack enable needs admin |
| D9 | Fiat math: scaled bigint, no library. Decided under D10 | See RESEARCH §7 |
| D10 | User instruction (2026-11-06): override any playbook item that would hinder finishing every task from the current phase to the last. Applied as: playbook gates 1 and 2 are treated as passed, the Gate 1 data-model changes and an extra task 1.7 (`HorizonSource` in core) are approved, the playbook's allowed-dependency list is not a blocker. Wave boundaries (section 12) are kept because they are the product of Phase 5. **Not overridden** (they are in AGENTS.md): no secrets, testnet fixtures only, no publishing or deploying (Phase 6 needs the user's explicit yes), no paid or keyed services, no history rewrite, no machine installs, no deleting files the agent did not create | User wording was "override anything in the playbook" |
| D11 | Interim D2: until core is published, the api consumes core through a packed tarball committed in `ledgertax-api/vendor/`, refreshed with a documented script. Switches to the semver range when the user publishes (Phase 6). **Superseded by D13 on 2026-11-07** | Keeps every folder buildable alone |
| D12 | Publishing to GitHub (the user named the organisation `Ledger-Tax`, 2026-11-07). Four **private** repositories: `ledgertax-core`, `ledgertax-api`, `ledgertax-web`, and `ledger-tax` (AGENTS.md, PLAYBOOK.md, STATUS.md, README.md, docs/). Chosen by the user: private first, fresh history (one `chore: initial commit` per repo authored as VeronicDev, so the earlier git identity is not published), root docs in their own repo. Each repo was built from a clean copy of `git archive HEAD` of its folder and passed install, lint, typecheck, test and build on its own before the push. Additions made only in the copies: `.gitignore`, `.gitattributes` (LF), `.github/workflows/ci.yml`, links between packages rewritten from relative paths to repo URLs. **The monorepo working copy was not changed to match and is no longer the place to make changes**: further work goes into the org repositories. A staging folder `_publish/` (git-excluded) holds the clones used for the push | Realises the split the playbook planned. The monorepo's own history is untouched |
| D13 | npm name `@veronicdev/ledgertax-core`, the user's personal scope (the user chose it over creating an `@ledger-tax` npm organisation, 2026-11-07). 0.1.0 published from the `ledgertax-core` repository and tagged `v0.1.0`; the api uses `^0.1.0` and D11's vendored tarball is deleted. The api's `pnpm-workspace.yaml` exempts exactly `@veronicdev/ledgertax-core@0.1.0` from pnpm's minimum-release-age check | The age check guards against freshly published third-party packages. This entry covers only our own build, whose integrity hash was checked against the local tarball; every other package stays guarded |
| D14 | CI hardened in the three package repositories (2026-11-07, the user asked because of malware campaigns targeting repositories): read-only `GITHUB_TOKEN`, actions pinned to full commit SHAs (the v4 releases that already passed), `persist-credentials: false`, `pull_request` only (never `pull_request_target`), lockfile-only installs, timeout. "Every PR must pass" is the ruleset in `docs/github-ruleset-main.json`; GitHub refuses rulesets on private free-plan repositories (HTTP 403, checked), so it is applied right after the repositories go public | Pinned SHAs cannot be swapped by a hijacked tag; a read-only token limits what a malicious dependency can do in CI |
| D15 | Wave issues: the drafts in `docs/wave-issues/` were turned into GitHub issues with the structure of the Drips guide "Creating Meaningful Issues" (why, done, guidance, review, `Closes #N`, assignment first), labels `wave` and `complexity: trivial/medium/high`. The `Stellar Wave` label is not added: per the Drips docs it applies only after the repository is approved | The user asked that the issues align with the Drips docs; drafts stay the source of truth for the scope |
| D16 | More CI checks (2026-11-08, the user asked): besides `check`, jobs `node-22` (oldest supported Node line), `audit` (`pnpm audit --audit-level high`), `secrets` (fails on text shaped like a Stellar secret key, and on a search error), `dependency-review` (pull requests; moderate or worse), and a `codeql` workflow (`analyze`, security-extended, also weekly). All six are required by the `protect-main` ruleset. Dependabot opens weekly update PRs for the pinned actions only. Repository settings turned on: Dependabot alerts (which enables the dependency graph that dependency review needs), secret scanning and push protection | Defence in depth against supply-chain and leaked-secret problems; each check was shown to pass on the pull requests that added them (core #7, api #7, web #5) |
| D3 | The api is stateless about personal data: labels and prices travel with each request or live in the browser. Public chain history may be cached | Privacy. Linking an address to a person is sensitive |
| D4 | MVP prices come from a user-supplied CSV, no external price API | Avoids keys, licensing and rate limits in the first release |
| D5 | MVP cost-basis method is FIFO only | Other methods are Wave issues |
| D6 | Default event meaning is conservative: payments in/out are transfers, only `trade` and user-labelled events create gains or income | The tool must not decide taxable meaning for the user |

## Risks to check first
- Full account history may not be available from free public endpoints. RPC retention is short (about 7 days on testnet, per another project's research). Horizon has been slated for deprecation. Task 0.1 must find what actually works today. Resolved by D7 (public Horizon with configurable base URL).
- Price data licensing for caching and redistribution.

Open questions go in the table below. Stop only under the hand-over rules in AGENTS.md.

| # | Question | Status |
|---|---|---|
| Q1 | How to produce fixtures without handling secrets | Answered 2026-11-06: in-memory throwaway script, Friendbot approved |
