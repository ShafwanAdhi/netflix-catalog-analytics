# Catalog Analytics: modeling guide

Analyze the calendar-year difference between original release and catalog entry. Compare metadata-based regression models and inspect scoped historical insights. The target is not a measure of commercial success, popularity or exact elapsed time.

Target: `year(date_added) - release_year`, a calendar-year difference in the September 25, 2021 catalog. The CSV has no views, revenue, engagement or viewer scores. This is not exact elapsed time, prospective waiting time or commercial success.

## Reproduce

Use the root setup and reviewed source at `data/raw/Dataset.csv`:

```powershell
uv run python scripts/train_analytics.py
uv run python scripts/build_analytics_notebook.py
pnpm dev
```

Training creates and validates a new immutable run before activation. Restart the API afterward. Browsing never trains. `NETFLIX_LAB_BUNDLE` remains specific.

Routes: `/overview`, `/insights`, `/evaluation`, `/methodology`. Scope query: `group=all|movies|tv`. Predictions accept metadata, not release/addition years. Export contains scoped stored insights, references, support and run ID.

## Frozen results

Run `20261106T131312231321Z`: **ridge_advanced_10**, CV MAE **3.8996 years**. Test MAE **4.3615**, RMSE **8.0973**, median absolute error **1.6586**, R² **0.1629**; global median baseline MAE **4.9680**. This improvement does not establish strong predictive quality. Partial 2021 has the largest addition-year MAE **4.8992**, n=1,498.

8,790 raw rows become 8,783 entities; 14 negative differences are audited/excluded. Of 8,769 eligible titles, 5,395 train through 2019 and 3,374 test in 2020–2021. Serving remains training-only. Survivorship and backfills prevent true point-in-time generalization claims.

- [Methodology](methodology.md)
- [Dataset card](dataset-card.md)
- [Model card](model-card.md)
- [Project capabilities](capabilities.md)
- [Report](../../reports/task-06/final_report.md)
- [Executed notebook](../../notebooks/task-06/01_analytics.ipynb)
