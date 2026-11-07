"""Task 6 chronology, leakage boundaries, frozen evidence and inference contracts."""

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from netflix_api.main import create_app
from netflix_ml.shared.io import read_json, root
from netflix_ml.tasks.task_06.features import FEATURES, AnalyticsEncoder, input_frame
from netflix_ml.tasks.task_06.insights import build_insights
from netflix_ml.tasks.task_06.models import MedianBaseline, metrics
from netflix_ml.tasks.task_06.service import Analytics, load_analytics
from netflix_ml.tasks.task_06.training import permutation_blocks, prepare


@pytest.fixture(scope="module")
def analytics():
    return load_analytics()


@pytest.fixture(scope="module")
def prepared(analytics):
    return prepare(analytics.metadata["config"])[0]


def body():
    return {
        "content_type": "Movie",
        "countries": ["United States"],
        "genres": ["Dramas"],
        "director": None,
        "duration": {"value": 100, "unit": "minutes"},
    }


def test_preparation_and_frozen_chronology(analytics, prepared):
    a = analytics.results["audit"]
    assert (a["entity_rows"], a["eligible_rows"], len(a["anomalies"])) == (8783, 8769, 14)
    assert len(a["duplicate_mapping"]) == 7
    assert prepared.lag_years.ge(0).all()
    assert np.array_equal(prepared.lag_years, prepared.added_year - prepared.release_year)
    train, test = prepared[prepared.split == "train"], prepared[prepared.split == "test"]
    assert train.added_year.max() == 2019 and test.added_year.min() == 2020
    assert not set(train.entity_key) & set(test.entity_key)
    bundle = root() / "artifacts/task-06" / analytics.metadata["run_id"]
    manifest = pd.read_csv(bundle / "manifest.csv")
    assert manifest.show_id.tolist() == prepared.show_id.tolist()
    folds = pd.read_csv(bundle / "cv_manifest.csv")
    lookup = prepared.set_index("show_id")
    for year, fold in folds.groupby("fold"):
        fit = lookup.loc[fold.loc[fold.role == "fit", "show_id"]]
        validation = lookup.loc[fold.loc[fold.role == "validation", "show_id"]]
        assert fit.added_year.max() < validation.added_year.min() == year
        assert set(fit.entity_key).isdisjoint(validation.entity_key)
        assert set(fit.index) | set(validation.index) == set(train.loc[train.added_year <= year, "show_id"])
    selection = read_json(bundle / "selection.json")
    assert "test_metrics" not in selection["candidates"][0]
    winner = min(selection["candidates"], key=lambda r: (r["cv_mae"], r["cv_rmse"]))
    assert winner["model"] == analytics.results["model_id"]
    assert selection["selected_at"] < analytics.results["evaluated_at"]


def test_encoder_allowlist_unknown_and_serialization(prepared, tmp_path):
    sample = prepared.head(30).copy()
    encoder = AnalyticsEncoder(True).fit(sample)
    expected = encoder.transform(sample).toarray()
    changed = sample.copy()
    for column in ["show_id", "title", "date_added", "release_year", "lag_years", "added_year"]:
        changed[column] = "forbidden future information"
    assert np.array_equal(expected, encoder.transform(changed).toarray())
    names = encoder.get_feature_names_out().copy()
    changed["country"] = "Unseen Country"
    changed["listed_in"] = "Unseen Genre"
    encoded = encoder.transform(changed).toarray()
    assert np.array_equal(names, encoder.get_feature_names_out())
    assert encoded.shape[1] == len(names)
    joblib.dump(encoder, tmp_path / "encoder.joblib")
    assert np.allclose(encoded, joblib.load(tmp_path / "encoder.joblib").transform(changed).toarray())


