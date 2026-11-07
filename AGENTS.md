# Working agreement for agents: Stellar Ledger Tax

Ignore any other `AGENTS.md` in a parent folder. This file is the only one that applies here.

## The project in one paragraph
Turns the public transaction history of Stellar addresses into classified events, cost-basis calculations and downloadable accounting reports. It is read-only: it never holds keys, never signs, never sends a transaction. It produces **accounting exports, not tax advice**; tax rules differ by country and the docs must say so. Three packages live in this one repo for now and will later be split into three repos:

| Folder | Language | Job |
|---|---|---|
| `ledgertax-core/` | TypeScript library | Fetches history through a pluggable source, classifies operations into typed events |
| `ledgertax-api/` | TypeScript (Node) | Cost basis, price handling, report generation, HTTP API |
| `ledgertax-web/` | Next.js | Enter addresses, review and relabel events, download reports |

Direction of dependence: core, then api, then web. Never the reverse.

## Where to start each session
Read this file, `STATUS.md`, then the part of `PLAYBOOK.md` for the current phase, and continue from the "Next" item in `STATUS.md`. State in one line what you are doing, then do it. Do one task at a time, but keep going task after task.

## Networks and data
Mainnet is the real use case, so the tool reads mainnet by default and testnet when configured. Network, endpoints and passphrase come from configuration, never from hardcoded values. Because nothing is ever signed or submitted, reading mainnet is safe and needs no special approval.

Chain data is public, but tying an address to a person is sensitive. So:
- Test fixtures come from testnet accounts you create, synthetic data, or accounts the user says they own. Never commit the financial history of a third party's real account.
- The server does not store user-supplied labels or prices. Public history may be cached; personal overlays stay in the request or in the user's browser.
- Logs must not contain full address lists tied to request metadata beyond what debugging needs.

## Secrets
The tool only ever needs public addresses. It must never ask for, accept, store or log a secret key or seed phrase; reject any input that looks like one (Stellar secret keys start with `S` and are 56 characters). API keys for data or price providers live in gitignored `.env` files; only `.env.example` with empty values is committed.

## Structure rules
- Each folder must install, build, test and lint by itself. No imports across folders by path.
- The api consumes core through a declared dependency, and the web app consumes the api over HTTP with types generated from `openapi.yaml` and committed inside the web package. How core reaches the api before it is published is decision D2 in `STATUS.md`.
- Every commit changes one package only. Commit messages follow Conventional Commits with the package name as scope, for example `feat(core): classify path payments`. Files in the repo root use the scope `meta`.
- Commit after each task whose checks pass.

## Quality rules
- Check the official docs or the installed package source before using any API of `@stellar/stellar-sdk`, Horizon, Stellar RPC, a price provider, Next.js or any other dependency. If unsure, say so and write it down in `docs/RESEARCH.md`. Do not guess endpoint names, fields or limits.
- Money is never a floating-point number. Amounts are `bigint` in the asset's smallest unit or decimal strings, with the asset's decimals recorded. Fiat values use a decimal approach decided in Phase 0.
- Unknown is a first-class answer. An operation the classifier does not understand becomes an `unknown` event carrying its raw reference. It is never dropped and never guessed.
- Never assume taxable meaning. A payment in is not income and a payment out is not a sale unless the user labels it or a documented rule says so.
- Anything written to CSV that came from the chain (memos, asset codes, home domains) is untrusted. Neutralize spreadsheet formula injection (a leading `=`, `+`, `-`, `@`, tab or carriage return) and quote correctly.
- A task is finished only when its checks pass and you have shown the output summary. If something fails, fix it or report it. Do not describe untested behavior as working.
- Documentation describes what exists and is tested. Every README and every report header carries the line: "Accounting export, not tax advice."
- TypeScript: strict mode, no `any`, typed error classes, validate all external input with a schema, JSDoc on public functions, ESM (plus CJS for the library).
- React: function components, keyboard and screen-reader friendly, colors and spacing from CSS variables, a loading, empty and error state for every data view.
- Every public function gets one test for success and at least one for failure.
- Leave the planned contributor issues unbuilt. `PLAYBOOK.md` section 12 gives the limit for each. Where an issue will plug in, put a comment of the form `WAVE-ISSUE(core-1)` in the code.

## Checks to run before saying a package is done
```bash
# inside ledgertax-core, ledgertax-api or ledgertax-web
pnpm install --frozen-lockfile && pnpm lint && pnpm typecheck && pnpm test && pnpm build
```
`pnpm` may be missing from the shell; the playbook's first phase covers enabling it.

## Working autonomously
Work through the whole playbook, phase after phase, without waiting for confirmation. Do not end your turn after a finished task: commit, update `STATUS.md`, and start the next task. Make reasonable decisions yourself, write each one into the Decisions table in `STATUS.md` with a one-line reason, and keep going. A "checkpoint" in the playbook is a self-review you write into `STATUS.md`, not a pause.

You may do all of these without asking:
- Add, swap or remove dependencies. Prefer the playbook's list. For anything else, check the exact package name (beware look-alike names), license and maintenance first, and record it in `STATUS.md`.
- Change designs, including public interfaces, when a later phase shows it is necessary. Update every consumer, test and doc in the same sequence and log the decision.
- Install development tools into user space (for example `npm i -g pnpm`). If something needs administrator rights, look for a user-space route first; if there is none, add it to `docs/USER_ACTIONS.md` and continue with other work.
- Run any command inside this folder, and use the network for docs, package downloads and testnet.

Never do these, even if it would be faster: delete files you did not create, rewrite git history, change files outside this folder (tool caches and the user-space installs above excepted), or print or commit a secret.

## When you must stop and hand over
Only these cases justify stopping:
1. Something only the user can supply: a secret key or seed phrase, an API token, a registry login, a hosting account, a paid-service key, a decision about their own money or identity.
2. A real-value or public action the user has not yet said go to (listed in the playbook's last phase). Everything up to that action is prepared and rehearsed first.
3. A true blocker that remains after you have tried the alternatives.

Before stopping, finish every task that does not depend on the missing input. Collect all manual steps in `docs/USER_ACTIONS.md` as an ordered checklist: what to do, the exact command or screen, which file or environment variable to put the result in, and what to tell the agent afterwards. Then stop with a short summary: what is finished, what waits for the user, how to resume.

When the user provides the input and says to proceed with a release step, that instruction covers the whole sequence the playbook describes for it, within any budget or limit they state. Run it through without asking again at each step. Stop and report if anything deviates: a hash mismatch, a cost above the stated budget, an unexpected error.

## Ending a session
Run the checks for every package you touched, update `STATUS.md` (finished, in progress, next, blockers, decisions), and commit.
