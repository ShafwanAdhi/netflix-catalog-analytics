"""Frozen chronological experiments and audited, deterministic catalog insights."""

import itertools
from datetime import UTC, datetime

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from threadpoolctl import threadpool_limits

from netflix_ml.shared.dataset import validate
from netflix_ml.shared.io import digest, read_json, root, write_json
from netflix_ml.tasks.task_06.features import FEATURES, tokens
from netflix_ml.tasks.task_06.insights import GROUPS, build_insights
from netflix_ml.tasks.task_06.models import MedianBaseline, NonnegativeLogRegressor, metrics


def prepare(config):
    source = root() / "data/raw/Dataset.csv"
    if digest(source) != config["source_sha256"]:
        raise ValueError("Source hash differs from reviewed snapshot")
    raw = pd.read_csv(source)
    validate(raw)
    raw["entity_key"] = (
        raw.title.str.strip().str.casefold() + "|" + raw.type + "|" + raw.release_year.astype(str)
    )
    seen, removed = {}, []
    for row in raw.itertuples():
        if row.entity_key in seen:
            removed.append({"removed_id": row.show_id, "retained_id": seen[row.entity_key]})
        else:
            seen[row.entity_key] = row.show_id
    entities = raw.drop_duplicates("entity_key").copy()
    dates = pd.to_datetime(entities.date_added.str.strip())
    entities["added_year"] = dates.dt.year
    entities["lag_years"] = entities.added_year - entities.release_year
    anomalies = entities.loc[entities.lag_years < 0]
    frame = entities.loc[entities.lag_years >= 0].reset_index(drop=True)
    frame["split"] = np.where(frame.added_year <= config["training_end"], "train", "test")
    audit = {
        "source_sha256": digest(source),
        "raw_rows": len(raw),
        "entity_rows": len(entities),
        "eligible_rows": len(frame),
        "duplicate_mapping": removed,
        "snapshot_date": dates.max().strftime("%Y-%m-%d"),
        "anomalies": anomalies[
            ["show_id", "title", "type", "release_year", "date_added", "lag_years"]
        ].to_dict("records"),
        "train_rows": int(frame.split.eq("train").sum()),
        "test_rows": int(frame.split.eq("test").sum()),
        "missing_country": int(entities.country.eq("Not Given").sum()),
        "missing_director": int(entities.director.eq("Not Given").sum()),
        "policy": "First row per normalized title/type/year; negative lags audited and excluded. No outlier trimming.",
    }
    return frame, audit


def candidates(config):
    yield "median_global", "baseline", MedianBaseline()
    yield "median_type", "baseline", MedianBaseline(True)
    for advanced in [False, True]:
        label = "advanced" if advanced else "base"
        for alpha in config["ridge_alpha"]:
            yield f"ridge_{label}_{alpha}", label, NonnegativeLogRegressor("ridge", advanced, alpha=alpha)
        for depth, leaf in itertools.product(config["forest_depth"], config["forest_min_leaf"]):
            yield (
                f"forest_{label}_{depth}_{leaf}",
                label,
                NonnegativeLogRegressor(
                    "forest",
                    advanced,
                    depth=depth,
                    leaf=leaf,
                    trees=config["forest_trees"],
                    seed=config["seed"],
                ),
            )


def breakdown(test, predicted):
    output = []
    values = test.copy()
    values["prediction"] = predicted
    values["target_band"] = np.where(
        values.lag_years.eq(0), "0", np.where(values.lag_years.le(5), "1-5", ">5")
    )
    for field in ["type", "added_year", "target_band"]:
        for name, subset in values.groupby(field, sort=True):
            output.append(
                {
                    "field": field,
                    "name": str(name),
                    "support": len(subset),
                    **metrics(subset.lag_years, subset.prediction),
                }
            )
    return output


def permutation_blocks(model, test, repeats, seed):
    baseline = metrics(test.lag_years, model.predict(test[FEATURES]))["mae"]
    rng = np.random.default_rng(seed)
    output = []
    blocks = {
        "type_duration": ["type", "duration"],
        "country": ["country"],
        "genre": ["listed_in"],
        "director": ["director"],
    }
    for block, columns in blocks.items():
        differences = []
        for _ in range(repeats):
            shuffled = test[FEATURES].copy()
            # Keep Movie/minutes and TV/seasons paired; independent type shuffles violate the input contract.
            indices = rng.permutation(len(shuffled))
            shuffled[columns] = shuffled[columns].iloc[indices].to_numpy()
            differences.append(metrics(test.lag_years, model.predict(shuffled))["mae"] - baseline)
        output.append(
            {
                "block": block,
                "mae_increase": float(np.mean(differences)),
                "std": float(np.std(differences)),
                "repeats": repeats,
            }
        )
    return sorted(output, key=lambda r: (-r["mae_increase"], r["block"]))


