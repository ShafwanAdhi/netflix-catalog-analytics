"""Local JSON inference through the same validated Task 6 service as HTTP."""

import argparse
import json
from pathlib import Path

from netflix_api.analytics import AnalyticsRequest
from netflix_ml.tasks.task_06.service import load_analytics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    body = AnalyticsRequest.model_validate_json(args.input.read_text(encoding="utf-8"))
    print(json.dumps(load_analytics().predict(body.model_dump()), ensure_ascii=False, allow_nan=False))
