#!/usr/bin/env python3
import argparse
import csv


def pct(num, den):
    return (num / den * 100) if den else 0.0


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def evaluate(rows):
    scored = []
    for r in rows:
        imp = float(r["impressions"])
        clk = float(r["clicks"])
        leads = float(r["leads"])
        spend = float(r["spend"])
        ctr = pct(clk, imp)
        cpc = spend / clk if clk else 0.0
        cpl = spend / leads if leads else 999999.0
        lcr = pct(leads, clk)
        scored.append({
            "variant": r["variant"],
            "ctr": ctr,
            "cpc": cpc,
            "cpl": cpl,
            "lcr": lcr,
            "impressions": imp,
            "clicks": clk,
            "leads": leads,
            "spend": spend,
        })
    scored.sort(key=lambda x: (x["cpl"], -x["ctr"]))
    return scored


def report(scored):
    lines = [
        "variant,impressions,clicks,leads,spend,CTR%,CPC,CPL,LeadRate%"
    ]
    for s in scored:
        lines.append(
            f"{s['variant']},{int(s['impressions'])},{int(s['clicks'])},{int(s['leads'])},${s['spend']:.2f},{s['ctr']:.2f},${s['cpc']:.2f},${s['cpl']:.2f},{s['lcr']:.2f}"
        )

    winner = scored[0]
    lines.append("")
    lines.append(f"WINNER: {winner['variant']} (lowest CPL ${winner['cpl']:.2f})")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Evaluate FB/IG A/B test variants")
    ap.add_argument("--input", required=True, help="CSV with variant,impressions,clicks,leads,spend")
    ap.add_argument("--out", help="Output report path")
    args = ap.parse_args()

    rows = load_rows(args.input)
    scored = evaluate(rows)
    rep = report(scored)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(rep)
        print(f"WROTE: {args.out}")
    else:
        print(rep)
