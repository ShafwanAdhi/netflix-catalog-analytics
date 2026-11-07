"""Trusted immutable artifact validation and shared inference."""

from pathlib import Path

import joblib
import numpy as np
import sklearn

from netflix_ml.shared.io import digest, read_json, root
from netflix_ml.tasks.task_06.features import input_frame, tokens


class Analytics:
    def __init__(self, bundle):
        required = {
            "pipeline.joblib",
            "metadata.json",
            "results.json",
            "selection.json",
            "manifest.csv",
            "cv_manifest.csv",
            "test_predictions.csv",
            "audit.json",
            "insights.json",
            "config.json",
        }
        checksums = read_json(bundle / "checksums.json")
        if not required <= checksums.keys():
            raise ValueError("Incomplete Task 6 checksum manifest")
        for name, expected in checksums.items():
            if Path(name).name != name or digest(bundle / name) != expected:
                raise ValueError("Task 6 artifact integrity check failed")
        self.metadata = read_json(bundle / "metadata.json")
        self.results = read_json(bundle / "results.json")
        selection = read_json(bundle / "selection.json")
        if (
            self.metadata["sklearn"] != sklearn.__version__
            or self.metadata["run_id"] != self.results["run_id"]
            or selection["model"] != self.results["model_id"]
        ):
            raise ValueError("Task 6 environment or identity mismatch")
        self.pipeline = joblib.load(bundle / "pipeline.joblib")

    def predict(self, body):
        warnings = []
        for field in ["countries", "genres"]:
            unknown = sorted(set(body[field]) - set(self.metadata[field]))
            if unknown:
                warnings.append(
                    f"Unseen {field}: {', '.join(unknown)}; learned category indicators are unavailable."
                )
        low, high = self.metadata["duration_ranges"][body["content_type"]]
        if not low <= body["duration"]["value"] <= high:
            warnings.append(f"Duration is outside the historical training range ({low}–{high}).")
        if not tokens(body.get("director") or "Not Given"):
            warnings.append("Director metadata is unavailable; represented as missing.")
        with np.errstate(over="ignore", invalid="ignore"):
            estimate = float(self.pipeline.predict(input_frame(body))[0])
        if not np.isfinite(estimate):
            raise ValueError("Metadata is outside the model's finite prediction range")
        return {
            "estimated_years": estimate,
            "run_id": self.metadata["run_id"],
            "model_id": self.metadata["model_id"],
            "warnings": warnings,
            "scope": "Historical metadata association; calendar-year difference, not a current acquisition forecast or success score.",
        }


def load_analytics():
    pointer = read_json(root() / "artifacts/task-06/active.json")
    run_id = pointer["run_id"]
    if Path(run_id).name != run_id:
        raise ValueError("Invalid Task 6 run identity")
    bundle = root() / "artifacts/task-06" / run_id
    if digest(bundle / "checksums.json") != pointer["checksums_sha256"]:
        raise ValueError("Task 6 checksum manifest does not match active pointer")
    return Analytics(bundle)
