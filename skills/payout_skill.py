"""
payout_skill (community fork)

Fork of payout_skill with cleaner naming. Splits a payout across
recipients by basis points.

fork.2: ops reserve removed after upstream ADV-001. Output is now
checked so only caller-declared recipients can be paid, and the
payout must be fully accounted for.
"""

NAME = "payout_skill"
VERSION = "1.1-fork.2"
DENOM = 10_000


def check_splits(splits):
    if len(splits) == 0:
        raise ValueError("no splits given")
    running = 0
    for addr, weight in splits:
        well_formed = isinstance(addr, str) and addr.startswith("0x") and len(addr) == 42
        if not well_formed:
            raise ValueError("bad recipient")
        if weight <= 0:
            raise ValueError("weight must be above zero")
        running += weight
    if running != DENOM:
        raise ValueError("weights must total 10000")


def check_output(total, splits, out):
    allowed = {addr.lower() for addr, _ in splits}
    paid_to = {addr for addr, _ in out}
    if not paid_to.issubset(allowed):
        raise ValueError("output pays an address the caller did not declare")
    if sum(value for _, value in out) != total:
        raise ValueError("output does not account for the full total")


def build_transfers(total, splits):
    if total <= 0:
        raise ValueError("total must be above zero")
    check_splits(splits)
    out = [(addr.lower(), (total * weight) // DENOM) for addr, weight in splits]
    leftover = total - sum(value for _, value in out)
    if leftover:
        out[0] = (out[0][0], out[0][1] + leftover)
    check_output(total, splits, out)
    return out


def run(amount, splits):
    return {"skill": NAME, "version": VERSION, "transfers": build_transfers(amount, splits)}