def train():
    base = root()
    config = read_json(base / "configs/task-06/experiment.json")
    frame, audit = prepare(config)
    train_rows = frame.loc[frame.split == "train"]
    test = frame.loc[frame.split == "test"]
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    bundle = base / "artifacts/task-06" / run_id
    bundle.mkdir(parents=True, exist_ok=False)
    frame[["show_id", "entity_key", "added_year", "release_year", "lag_years", "split"]].to_csv(
        bundle / "manifest.csv", index=False
    )
    cv_membership = []
    for year in config["cv_years"]:
        fold = train_rows.loc[train_rows.added_year <= year]
        cv_membership.extend(
            {"fold": year, "show_id": r.show_id, "role": "fit" if r.added_year < year else "validation"}
            for r in fold.itertuples()
        )
    pd.DataFrame(cv_membership).to_csv(bundle / "cv_manifest.csv", index=False)
    comparison, fitted = [], {}
    with threadpool_limits(limits=1):
        for name, feature_set, model in candidates(config):
            scores = []
            for year in config["cv_years"]:
                fit = train_rows.loc[train_rows.added_year < year]
                validation = train_rows.loc[train_rows.added_year == year]
                model.fit(fit[FEATURES], fit.lag_years)
                scores.append(
                    {
                        "validation_year": year,
                        "fit_rows": len(fit),
                        "validation_rows": len(validation),
                        **metrics(validation.lag_years, model.predict(validation[FEATURES])),
                    }
                )
            row = {
                "model": name,
                "feature_set": feature_set,
                "folds": scores,
                "cv_mae": float(np.mean([s["mae"] for s in scores])),
                "cv_rmse": float(np.mean([s["rmse"] for s in scores])),
            }
            comparison.append(row)
            fitted[name] = model.fit(train_rows[FEATURES], train_rows.lag_years)
            print(f"{name}: CV MAE {row['cv_mae']:.4f}", flush=True)
        selected = min(comparison, key=lambda r: (r["cv_mae"], r["cv_rmse"], comparison.index(r)))
        selection = {
            "model": selected["model"],
            "feature_set": selected["feature_set"],
            "selected_at": datetime.now(UTC).isoformat(),
            "rule": config["selection"],
            "candidates": comparison,
        }
        write_json(bundle / "selection.json", selection)
        # Selection is persisted before any final test metrics are accessed.
        for row in comparison:
            row["test_metrics"] = metrics(test.lag_years, fitted[row["model"]].predict(test[FEATURES]))
        model = fitted[selected["model"]]
        predicted = model.predict(test[FEATURES])
        errors = breakdown(test, predicted)
        importance = permutation_blocks(model, test, config["permutation_repeats"], config["seed"])
    predictions = test[["show_id", "title", "type", "added_year", "lag_years"]].copy()
    predictions["predicted"] = predicted
    predictions["absolute_error"] = abs(predictions.lag_years - predictions.predicted)
    predictions.to_csv(bundle / "test_predictions.csv", index=False)
    groups, insights = build_insights(frame, config["minimum_support"])
    summary = []
    for scope, kind in GROUPS.items():
        subset = frame if kind is None else frame.loc[frame.type == kind]
        summary.append(
            {
                "group": scope,
                "support": len(subset),
                "median_years": float(subset.lag_years.median()),
                "mean_years": float(subset.lag_years.mean()),
                "same_year_share": float(subset.lag_years.eq(0).mean()),
            }
        )
    baseline = next(r for r in comparison if r["model"] == "median_global")["test_metrics"]["mae"]
    cohorts = [r for r in errors if r["field"] == "added_year"]
    quality = {
        "support": len(test),
        "reference": "Global median baseline on the same test rows",
        "mae_difference": selected["test_metrics"]["mae"] - baseline,
        "baseline_mae": baseline,
        "model_mae": selected["test_metrics"]["mae"],
        "worst_cohort": max(cohorts, key=lambda r: (r["mae"], r["name"])),
        "limitation": "Single historical snapshot; test diagnosis did not change selection. Partial 2021 coverage.",
    }
    metadata = {
        "run_id": run_id,
        "model_id": selected["model"],
        "sklearn": sklearn.__version__,
        "config": config,
        "feature_columns": FEATURES,
        "source_sha256": audit["source_sha256"],
        "countries": sorted({v for value in train_rows.country for v in tokens(value)}),
        "genres": sorted({v for value in train_rows.listed_in for v in tokens(value)}),
        "duration_ranges": {
            kind: [
                int(g.duration.str.split().str[0].astype(int).min()),
                int(g.duration.str.split().str[0].astype(int).max()),
            ]
            for kind, g in train_rows.groupby("type")
        },
    }
    result = {
        "run_id": run_id,
        "model_id": selected["model"],
        "feature_set": selected["feature_set"],
        "selected_at": selection["selected_at"],
        "evaluated_at": datetime.now(UTC).isoformat(),
        "audit": audit,
        "comparison": comparison,
        "metrics": selected["test_metrics"],
        "summary": summary,
        "distribution": [
            {"years": int(y), "count": int(n)} for y, n in frame.lag_years.value_counts().sort_index().items()
        ],
        "breakdown": groups,
        "insights": insights,
        "errors": errors,
        "importance": importance,
        "quality": quality,
        "test_points": predictions.iloc[
            np.linspace(0, len(predictions) - 1, min(500, len(predictions)), dtype=int)
        ].to_dict("records"),
        "countries": metadata["countries"],
        "genres": metadata["genres"],
    }
    joblib.dump(model, bundle / "pipeline.joblib", compress=3)
    write_json(bundle / "metadata.json", metadata)
    write_json(bundle / "results.json", result)
    write_json(bundle / "audit.json", audit)
    write_json(bundle / "insights.json", insights)
    write_json(bundle / "config.json", config)
    write_json(bundle / "checksums.json", {p.name: digest(p) for p in bundle.iterdir() if p.is_file()})
    from netflix_ml.tasks.task_06.service import Analytics

    Analytics(bundle)
    render_report(result)
    write_json(
        base / "artifacts/task-06/active.json",
        {"run_id": run_id, "checksums_sha256": digest(bundle / "checksums.json")},
    )
    print(f"Activated Task 6 {run_id}: {selected['model']}", flush=True)
    return result


