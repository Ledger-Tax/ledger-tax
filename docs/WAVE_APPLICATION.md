# Wave application checklist

Accounting export, not tax advice.

This is a checklist **for you**. The agent does not apply to anything on your behalf. Read the whole page before submitting anything.

## Important

- **A rejected repository cannot be re-applied.** Make sure each repository is ready before it is submitted.
- **Application limits may apply per cycle** (for example how many repositories one maintainer may submit). Check the programme's current rules first; this file does not know them.
- I could not verify the programme's current requirements (this was written from the playbook). Use the programme's own page as the authority and treat the list below as preparation.

## Before you split the monorepo

- [x] Repository names: done, `ledgertax-core`, `ledgertax-api`, `ledgertax-web` and `ledger-tax` (root docs) in the `Ledger-Tax` organisation, **private**. npm name: `@veronicdev/ledgertax-core` (chosen by you on 2026-11-07).
- [x] **Publish `ledgertax-core` to npm**: done on 2026-11-07 (0.1.0, tagged `v0.1.0` in the repository). The api depends on `^0.1.0`; `vendor/` and `scripts/refresh-core.mjs` are deleted; CI passed.
- [x] Each repository has its own `.github/workflows/ci.yml`. **Verified on 2026-11-07: the first run passed in all three package repositories** (so `actions/checkout@v4`, `pnpm/action-setup@v4` with `version: 12` and `actions/setup-node@v4` work). The old workflow files in the monorepo root are obsolete.
- [x] In `ledgertax-web`, the monorepo-only `scripts/refresh-openapi.mjs` is deleted and the README says to copy `openapi.yaml` from the api repository (done on 2026-11-07).
- [x] History: the repositories start with one fresh commit authored as VeronicDev, so the earlier git identity was not published. (Decided by you on 2026-11-07.)
- [ ] Remove or keep `docs/demo-output/` and `docs/screenshots/` (public testnet data) as you prefer.

## For each of the three repositories

- [ ] **README** with what it is, "Accounting export, not tax advice.", and only what is implemented and tested. (Each package README was checked against the code on 2026-11-07; re-read it after the split.)
- [x] **Passing CI** on the default branch: yes for all three on 2026-11-07. Re-check after every change.
- [ ] **Licence**: MIT is in each package (`LICENSE`, copyright "Stellar Ledger Tax contributors"). Change the holder if you want a name.
- [ ] **CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, issue templates, PR template**: present. **Fill in the two `TODO(maintainer)` lines** (a private way to report vulnerabilities, and a contact for conduct reports) before the repository is public. The agent cannot invent a contact for you.
- [ ] **4 to 6 scoped issues** created from `docs/wave-issues/<package>.md`: core has 5, api has 5, web has 4. Create them in the repository and label them. Each names a marker you can find with `git grep "WAVE-ISSUE"`.
- [ ] **Clear scope per repository**: core classifies, api calculates and serves, web is the interface (the dependency direction is core, then api, then web).
- [ ] No secrets in any history: search for `S` followed by 55 base32 characters, `.env` files and key files before publishing. (None were committed; `.env.example` files have empty values.)

## Things to be honest about when you apply

- The project is early: core is published to npm (0.1.0) but nothing is deployed, and it has been verified on testnet only. The mainnet read path uses the same code but was not exercised.
- Classification can be wrong and history can be incomplete; both are said in the docs and in every report.
- Liquidity pools, Soroban contract events, several addresses, other cost-basis methods, price sources and other export formats are deliberately left as the contributor issues.
