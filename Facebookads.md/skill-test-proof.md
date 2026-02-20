# Skill Test Proof — Clean Up Bros Social Growth

## 1) social-weekly-planner
- Skill file: `skills/social-weekly-planner/SKILL.md`
- Script: `scripts/social_growth_weekly_planner.py`
- Test command run:
  - `python3 scripts/social_growth_weekly_planner.py --start-date 2026-02-23 --suburb Liverpool --bedrooms 3 --out references/social-growth/weekly-plan.md`
- Proof log: `logs/skill-tests/social-weekly-planner-test.log`
- Result: 7-day plan generated successfully with pillar/format/hook/CTA rotation.

## 2) social-ab-test-optimizer
- Skill file: `skills/social-ab-test-optimizer/SKILL.md`
- Script: `scripts/social_ad_ab_test_tracker.py`
- Sample input: `references/social-growth/sample-ab-test.csv`
- Test command run:
  - `python3 scripts/social_ad_ab_test_tracker.py --input references/social-growth/sample-ab-test.csv --out logs/skill-tests/ab-test-report.txt`
- Proof log: `logs/skill-tests/social-ab-test-optimizer-test.log`
- Result: Variants ranked by CPL; winner selected = `B_Checklist_Form` with CPL `$16.50`.