def render_report(result):
    folder = root() / "reports/task-06"
    figures = folder / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(
        [r["years"] for r in result["distribution"]],
        [r["count"] for r in result["distribution"]],
        color="#ad292e",
    )
    ax.set(
        xlabel="Calendar-year difference",
        ylabel="Eligible titles",
        title="Observed release-to-catalog difference",
    )
    fig.tight_layout()
    fig.savefig(figures / "distribution.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 6))
    points = result["test_points"]
    ax.scatter(
        [r["lag_years"] for r in points], [r["predicted"] for r in points], s=10, alpha=0.35, color="#ad292e"
    )
    maximum = max(r["lag_years"] for r in points)
    ax.plot([0, maximum], [0, maximum], color="#555555", linestyle="--")
    ax.set(
        xlabel="Actual years",
        ylabel="Predicted years",
        title="Chronological held-out test (deterministic sample)",
    )
    fig.tight_layout()
    fig.savefig(figures / "test-predictions.png", dpi=150)
    plt.close(fig)
    text = f"# Task 6 — Historical Catalog Entry Analytics\n\nRun `{result['run_id']}`. Selected **{result['model_id']}** ({result['feature_set']}).\n\n"
    text += "Target is addition calendar year minus release year, not elapsed duration or commercial success. No release year or addition date is a predictor.\n\n"
    text += f"Audit: {result['audit']['entity_rows']} entities, {len(result['audit']['anomalies'])} negative anomalies excluded; {result['audit']['eligible_rows']} eligible, {result['audit']['train_rows']} training and {result['audit']['test_rows']} test. Snapshot {result['audit']['snapshot_date']}; 2021 is partial.\n\n"
    text += "## Frozen model comparison\n\n| Model | Features | CV MAE | Test MAE | RMSE | Median AE | R² |\n| --- | --- | ---: | ---: | ---: | ---: | ---: |\n"
    for row in result["comparison"]:
        m = row["test_metrics"]
        text += f"| {row['model']} | {row['feature_set']} | {row['cv_mae']:.4f} | {m['mae']:.4f} | {m['rmse']:.4f} | {m['median_absolute_error']:.4f} | {m['r2']} |\n"
    q = result["quality"]
    text += f"\nSelected-model MAE minus global-median baseline MAE: **{q['mae_difference']:+.4f} years**; negative means lower error. Worst addition-year cohort: {q['worst_cohort']['name']}, support {q['worst_cohort']['support']}, MAE {q['worst_cohort']['mae']:.4f}.\n\n"
    text += "## Automated descriptive insights\n\n"
    for scope, rows in result["insights"].items():
        text += f"### {scope}\n\n"
        for row in rows:
            text += f"- {row['content_type']} / {row['field']} / {row['name']}: median {row['median_years']:.1f} vs {row['reference_median']:.1f}; difference {row['difference']:+.1f} years, n={row['support']} (reference n={row['reference_support']}).\n"
    text += "\n## Interpretation and follow-up\n\nDifferences identify cohorts to inspect, not an acquisition policy or success ranking. Consider whether observed metadata, season definitions, and catalog backfills explain the differences before collecting additional outcome data. Country/genre groups overlap and minimum n=30 is a support rule, not statistical significance.\n\nModels train through 2019; validation years are 2017/2018/2019 and test is 2020–2021. The selected pipeline remains training-only. Snapshot survivorship, missing original release dates, incomplete 2021, and changing catalog policies limit all extrapolation. TV release years can refer to later seasons. Permutation importance is post-selection test diagnosis, not a causal effect or selection criterion. No uncertainty interval or current forecast is claimed.\n"
    (folder / "final_report.md").write_text(text, encoding="utf-8")
