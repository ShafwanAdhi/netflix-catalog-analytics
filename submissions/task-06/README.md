# Task 6 submission

Prepared locally for private review, not externally submitted. Run `20261106T131312231321Z`. [Requirements](../../docs/tasks/task-06/requirements.md), [report](../../reports/task-06/final_report.md), [methodology](../../docs/tasks/task-06/methodology.md).

Includes source, configs, lockfiles, OpenAPI/types, tests, four active bundles, reports, executed notebook, seven screenshots and recorded checks. Derived title metadata is for private review. Excludes raw/processed CSVs, dependencies, caches, builds, inactive runs and previous ZIPs. Historical Task 3–5 ZIPs stay unchanged; their evidence belongs to historical snapshots.

## Replay and package

Build with `pnpm build`, then serve with `uv run uvicorn netflix_api.main:app --host 127.0.0.1 --port 8000`. In another terminal:

```powershell
New-Item -ItemType Directory -Force output/playwright/task-06 | Out-Null
npx --yes --package @playwright/cli playwright-cli -s=analytics open http://127.0.0.1:8000/tasks/6/overview --browser chrome
npx --yes --package @playwright/cli playwright-cli -s=analytics run-code --filename=scripts/browser-check-analytics.js --json | Out-File -Encoding utf8 output/playwright/task-06/browser-result.json
```

Visually inspect all seven screenshots, then:

```powershell
uv run python scripts/verify_analytics_submission.py --record-browser --checks --package
npx --yes --package @playwright/cli playwright-cli -s=analytics close
```

`--package` alone verifies existing evidence. The verifier refuses stale source/docs/configs, failed command logs, altered captures/exports, bundle mismatches or unexecuted notebook. A new run requires notebook/report regeneration, API restart, browser replay and current documentation. Serving needs no CSV; full data tests/retraining need original source and Task 3 preparation.

## Demo

1. Overview: target, eligible population, anomalies, partial snapshot.
2. Insights: scope, references, support and real CSV export.
3. Estimate: Movie/TV units, metadata, actual estimate and caveats.
4. Evaluation: feature comparison, baseline, cohort errors, importance.
5. Methodology: chronology, feature exclusion, immutable artifacts.
6. Tablet/mobile, Task 3–5 regression, notebook and verification records.

No GitHub publication, video, public hosting, portal upload or receipt is claimed. Docker Engine was unavailable; configuration includes all bundles but image execution is unverified.
