# Task 6 — Historical Catalog Entry Analytics

Run `20261106T131312231321Z`. Selected **ridge_advanced_10** (advanced).

Target is addition calendar year minus release year, not elapsed duration or commercial success. No release year or addition date is a predictor.

Audit: 8783 entities, 14 negative anomalies excluded; 8769 eligible, 5395 training and 3374 test. Snapshot 2021-09-25; 2021 is partial.

## Frozen model comparison

| Model | Features | CV MAE | Test MAE | RMSE | Median AE | R² |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| median_global | baseline | 4.1137 | 4.9680 | 9.7785 | 1.0000 | -0.22075310107680224 |
| median_type | baseline | 4.1962 | 4.9680 | 9.7785 | 1.0000 | -0.22075310107680224 |
| ridge_base_0.1 | base | 3.9429 | 4.4492 | 8.5700 | 1.6410 | 0.06234966899599004 |
| ridge_base_1 | base | 3.9501 | 4.4288 | 8.4489 | 1.6455 | 0.08865086390613586 |
| ridge_base_10 | base | 3.9264 | 4.3265 | 7.9038 | 1.6574 | 0.20245090836192758 |
| ridge_base_100 | base | 4.0647 | 4.5867 | 8.5952 | 1.6121 | 0.05682399111556857 |
| forest_base_10_2 | base | 3.9573 | 4.2507 | 7.6665 | 1.5557 | 0.249638807255818 |
| forest_base_10_10 | base | 3.9172 | 4.2536 | 7.6527 | 1.5668 | 0.2523303195383463 |
| forest_base_None_2 | base | 3.9857 | 4.2169 | 7.5608 | 1.6610 | 0.2701780469222633 |
| forest_base_None_10 | base | 3.9128 | 4.2027 | 7.5750 | 1.5887 | 0.26742492353473524 |
| ridge_advanced_0.1 | advanced | 3.9591 | 4.4735 | 8.5715 | 1.6862 | 0.06201314935582758 |
| ridge_advanced_1 | advanced | 3.9594 | 4.4583 | 8.5230 | 1.6885 | 0.0726070986716566 |
| ridge_advanced_10 | advanced | 3.8996 | 4.3615 | 8.0973 | 1.6586 | 0.1629328341994455 |
| ridge_advanced_100 | advanced | 4.0436 | 4.4645 | 8.2636 | 1.6191 | 0.12819803740317637 |
| forest_advanced_10_2 | advanced | 3.9522 | 4.2589 | 7.6645 | 1.5515 | 0.2500127657068497 |
| forest_advanced_10_10 | advanced | 3.9104 | 4.2492 | 7.6482 | 1.5687 | 0.253199614678139 |
| forest_advanced_None_2 | advanced | 3.9695 | 4.2380 | 7.5819 | 1.6665 | 0.2661033295408687 |
| forest_advanced_None_10 | advanced | 3.9023 | 4.1950 | 7.5697 | 1.5888 | 0.2684623516775191 |

Selected-model MAE minus global-median baseline MAE: **-0.6064 years**; negative means lower error. Worst addition-year cohort: 2021, support 1498, MAE 4.8992.

## Automated descriptive insights

### all

- Movie / genre / Classic Movies: median 44.0 vs 2.0; difference +42.0 years, n=116 (reference n=6119).
- Movie / genre / Cult Movies: median 25.0 vs 2.0; difference +23.0 years, n=70 (reference n=6119).
- Movie / country / Hong Kong: median 12.0 vs 2.0; difference +10.0 years, n=75 (reference n=6119).
- Movie / country / Egypt: median 7.0 vs 2.0; difference +5.0 years, n=109 (reference n=6119).
- Movie / country / Thailand: median 4.5 vs 2.0; difference +2.5 years, n=42 (reference n=6119).
### movies

- Movie / genre / Classic Movies: median 44.0 vs 2.0; difference +42.0 years, n=116 (reference n=6119).
- Movie / genre / Cult Movies: median 25.0 vs 2.0; difference +23.0 years, n=70 (reference n=6119).
- Movie / country / Hong Kong: median 12.0 vs 2.0; difference +10.0 years, n=75 (reference n=6119).
- Movie / country / Egypt: median 7.0 vs 2.0; difference +5.0 years, n=109 (reference n=6119).
- Movie / country / Thailand: median 4.5 vs 2.0; difference +2.5 years, n=42 (reference n=6119).
### tv

- TV Show / country / Taiwan: median 2.0 vs 0.0; difference +2.0 years, n=71 (reference n=2650).
- TV Show / country / Turkey: median 2.0 vs 0.0; difference +2.0 years, n=30 (reference n=2650).
- TV Show / genre / Anime Series: median 1.0 vs 0.0; difference +1.0 years, n=174 (reference n=2650).
- TV Show / genre / British TV Shows: median 1.0 vs 0.0; difference +1.0 years, n=252 (reference n=2650).
- TV Show / country / Canada: median 1.0 vs 0.0; difference +1.0 years, n=82 (reference n=2650).

## Interpretation and follow-up

Differences identify cohorts to inspect, not an acquisition policy or success ranking. Consider whether observed metadata, season definitions, and catalog backfills explain the differences before collecting additional outcome data. Country/genre groups overlap and minimum n=30 is a support rule, not statistical significance.

Models train through 2019; validation years are 2017/2018/2019 and test is 2020–2021. The selected pipeline remains training-only. Snapshot survivorship, missing original release dates, incomplete 2021, and changing catalog policies limit all extrapolation. TV release years can refer to later seasons. Permutation importance is post-selection test diagnosis, not a causal effect or selection criterion. No uncertainty interval or current forecast is claimed.
