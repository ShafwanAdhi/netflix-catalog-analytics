# Task 6 methodology

## Source and chronology

Verify the shared reviewed SHA-256 and ten-column contract. Keep the first row per trimmed casefolded title/type/year. Record seven removed rows. Audit 14 negative differences and exclude them from target statistics/modeling; do not correct dates or trim nonnegative outliers. Target is addition calendar year minus release year. Missing country/director tokens represent unavailable information.

Training ends in 2019; test covers 2020–2021. CV fits strictly before validation years 2017, 2018, 2019. This retrospective snapshot does not reconstruct a point-in-time archive. Partial 2021 remains eligible because each observed row has a defined target.

## Features and selection

Base: type, country/genre multi-hot encoding and separate movie-minute/TV-season values. Advanced: log duration, country/genre/director counts, country/director missingness and type×genre indicators. Exclude title, ID, release year, addition date and target derivatives. Director names are not individually encoded. Fit vocabulary/scalers inside each fold; unseen categories do not expand vocabulary.

Candidate order: global median, type median, then base and advanced models. Each set has Ridge alpha 0.1/1/10/100 and 200-tree forests with depth 10/unlimited × minimum leaf 2/10. Seed 42. Type baseline falls back to global median. Ridge/forest fit log1p targets and invert estimates, clipped at zero; the transformation may emphasize smaller targets.

Choose lowest mean CV MAE in years, then CV RMSE, then declared order. Persist selection before test. Evaluate all candidates transparently without reselection; keep the serving model trained through 2019. New training creates a unique run; there is no evaluate/overwrite-existing-run command. Repeated tuning against the same test cannot be described as an untouched holdout.

## Insight protocol

Catalog summaries use all eligible titles and are distinct from test metrics. Explode country/genre labels within type and compare group median with the full same-type median. Require n≥30 for ranking; keep smaller groups marked under-supported. Rank by absolute difference, name, field, type; at most five per scope. References include the compared group. Multi-label membership overlaps; the support threshold does not establish significance.

Post-selection permutation shuffles metadata blocks three times and recomputes derived features. Type and duration are shuffled together to preserve Movie/minute and TV/season units; country, genre and director are separate blocks. Report test MAE increase and standard deviation, including negative values. Correlation affects importance; no causal or selection interpretation applies. Record baseline MAE difference and worst addition-year cohort with support.

Insights store sample/reference sizes, medians, difference, direction and limitations. Follow-up hypotheses ask whether backfills, missingness or TV season definitions explain patterns; they do not prescribe acquisition or imply success.

## Operation and limits

Immutable bundles contain pipeline, source/config identity, configuration, manifests, selection, test predictions, audit, results and insights. Validate required files, checksums, run identity and scikit-learn version before activation/loading. Only trust project-generated joblib files; checksums do not establish arbitrary-file trust. Tasks load independently, without uploads or HTTP training.

Removed titles and future additions are absent. TV release year may describe a season. Year granularity prevents precise durations; 2021 is partial. No current forecast, demand estimate, confidence interval or commercial outcome is claimed.
