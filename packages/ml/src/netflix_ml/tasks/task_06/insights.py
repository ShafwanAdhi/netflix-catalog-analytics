"""Deterministic descriptive comparisons; supported differences are not causal effects."""

from netflix_ml.tasks.task_06.features import tokens

GROUPS = {"all": None, "movies": "Movie", "tv": "TV Show"}
LIMITATION = (
    "Snapshot association only; overlapping labels and catalog survivorship prevent causal or demand claims."
)


def build_insights(frame, minimum_support):
    breakdown, insights = [], {}
    for kind, subset in frame.groupby("type", sort=True):
        reference = float(subset.lag_years.median())
        for field, column in [("country", "country"), ("genre", "listed_in")]:
            expanded = (
                subset.assign(category=subset[column].map(tokens))
                .explode("category")
                .dropna(subset=["category"])
            )
            for name, group in expanded.groupby("category", sort=True):
                median = float(group.lag_years.median())
                breakdown.append(
                    {
                        "content_type": kind,
                        "field": field,
                        "name": name,
                        "support": len(group),
                        "reference_support": len(subset),
                        "reference": f"All {kind} titles",
                        "median_years": median,
                        "reference_median": reference,
                        "difference": median - reference,
                        "supported": len(group) >= minimum_support,
                        "direction": "higher"
                        if median > reference
                        else "lower"
                        if median < reference
                        else "equal",
                        "limitation": LIMITATION,
                    }
                )
    for scope, kind in GROUPS.items():
        candidates = [r for r in breakdown if r["supported"] and (kind is None or r["content_type"] == kind)]
        insights[scope] = sorted(
            candidates,
            key=lambda r: (
                -abs(r["difference"]),
                r["name"],
                r["field"],
                r["content_type"],
            ),
        )[:5]
    return breakdown, insights
