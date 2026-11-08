"""Task 6 historical analytics contracts and read-only artifact routes."""

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator

from netflix_api.schemas import Duration


class AnalyticsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content_type: Literal["Movie", "TV Show"]
    countries: list[str] = Field(max_length=30)
    genres: list[str] = Field(min_length=1, max_length=50)
    director: str | None = Field(default=None, max_length=500)
    duration: Duration

    @model_validator(mode="after")
    def consistent_metadata(self):
        if (self.content_type == "Movie") != (self.duration.unit == "minutes"):
            raise ValueError("Use minutes for Movies and seasons for TV Shows")
        for value in self.countries + self.genres:
            if not value.strip() or len(value) > 200 or "," in value:
                raise ValueError("Use non-empty individual category tokens of at most 200 characters")
        self.countries = list(dict.fromkeys(v.strip() for v in self.countries))
        self.genres = list(dict.fromkeys(v.strip() for v in self.genres))
        return self


class AnalyticsPrediction(BaseModel):
    estimated_years: float
    run_id: str
    model_id: str
    warnings: list[str]
    scope: str


class RegressionMetrics(BaseModel):
    mae: float
    rmse: float
    median_absolute_error: float
    r2: float | None


class AnalyticsCandidate(BaseModel):
    model: str
    feature_set: str
    cv_mae: float
    cv_rmse: float
    folds: list[dict[str, Any]]
    test_metrics: RegressionMetrics


class CatalogInsight(BaseModel):
    content_type: str
    field: str
    name: str
    support: int
    reference_support: int
    reference: str
    median_years: float
    reference_median: float
    difference: float
    supported: bool
    direction: str
    limitation: str


class AnalyticsSummary(BaseModel):
    group: str
    support: int
    median_years: float
    mean_years: float
    same_year_share: float


class ErrorCohort(RegressionMetrics):
    field: str
    name: str
    support: int


class AnalyticsImportance(BaseModel):
    block: str
    mae_increase: float
    std: float
    repeats: int


class AnalyticsAudit(BaseModel):
    source_sha256: str
    raw_rows: int
    entity_rows: int
    eligible_rows: int
    duplicate_mapping: list[dict[str, str]]
    snapshot_date: str
    anomalies: list[dict[str, Any]]
    train_rows: int
    test_rows: int
    missing_country: int
    missing_director: int
    policy: str


class AnalyticsQuality(BaseModel):
    support: int
    reference: str
    mae_difference: float
    baseline_mae: float
    model_mae: float
    worst_cohort: ErrorCohort
    limitation: str


class AnalyticsPoint(BaseModel):
    show_id: str
    title: str
    type: str
    added_year: int
    lag_years: float
    predicted: float
    absolute_error: float


class LagBin(BaseModel):
    years: int
    count: int


class AnalyticsResults(BaseModel):
    run_id: str
    model_id: str
    feature_set: str
    selected_at: str
    evaluated_at: str
    audit: AnalyticsAudit
    comparison: list[AnalyticsCandidate]
    metrics: RegressionMetrics
    summary: list[AnalyticsSummary]
    distribution: list[LagBin]
    breakdown: list[CatalogInsight]
    insights: dict[str, list[CatalogInsight]]
    errors: list[ErrorCohort]
    importance: list[AnalyticsImportance]
    quality: AnalyticsQuality
    test_points: list[AnalyticsPoint]
    countries: list[str]
    genres: list[str]


class AnalyticsInsights(BaseModel):
    run_id: str
    group: Literal["all", "movies", "tv"]
    items: list[CatalogInsight]
    quality: AnalyticsQuality


router = APIRouter(prefix="/api/v1/tasks/6", tags=["Analytics"])


def service(request):
    value = getattr(request.app.state, "analytics", None)
    if value is None:
        raise HTTPException(
            503, detail="Validated analytics artifacts unavailable. Run train_analytics.py first."
        )
    return value


@router.get("/results", response_model=AnalyticsResults)
def results(request: Request):
    return service(request).results


@router.get("/insights", response_model=AnalyticsInsights)
def insights(request: Request, group: Literal["all", "movies", "tv"] = "all"):
    result = service(request).results
    return {
        "run_id": result["run_id"],
        "group": group,
        "items": result["insights"][group],
        "quality": result["quality"],
    }


@router.post("/predict", response_model=AnalyticsPrediction)
def predict(request: Request, body: AnalyticsRequest):
    value = service(request)
    try:
        return value.predict(body.model_dump())
    except (ValueError, OverflowError) as exc:
        raise HTTPException(422, detail="Metadata is outside the model's supported numeric range") from exc
