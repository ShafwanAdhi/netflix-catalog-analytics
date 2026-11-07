"""Reviewed source dataset contract, independent of other tasks."""

import pandas as pd

LABELS = [
    "G",
    "NC-17",
    "NR",
    "PG",
    "PG-13",
    "R",
    "TV-14",
    "TV-G",
    "TV-MA",
    "TV-PG",
    "TV-Y",
    "TV-Y7",
    "TV-Y7-FV",
    "UR",
]

COLUMNS = [
    "show_id",
    "type",
    "title",
    "director",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "listed_in",
]


def validate(frame: pd.DataFrame) -> None:
    if set(frame.columns) != set(COLUMNS):
        raise ValueError("Dataset does not match the ten-column contract")
    if frame.isna().any().any() or frame.show_id.duplicated().any():
        raise ValueError("Null cells or duplicate source IDs require review")
    if set(frame.rating) != set(LABELS) or not frame.type.isin(["Movie", "TV Show"]).all():
        raise ValueError("Unexpected target labels or content type")
    parts = frame.duration.str.extract(r"^(\d+) (min|Seasons?)$")
    if parts.isna().any().any() or (parts[0].astype(int) <= 0).any():
        raise ValueError("Invalid duration")
    if not ((frame.type == "Movie") == (parts[1] == "min")).all():
        raise ValueError("Duration unit does not match content type")
    pd.to_datetime(frame.date_added.str.strip(), errors="raise")
