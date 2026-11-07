# Wave application checklist

Accounting export, not tax advice.

This is a checklist **for you**. The agent does not apply to anything on your behalf. Read the whole page before submitting anything.

## Important

- **A rejected repository cannot be re-applied.** Make sure each repository is ready before it is submitted.
- **Application limits may apply per cycle** (for example how many repositories one maintainer may submit). Check the programme's current rules first; this file does not know them.
- I could not verify the programme's current requirements (this was written from the playbook). Use the programme's own page as the authority and treat the list below as preparation.

## Before you split the monorepo

- [ ] Decide the final repository names and the npm scope for core (the api depends on a package named `ledgertax-core`; a scope may change the name).
- [ ] **Publish `ledgertax-core` to npm** (your explicit decision; nothing has been published). Then in `ledgertax-api` replace the `file:vendor/...` dependency by a semver range, delete `vendor/` and `scripts/refresh-core.mjs`, run `pnpm install`, and update its README's last section.
- [ ] Move each package's CI workflow out of the monorepo root: `.github/workflows/ledgertax-<name>.yml` becomes `.github/workflows/ci.yml` inside that repository, and the `working-directory` line and the `paths` filter are removed. **The workflows have never run**; the action versions (`actions/checkout@v4`, `pnpm/action-setup@v4` with `version: 12`, `actions/setup-node@v4`) are unverified. Push a branch and make sure they pass in every repository.
- [ ] In `ledgertax-web`, `scripts/refresh-openapi.mjs` only works inside the monorepo. Delete it after the split, and document where to get `openapi.yaml` (the api repository's release or raw file).
- [ ] Decide what to do about history: the first four commits carry an earlier git identity (see `STATUS.md`). Splitting with history preserved is your call and touches git history; the agent did not do it.
- [ ] Remove or keep `docs/demo-output/` and `docs/screenshots/` (public testnet data) as you prefer.

## For each of the three repositories

- [ ] **README** with what it is, "Accounting export, not tax advice.", and only what is implemented and tested. (Each package README was checked against the code on 2026-11-07; re-read it after the split.)
- [ ] **Passing CI** on the default branch (see above: never run yet).
- [ ] **Licence**: MIT is in each package (`LICENSE`, copyright "Stellar Ledger Tax contributors"). Change the holder if you want a name.
- [ ] **CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, issue templates, PR template**: present. **Fill in the two `TODO(maintainer)` lines** (a private way to report vulnerabilities, and a contact for conduct reports) before the repository is public. The agent cannot invent a contact for you.
- [ ] **4 to 6 scoped issues** created from `docs/wave-issues/<package>.md`: core has 5, api has 5, web has 4. Create them in the repository and label them. Each names a marker you can find with `git grep "WAVE-ISSUE"`.
- [ ] **Clear scope per repository**: core classifies, api calculates and serves, web is the interface (the dependency direction is core, then api, then web).
- [ ] No secrets in any history: search for `S` followed by 55 base32 characters, `.env` files and key files before publishing. (None were committed; `.env.example` files have empty values.)

## Things to be honest about when you apply

- The project is early: nothing is published or deployed, and it has been verified on testnet only. The mainnet read path uses the same code but was not exercised.
- Classification can be wrong and history can be incomplete; both are said in the docs and in every report.
- Liquidity pools, Soroban contract events, several addresses, other cost-basis methods, price sources and other export formats are deliberately left as the contributor issues.
