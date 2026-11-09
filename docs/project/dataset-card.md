# Catalog Analytics: dataset card

Historical ten-column catalog CSV. SHA-256 `90b02beeb554921f81d3b9a774d0f7766f6a65240162565f6b4082165dc2a1d3`. Original provenance and redistribution rights remain unverified. Raw and processed source CSVs are excluded from version control.

- Raw: 8,790; entity deduplication: 8,783, seven removed rows.
- Negative differences: 14, audited and excluded without date correction.
- Eligible: 8,769; training 5,395 through 2019; test 3,374 in 2020–2021.
- Snapshot ends September 25, 2021. Its final year is partial; older cohorts are not proven complete.
- `Not Given` denotes semantic missingness. Movie minutes and TV seasons are distinct units.
- No full original release date, commercial success, demand or viewer outcome is available.

Survivorship, retrospective backfills and TV season definitions limit interpretation. Serving uses bundled derived statistics and models; retraining/full data tests need the source. Derived title metadata supports reproducibility; source redistribution rights are not established.

## Provenance and reproduction boundary

The structured [provenance record](../../data/provenance.json) is bound to the audited source SHA-256 and is included in the generated dataset profile. **Upstream source unverified. Redistribution permission unverified.** Public candidate datasets were reviewed on 9 November 2026; none established the exact byte lineage and transformation history of this input. No upstream license is attributed to the supplied CSV.

Observed release years are 1925–2021; date-added values span 2008-01-01 through 2021-09-25. The maximum date-added value is not a known acquisition date. Acquisition date and upstream version remain unknown.

**Artifact inference** works with the bundled model without raw data. **Training reproduction** requires the exact supplied CSV with the documented hash; there is no verified public download instruction for that input. Raw CSV remains excluded from Git. Run `uv run python scripts/refresh_dataset.py` after changing an active run; the generator checks the provenance hash before emitting the profile.
