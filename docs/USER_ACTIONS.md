# What only you can do

Accounting export, not tax advice.

The steps below need your accounts or your decision, in this order. Each one says what to tell the agent afterwards. Never paste a password, 2FA code, token or secret key into the chat: log in to tools yourself.

The four repositories are cloned locally in `_publish/` inside the monorepo folder. That is where work happens now (decision D12 in `STATUS.md`).

## Done

- [x] npm: logged in as `veronicdev`, 2FA enabled, `@veronicdev/ledgertax-core` 0.1.0 published (2026-11-07).

## 1. Maintainer contacts: done (2026-11-07)

Both contacts are chrisjacobs2468@gmail.com, in `SECURITY.md` and `CODE_OF_CONDUCT.md` of each package repository. `SECURITY.md` also points to GitHub's private vulnerability reporting; turn it on after step 2 in each repository's security settings, or tell the agent to.

## 2. Make the repositories public: done (2026-11-07)

All four repositories are public; `docs/demo-output/` and `docs/screenshots/` stay (your decision). In the three package repositories the ruleset is active (changes to `main` only through a pull request whose `check` job passed; no force-push, no deletion) and private vulnerability reporting is on. **Still for you:** the fork pull request approval setting in the last bullet below; the agent was not permitted to change organisation settings.

What this step asked for:

Wave needs public repositories. Do this after step 1. Also decide whether `docs/demo-output/` and `docs/screenshots/` (public testnet data) stay in `ledger-tax`.

- On GitHub: each repository, then **Settings**, **General**, **Danger Zone**, **Change visibility**. Read [GitHub's note on the consequences](https://gh.io/setting-repository-visibility) first.
- Or tell the agent: "make the repos public". It runs `gh repo edit Ledger-Tax/<repo> --visibility public --accept-visibility-change-consequences` for `ledgertax-core`, `ledgertax-api`, `ledgertax-web` and `ledger-tax`.
- Right after that, the agent turns on the branch rule in `docs/github-ruleset-main.json` for the three package repositories (`gh api -X POST repos/Ledger-Tax/<repo>/rulesets --input docs/github-ruleset-main.json`): changes to `main` only through a pull request whose `check` CI job passed, no force-push, no deletion. GitHub refuses this rule on private repositories of a free organisation, which is why it waits for this step.
- Recommended on GitHub: organisation **Settings**, **Actions**, **General**, "Approval for running fork pull request workflows": choose approval for all outside collaborators, so a stranger's pull request cannot run code in CI until you have read it.

## 3. Wave issues

Tell the agent: "create the Wave issues". It creates the issues drafted in `docs/wave-issues/` (core 5, api 5, web 4) in the three repositories, with labels.

## 4. Deploy the api and the web app (Phase 6.2)

Choose a host for each and create the accounts. If a host has a command-line tool, log in to it yourself.

- **api:** needs a long-running Node.js 22.13 or newer process. Build with `pnpm install --frozen-lockfile && pnpm build`, start with `node dist/server.js`, health check `GET /health`. A persistent disk is needed only if you want the history cache to survive restarts (`CACHE_DB`).
- **web:** a host that builds and serves Next.js apps.

Settings (none of them is a secret):

| Where | Variable | Value |
|---|---|---|
| api | `HORIZON_URL` | `https://horizon.stellar.org` (mainnet) or `https://horizon-testnet.stellar.org` (testnet) |
| api | `HOST`, `PORT` | Usually `0.0.0.0` and the port the host gives you (the default `127.0.0.1` accepts local connections only) |
| api | `CORS_ORIGINS` | The web app's public URL |
| api | `CACHE_DB` | A file on a persistent disk, or empty for an in-memory cache |
| api | `TRUST_PROXY` | `true` only if the host's proxy sits in front of the api (the rate limit needs the real client IP) |
| api | `RATE_LIMIT_MAX`, `RATE_LIMIT_WINDOW_MS` and the size limits | Optional; defaults are in the api README |
| web | `NEXT_PUBLIC_API_URL` | The api's public URL; read at build time |

Costs depend on the host and plan. The agent does not pick a paid plan for you.

Tell the agent: "deploy the api to <host> and the web app to <host>; I am logged in". The agent writes the host-specific steps, deploys, checks `/health` and the app, and updates every README's status.

## Optional

- **Core 0.1.1:** the README shown on npmjs.com for 0.1.0 still says "not published". Tell the agent "release core 0.1.1"; it bumps the version, updates the changelog and dry-runs. You then run `npm publish` in `_publish\ledgertax-core` and confirm in the browser. The api can take the new version a day later (pnpm's minimum release age) or through an exact-version exception like the one for 0.1.0.
- **A real address of yours** for the spreadsheet comparison in task 4.1. Tell the agent the public address; its history is not committed.
- **A person's keyboard and screen-reader pass** of the web app.
- **The Wave application** itself: follow `docs/WAVE_APPLICATION.md`. The agent does not apply for you.
