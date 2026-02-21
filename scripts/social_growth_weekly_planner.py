#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta

PILLARS = [
    "Transformation Proof",
    "Speed + Reliability",
    "Trust Signals",
    "Local Relevance",
    "Education/Objection Handling",
]

HOOKS = [
    "Moving out in {suburb} this week? Don’t risk your bond on the final clean.",
    "We cleaned this {bedrooms}-bed home in {suburb} in under 4 hours — here’s the result.",
    "Real estate inspection in 48 hours? Use this pre-inspection clean checklist.",
    "Western Sydney Airbnb hosts: same-day turnover is possible if this is done first.",
    "Most cleaners skip these 3 end-of-lease items (agents check them first).",
]

CTAS = [
    "DM 'QUOTE' for same-day estimate",
    "Tap to check this week’s availability",
    "Comment 'CHECKLIST' and we’ll send it",
    "Call now for priority booking",
]

def build_plan(start_date: str, suburb: str, bedrooms: int):
    dt = datetime.strptime(start_date, "%Y-%m-%d")
    rows = []
    for i in range(7):
        d = dt + timedelta(days=i)
        pillar = PILLARS[i % len(PILLARS)]
        hook = HOOKS[i % len(HOOKS)].format(suburb=suburb, bedrooms=bedrooms)
        cta = CTAS[i % len(CTAS)]
        platform = "FB+IG Reel" if i % 2 == 0 else "FB+IG Carousel"
        rows.append((d.strftime("%a %Y-%m-%d"), pillar, platform, hook, cta))
    return rows


def to_markdown(rows):
    out = ["# 7-Day Social Plan", "", "| Day | Pillar | Format | Hook | CTA |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate 7-day FB/IG content plan for Clean Up Bros")
    p.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    p.add_argument("--suburb", default="Liverpool")
    p.add_argument("--bedrooms", type=int, default=3)
    p.add_argument("--out", help="Output markdown file path")
    args = p.parse_args()

    plan = build_plan(args.start_date, args.suburb, args.bedrooms)
    md = to_markdown(plan)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"WROTE: {args.out}")
    else:
        print(md)
