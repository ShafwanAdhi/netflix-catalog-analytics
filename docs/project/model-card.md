# Catalog Analytics: model card

Run `20261106T131312231321Z`: `ridge_advanced_10`, StandardScaler + Ridge(alpha=10), log1p target with nonnegative inverse estimates. Selected by CV MAE 3.8996 years among 18 specifications including two baselines. Fitted on 5,395 training titles; vocabulary/scaling are training-fitted.

Chronological test n=3,374: MAE 4.3615 years, RMSE 8.0973, median absolute error 1.6586, R² 0.1629. Global median MAE 4.9680. Worst addition-year cohort is partial 2021: MAE 4.8992, n=1,498. Long-tail and cohort errors remain visible; improvement over one baseline does not establish strong predictive performance.

Intended use: educational catalog metadata analysis. Inputs: type, countries, genres, director (count/missingness only), duration. Output: historical calendar-year-difference estimate, warnings and run/model identity. Unseen labels lack learned category indicators; derived counts can still contribute. Out-of-training-range duration triggers a warning.

Not intended: prospective acquisition timing, official dates, commercial success, demand, causal policy or investment decisions. No interval is supplied. Partial 2021, survivorship, anomalies, correlated features, overlapping labels and sparse early CV history limit interpretation. No test-based reselection/refit occurs. Permutation importance is diagnostic only.
