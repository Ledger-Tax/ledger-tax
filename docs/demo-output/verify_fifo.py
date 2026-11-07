"""Independent FIFO check: recomputes gains from the downloaded events.csv with exact fractions and
compares them with the downloaded gains.csv. Shares no code with the TypeScript implementation."""
import csv
import sys
from collections import defaultdict, deque
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

sp = sys.argv[1]
ISSUER = sys.argv[2]
PRICES = {  # the price file used in the walkthrough, per UTC day
    ("native", "2026-11-06"): Fraction("0.10"),
    (f"TEST:{ISSUER}", "2026-11-06"): Fraction("1.50"),
}


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))


def cents(x: Fraction) -> str:
    return str(Decimal(x.numerator).__truediv__(Decimal(x.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


events = rows(f"{sp}/events.csv")
lots = defaultdict(deque)  # asset -> deque of [qty, cost or None, time, event_id]
gains, problems = [], []


def price(asset, time):
    return PRICES.get((asset, time[:10]))


def consume(asset, qty, proceeds, ev):
    """FIFO. proceeds None = silent use (fees, transfers). Returns uncovered quantity."""
    left, taken, allocated = qty, Fraction(0), Fraction(0)
    while left > 0 and lots[asset]:
        lot = lots[asset][0]
        take = min(left, lot[0])
        cost = None
        if lot[1] is not None:
            cost = lot[1] if take == lot[0] else lot[1] * take / lot[0]
            lot[1] -= cost
        lot[0] -= take
        left -= take
        taken += take
        if proceeds is not None:
            cum = proceeds * taken / qty
            part, allocated = cum - allocated, cum
            if cost is None:
                problems.append(("unknown_cost_basis", ev["event_id"]))
            else:
                days = (ts(ev["time"]) - ts(lot[2])).days
                gains.append((lot[2][:10], ev["time"][:10], asset, take, part, cost, part - cost, days, ev["event_id"], lot[3]))
        if lot[0] == 0:
            lots[asset].popleft()
    return left


for ev in events:
    t, label = ev["type"], ev["label"]
    if label == "ignore":
        continue
    amount = Fraction(ev["amount"]) if ev["amount"] else None
    asset = ev["asset"]
    inflow = t in ("payment_in", "account_funded", "claimable_claimed") or (t == "account_merged" and ev["direction"] == "in")
    outflow = t == "payment_out" or (t == "account_merged" and ev["direction"] == "out")
    if t == "fee":
        consume(asset, amount, None, ev)
    elif t == "trade":
        got_asset, got = ev["counter_asset"], Fraction(ev["counter_amount"])
        p_got, p_sold = price(got_asset, ev["time"]), price(asset, ev["time"])
        value = got * p_got if p_got is not None else (amount * p_sold if p_sold is not None else None)
        if value is None:
            problems.append(("missing_price", ev["event_id"]))
            consume(asset, amount, None, ev)
            lots[got_asset].append([got, None, ev["time"], ev["event_id"]])
        else:
            left = consume(asset, amount, value, ev)
            if left > 0:
                problems.append(("insufficient_lots", ev["event_id"]))
            lots[got_asset].append([got, value, ev["time"], ev["event_id"]])
    elif inflow and amount is not None:
        cost = None
        if label == "income":
            p = price(asset, ev["time"])
            cost = amount * p if p is not None else None
            if p is None:
                problems.append(("missing_price", ev["event_id"]))
        lots[asset].append([amount, cost, ev["time"], ev["event_id"]])
    elif outflow and amount is not None:
        if label == "disposal":
            p = price(asset, ev["time"])
            if p is None:
                problems.append(("missing_price", ev["event_id"]))
                consume(asset, amount, None, ev)
            else:
                left = consume(asset, amount, amount * p, ev)
                if left > 0:
                    problems.append(("insufficient_lots", ev["event_id"]))
        else:
            consume(asset, amount, None, ev)

mine = [(g[0], g[1], g[2], f"{float(g[3]):.7f}", cents(g[4]), cents(g[5]), cents(g[6]), str(g[7])) for g in gains]
reported = [
    (r["acquired_date"], r["disposed_date"], r["asset"], r["quantity"], r["proceeds"], r["cost_basis"], r["gain"], r["holding_days"])
    for r in rows(f"{sp}/gains.csv")
    if r["status"] == "ok"
]
errors = [r["note"].split(":")[0] for r in rows(f"{sp}/gains.csv") if r["status"] == "error"]

print("independent rows:", len(mine), " reported rows:", len(reported))
for a, b in zip(mine, reported):
    print("MATCH " if a == b else "DIFF  ", a, "|" if a == b else "!=", b if a != b else "")
print("rows equal:", mine == reported)
print("independent problems:", sorted(p[0] for p in problems), " reported errors:", sorted(errors))
total = sum((g[6] for g in gains), Fraction(0))
print("independent total gain:", cents(total))
