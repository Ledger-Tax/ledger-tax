# RESEARCH (Phase 0, task 0.1)

Checked 2026-11-05. Accounting export, not tax advice.

Legend: **[verified live]** = I called the public endpoint myself (read-only, network-wide queries, no particular account). **[docs]** = read from the linked page. **[unverified]** = could not confirm; do not rely on it.

## 0. Toolchain

| Tool | Result |
|---|---|
| git | 2.49.0 |
| node | v24.18.0 (satisfies `@stellar/stellar-sdk` engines `>=22.12.0`) |
| npm | 11.16.0 |
| corepack | 0.35.0 present, but `corepack enable` fails: `EPERM ... C:\Program Files\nodejs\pnpm` (needs admin rights). Not elevated. |
| pnpm | **Missing.** Options in STATUS.md (blocker B1). |

## 1. History source (the feasibility question)

| Source | Full history of an arbitrary mainnet account? | Cost / limits | Notes |
|---|---|---|---|
| SDF public Horizon `horizon.stellar.org` | **No: rolling ~1 year.** | Free. Rate limits not documented on the pages I read; I saw no `X-RateLimit-*` headers. [unverified] | [verified live] v30.0.0, `history_elder_ledger` 59010481; oldest operation returned is dated 2025-09-20 (about 13.5 months old today, so truncation lags the one-year target). Truncation announced for 2024-08-01: [SDF blog](https://stellar.org/blog/foundation-news/sdf-s-horizon-limiting-data-to-1-year). A third-party issue ([x402scan#3](https://github.com/EmanuXBe/x402scan/issues/3)) claims a backfill stays complete only until 2027-03-06: [unverified]. |
| SDF public Horizon testnet | Yes, from ledger 128 [verified live] | Free | Testnet resets; fine for fixtures. |
| Stellar RPC `getTransactions` | **No: about 7 days by default** ([RPC docs](https://developers.stellar.org/docs/data/apis/rpc)). | Providers differ; no public SDF mainnet RPC named on that page. | `limit` 1..200, opaque `cursor`, errors if `startLedger` is older than the node's oldest ledger ([getTransactions](https://developers.stellar.org/docs/data/apis/rpc/api-reference/methods/getTransactions)). Returns XDR only (envelope, result, meta), so we would parse XDR ourselves. No per-account filter that I found [unverified]. |
| Hubble (BigQuery public dataset) | **Yes, full network history** | Free storage, but the user pays query cost (needs a Google Cloud project). Intraday batch latency, not real time ([Hubble](https://developers.stellar.org/docs/data/analytics/hubble)). | Not usable from a plain browser/anonymous server without credentials. Dataset path and schema not yet verified. |
| Third-party Horizon providers / indexers | Possibly | Usually paid or key-gated | Listed in Stellar docs (see [Horizon page](https://developers.stellar.org/docs/data/apis/horizon)). Not evaluated; needs the user's OK (paid/keyed service). |
| Self-hosted Horizon | Yes if you ingest from genesis | Heavy infrastructure | Out of scope; "Do not install" rule. |
| Galexie / data lake | Yes in principle | Not evaluated | Mentioned as the forward path for full-history ledger data ([migration guide](https://developers.stellar.org/docs/data/apis/migrate-from-horizon-to-rpc)). I did not find a public bucket URL. [unverified] |

**Horizon status.** Still live and current (v30) on both networks today [verified live]. I found no official SDF end-of-life date. Secondary sources describe it as maintenance-only, with the `stellar/go` monorepo archived 2025-12-16 (from a [third-party ADR](https://stellarindex-showcase.pages.dev/research/adr/0001/), [unverified]). Treat Horizon as usable but at risk.

**Conclusion for Gate 0.** No free source returns the *complete* mainnet history of an arbitrary address. The best free option, public Horizon, covers about the last year (and any account's older activity is gone). That is enough for a tax-year report only for recent years; older cost basis (assets bought earlier) will be missing, and FIFO lots would be wrong. The report must state the range the source covered (PLAYBOOK §13).

## 2. Record shapes (Horizon JSON)

Field lists below come from **live samples [verified live]** (200 most recent network-wide operations). Types not seen in the sample are marked.

All operations: `id, paging_token, type, type_i, created_at, transaction_hash, transaction_successful, source_account`.

| Operation | Amount / asset fields | Counterparty |
|---|---|---|
| `payment` | `amount` (string, 7 dp), `asset_type/asset_code/asset_issuer` | `from`, `to`, `to_muxed`, `to_muxed_id` |
| `path_payment_strict_send` | dest: `amount`, `asset_*`; source: `source_amount`, `source_asset_*`; `destination_min`, `path` | `from`, `to` |
| `path_payment_strict_receive` | dest `amount`, `asset_*`; `source_amount`, `source_max`, `source_asset_*`; `path` | `from`, `to` |
| `create_account` | `starting_balance` (XLM) | `funder`, `account` |
| `manage_sell_offer` / `manage_buy_offer` | `amount`, `price`, `price_r`, `selling_asset_*`, `buying_asset_*`, `offer_id` (**offer params, not what was filled**) | none |
| `change_trust` | `asset_*`, `limit`, `trustor`, `trustee` | |
| `create_claimable_balance` | `asset` (string), `amount`, `claimants` | claimants |
| `invoke_host_function` | `function`, `parameters`, `asset_balance_changes` | |
| `set_options` | `home_domain` only when set (not in the sample); signers/thresholds seen | |
| `begin/end_sponsoring_future_reserves` | seen in sample | |
| `account_merge`, `claim_claimable_balance`, `create_passive_sell_offer`, `liquidity_pool_deposit/withdraw`, `clawback` | **Not in the sample; shapes not verified.** Must be checked from the per-type pages or testnet before Phase 1.3. | |

Transaction object [verified live]: `successful, hash, ledger, created_at, source_account, fee_account, fee_charged, max_fee, operation_count, envelope_xdr, result_xdr, fee_meta_xdr, memo_type, preconditions, fee_bump_transaction, inner_transaction`. `memo` is present only when the transaction has one; `memo_type` is documented as `MEMO_TEXT|ID|HASH|RETURN` ([docs](https://developers.stellar.org/api/horizon/resources/transactions/object)). Memos are untrusted.

## 3. Effects versus operations

- Operations show what the submitter *asked for*. Offers show offer parameters, not fills; path payments show max/min bounds plus the sent/received amounts.
- Effects show what *moved*, per account [verified live]: `account_credited`/`account_debited` (`amount`, `asset_*`), `trade` (`sold_amount/asset`, `bought_amount/asset`, `seller`, `offer_id`), `liquidity_pool_trade` (`sold`, `bought`), `claimable_balance_claimed`, `trustline_created/removed`, `account_removed`.
- `/trades` gives `base_amount`, `counter_amount`, `base_asset_*`, `counter_asset_*`, `base_account`, `base_is_seller`, `price`, `trade_type` (orderbook vs liquidity pool) [verified live].
- **Recommendation:** use effects (plus the operation for context and memo) for amounts of trades and path payments; use operations for classification. RPC has no trade events; trades must be inferred from events plus meta XDR ([migration guide](https://developers.stellar.org/docs/data/apis/migrate-from-horizon-to-rpc)).
- **Found while recording fixtures (2026-11-06, testnet, verified live):** `/accounts/{id}/transactions` does NOT include a transaction in which another account filled this account's resting offer (maker-side fill), although `/accounts/{id}/effects` contains the `trade` effect. A source built only on the transactions list silently misses those trades. Discover transactions through effects as well. See ledgertax-core `docs/FIXTURES.md`.
- Open point: the effect-to-operation link (`_links.operation`) and per-account effects endpoint were not exercised. Verify in Phase 1.3.

## 4. `@stellar/stellar-sdk`

Latest on npm: **17.4.0**, `node >=22.12.0` ([npm registry](https://registry.npmjs.org/@stellar/stellar-sdk/latest), checked 2026-11-05). Its dependency list includes `bignumber.js`. I did not yet read the installed package source, so I have **not verified class names** for the Horizon client (`Horizon.Server`) or RPC client (`rpc.Server`) in v17. Verify from the installed package in task 1.x before use. Core can alternatively call Horizon over `fetch` with zod validation, which avoids coupling to SDK class names.

## 5. Asset decimals

- Classic assets (and XLM): 7 decimals; Horizon amounts are decimal strings with 7 places (seen in samples). Store as `bigint` stroops = amount × 10^7.
- Soroban tokens: SEP-41 `decimals() -> u32` ([SEP-41](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0041.md)). Reading it needs a contract call (simulate) and is part of core-2, out of MVP.

## 6. Fees

- `fee_charged` (stroops, string) is the fee actually charged; `max_fee` is the cap [docs](https://developers.stellar.org/api/horizon/resources/transactions/object).
- `fee_account` can differ from `source_account` [verified live]: a fee-bump sample had a different `fee_account`, with `fee_bump_transaction.hash` and `inner_transaction.{hash,max_fee}`. Rule: the **fee event belongs to `fee_account`**, not `source_account`. A watched address that is only the inner source pays nothing.
- Failed transactions still charge the fee.
- Sponsorship: the sponsor pays *reserves*, not fees. I did not confirm how sponsored fee payment looks beyond fee bumps. [unverified]

## 7. Decimal handling for fiat

Recommendation: **scaled `bigint` integers, no library.** Crypto amounts: stroops (10^7). Prices: parse decimal strings into a bigint with a fixed scale (propose 10^18 working precision for prices and rounding to currency minor units at report time, half-up, documented). Avoids a new dependency (none beyond the allowed list). `bignumber.js` is already transitive via the SDK, but it must not be imported unless approved. Needs sign-off at Gate 1 (data model).

## 8. CSV injection

OWASP lists leading `=`, `+`, `-`, `@`, tab, CR, LF and full-width variants (＝ ＋ － ＠) as dangerous. Mitigations: quote the field and prefix a single quote; or, Excel-resistant, a tab inside the quotes. It warns these can fail after save/reopen in Excel ([OWASP](https://community.owasp.org/attacks/CSV_Injection)).
Plan: RFC 4180 quoting (double quotes, doubled internal quotes, quote fields containing comma, quote, CR/LF); for text fields that begin (after optional whitespace) with any listed character, prefix `'`. Numeric columns come from our own bigint formatting, so a legitimately negative number is not a text field and is never prefixed. Includes the full-width variants, which the playbook list omits; flagging this addition.

## 9. Next.js and OpenAPI generator

- Next.js latest on npm: **16.4.5** (checked 2026-11-05). App Router is the default; I have not yet read the v16 docs, so conventions are **[unverified]** until task 3.1.
- Generator: `openapi-typescript` **7.13.0** (types only, no runtime client). Candidate to propose at 3.1; it is not in the playbook's allowed list, which says "one OpenAPI-to-types generator chosen in research", so choosing it here is within the list.
- Other current versions seen: typescript 7.0.2, vitest 5.1.0, zod 4.6.7, fastify 5.12.8, tsup 9.0.0. I have not checked compatibility between them (for example typescript-eslint support for TypeScript 7). To verify in 0.2.
