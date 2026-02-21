---
name: social-ab-test-optimizer
description: Score FB/IG ad variants by CTR, CPC, CPL and select winner using execution-safe rules. Use when reviewing paid social performance and deciding which creative/offer to scale.
---

# Social A/B Test Optimizer

## Purpose
Turn raw variant performance data into a clear winner decision.

## Required CSV Columns
- variant
- impressions
- clicks
- leads
- spend

## Command
```bash
python3 scripts/social_ad_ab_test_tracker.py --input references/social-growth/sample-ab-test.csv --out logs/skill-tests/ab-test-report.txt
```

## Decision Logic
1. Rank by lowest CPL (primary)
2. Break ties by higher CTR

## Output
- Ranked variant report
- Explicit winner line for budget reallocation

## Operating Rule
Only decide winners after minimum threshold per variant:
- 1,500 impressions OR 20 clicks OR 5 leads