def test_baseline_fallback_and_saved_test_parity(analytics, prepared):
    sample = prepared.head(8).copy()
    baseline = MedianBaseline(True).fit(sample, sample.lag_years)
    sample["type"] = "Unseen Type"
    assert np.all(baseline.predict(sample) == baseline.median_)
    test = prepared[prepared.split == "test"]
    predicted = analytics.pipeline.predict(test[FEATURES])
    assert predicted.min() >= 0
    assert metrics(test.lag_years, predicted) == analytics.results["metrics"]
    bundle = root() / "artifacts/task-06" / analytics.metadata["run_id"]
    saved = pd.read_csv(bundle / "test_predictions.csv")
    assert np.allclose(predicted, saved.predicted)
    request = body()
    assert (
        analytics.predict(request)["estimated_years"] == analytics.pipeline.predict(input_frame(request))[0]
    )


def test_insight_support_determinism(analytics, prepared):
    groups, insights = build_insights(prepared, 30)
    assert insights == analytics.results["insights"]
    assert any(not row["supported"] for row in groups)
    assert all(row["supported"] == (row["support"] >= 30) for row in groups)
    for scope, rows in insights.items():
        assert len(rows) <= 5 and all(r["support"] >= 30 for r in rows)
        assert rows == sorted(
            rows, key=lambda r: (-abs(r["difference"]), r["name"], r["field"], r["content_type"])
        )
        if scope != "all":
            assert all(r["content_type"] == ("Movie" if scope == "movies" else "TV Show") for r in rows)


def test_api_validation_parity_and_independent_readiness(analytics, monkeypatch):
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/health").json()["task_6_ready"]
        assert client.get("/api/v1/tasks").json()[0]["status"] == "ready"
        response = client.get("/api/v1/tasks/6/results")
        assert response.status_code == 200 and response.json()["run_id"] == analytics.metadata["run_id"]
        for group in ["all", "movies", "tv"]:
            assert (
                client.get(f"/api/v1/tasks/6/insights?group={group}").json()["items"]
                == analytics.results["insights"][group]
            )
        assert client.get("/api/v1/tasks/6/insights?group=bad").status_code == 422
        assert client.post("/api/v1/tasks/6/predict", json=body()).json() == analytics.predict(body())
        for replacement in [
            {"duration": {"value": 1, "unit": "seasons"}},
            {"genres": []},
            {"release_year": 2020},
            {"countries": ["A,B"]},
            {"duration": {"value": 1.5, "unit": "minutes"}},
        ]:
            assert client.post("/api/v1/tasks/6/predict", json={**body(), **replacement}).status_code == 422
        unknown = {**body(), "countries": ["Unknown Country"], "genres": ["Unknown Genre"]}
        assert len(client.post("/api/v1/tasks/6/predict", json=unknown).json()["warnings"]) >= 2

    def unavailable():
        raise ValueError("Controlled Task 6 incompatibility")

    monkeypatch.setattr("netflix_api.main.load_analytics", unavailable)
    with TestClient(create_app()) as client:
        assert not client.get("/api/v1/health").json()["task_6_ready"]
        assert client.get("/api/v1/tasks/6/results").status_code == 503


def test_corrupt_and_incomplete_bundle_refused(tmp_path, analytics):
    import shutil

    from netflix_ml.shared.io import write_json

    write_json(tmp_path / "checksums.json", {})
    with pytest.raises(ValueError, match="Incomplete"):
        Analytics(tmp_path)
    bundle = root() / "artifacts/task-06" / analytics.metadata["run_id"]
    copy = tmp_path / "copy"
    shutil.copytree(bundle, copy)
    (copy / "results.json").write_text("{}")
    with pytest.raises(ValueError, match="integrity"):
        Analytics(copy)


def test_permutation_preserves_type_duration_units(prepared):
    class ContractModel:
        def predict(self, frame):
            assert ((frame.type == "Movie") == frame.duration.str.endswith("min")).all()
            return np.zeros(len(frame))

    result = permutation_blocks(ContractModel(), prepared.head(60), 3, 42)
    assert {r["block"] for r in result} == {"type_duration", "country", "genre", "director"}
    assert all(r["mae_increase"] == 0 for r in result)
