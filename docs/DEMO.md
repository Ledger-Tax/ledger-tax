# Demo and end-to-end verification

Accounting export, not tax advice.

Recorded 2026-11-06. Everything here ran on the **testnet** with throwaway accounts (public addresses only). No mainnet address and nothing belonging to a real person was used.

## What was run

- `ledgertax-api` built and started with `HORIZON_URL=https://horizon-testnet.stellar.org`, `CORS_ORIGINS=http://localhost:3099`, an in-memory cache.
- `ledgertax-web` built with `NEXT_PUBLIC_API_URL=http://localhost:8799` and started with `next start`.
- A real Chrome (headless) controlled through the DevTools protocol by a scratch script (not part of the repo) walked through the whole flow against those two servers and live testnet Horizon. The watched address is the main account of the recorded fixtures (`GCIINRBMEA2NGR46LMT5WWJNGVA242YSTV2ALU57CQIDOHL2CQSUJKYR`).

## Steps and what was observed

| # | Step | Result |
|---|---|---|
| 1 | Open the page | Loads; heading, disclaimer, one labelled field. [screenshot](screenshots/01-initial.png) |
| 2 | Press Tab from the top | Focus goes to the address field, then the "Load history" button (native controls, natural order) |
| 3 | Type a string shaped like a secret key | The field is emptied at once, a warning appears, the string appears nowhere in the page, nothing is sent. [screenshot](screenshots/02-secret-warning.png) |
| 4 | Enter the public address, "Load history" | A loading state appears, then 34 events (6 marked Unknown). [screenshot](screenshots/03-events.png) |
| 5 | Filter by type "Unknown" | 6 rows; back to all types |
| 6 | Label the funding as income, the first payment out as disposal | Selects change; both labels are in this browser's `localStorage` |
| 7 | Upload [prices.csv](demo-output/prices.csv) (XLM 0.10, TEST 1.50 USD on 2026-11-06), "Generate report" | Report with totals, 1 error row, gains table, two download links. [screenshot](screenshots/04-report.png) |
| 8 | Read the two downloads | [gains.csv](demo-output/gains.csv) (4 gain rows and 1 error row) and [events.csv](demo-output/events.csv) (34 rows); both start with `# Accounting export, not tax advice.` and state the source and history range |
| 9 | Reload the page and load the same address | Both labels are restored from the browser |
| 10 | Dark colour scheme | Applies from the tokens. [screenshot](screenshots/05-dark.png) |

Console errors: none. Failed requests: two `ERR_ABORTED`, which are the event stream being cancelled when the script navigated away; no CORS failures.

## Comparison with an independent calculation (task 4.1)

[verify_fifo.py](demo-output/verify_fifo.py) recomputes the gains from the downloaded `events.csv` (which carries the labels) with exact fractions, sharing no code with the TypeScript implementation, and the walkthrough's prices. Result:

- 4 gain rows, identical in acquired date, disposed date, asset, quantity, proceeds, cost, gain and holding days to the 4 rows of `gains.csv`.
- Total gain 48.00 USD in both.
- The same single problem in both: `unknown_cost_basis` for 40 TEST that arrived by a plain payment.

The hand-calculated example in `ledgertax-api/docs/EXAMPLE.md` is also reproduced row by row by the API tests, and the core tests rebuild the account's real XLM and TEST balances from the events (see `ledgertax-core/docs/CLASSIFICATION.md`).

Not done: a comparison on a real address of the user's, which needs the user to name one (public addresses only). It was not attempted.

## Timings seen

First request for this address (cold cache): about 2 seconds on this run, 14 seconds on another run, depending on Horizon's latency (dozens of Horizon requests are needed for 34 events). A repeat request is served from the cache and takes about 2 seconds. Once, after the machine had been suspended, two requests failed with `upstream_failed` after 46 seconds; they were reported to the client as normal error responses.

## Known issues and limits

- The classifier does not understand liquidity pools, Soroban contract events or linked addresses (they become `unknown` or are not modelled). `create_claimable_balance` is `unknown` and carries no amount, so locked funds are only visible as a flagged event.
- Incoming payments have an unknown cost basis unless labelled income, so selling them gives an error row. That is deliberate (nothing is guessed) but means a real history needs labelling to get a complete report.
- Only FIFO, only a user-supplied price CSV, only the two CSV formats.
- The public SDF Horizon keeps about one year; older history is missing and the report says which ledger range the server holds.
- Verification limits: a human keyboard-only and screen-reader walkthrough was **not** done (only automated checks and the Tab presses above); only desktop Chrome was used, at one window width; no Firefox, Safari or phone layout checks.
- The CI workflows have never run (no remote repository), and nothing has been published or deployed.
