"""Fold-fitted metadata features with an explicit allowlist and no calendar predictors."""

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted

FEATURES = ["type", "country", "listed_in", "duration", "director"]


def tokens(value):
    return sorted({v.strip() for v in str(value).split(",") if v.strip() and v.strip() != "Not Given"})


def input_frame(body):
    unit = "min" if body["duration"]["unit"] == "minutes" else "Seasons"
    return pd.DataFrame(
        [
            {
                "type": body["content_type"],
                "country": ", ".join(body["countries"]) or "Not Given",
                "listed_in": ", ".join(body["genres"]),
                "director": body.get("director") or "Not Given",
                "duration": f"{body['duration']['value']} {unit}",
            }
        ]
    )


class AnalyticsEncoder(TransformerMixin, BaseEstimator):
    def __init__(self, advanced=False):
        self.advanced = advanced

    def rows(self, X):
        categorical, numeric = [], []
        for row in X[FEATURES].itertuples(index=False):
            countries, genres, directors = tokens(row.country), tokens(row.listed_in), tokens(row.director)
            movie = row.type == "Movie"
            amount = float(row.duration.split()[0])
            fields = {"type=" + row.type: 1.0}
            fields.update({"country=" + v: 1.0 for v in countries})
            fields.update({"genre=" + v: 1.0 for v in genres})
            values = [amount if movie else 0.0, 0.0 if movie else amount]
            if self.advanced:
                fields.update({f"type_genre={row.type}|{v}": 1.0 for v in genres})
                values += [
                    np.log1p(amount) if movie else 0.0,
                    0.0 if movie else np.log1p(amount),
                    len(countries),
                    len(genres),
                    len(directors),
                    float(not countries),
                    float(not directors),
                ]
            categorical.append(fields)
            numeric.append(values)
        return categorical, np.asarray(numeric, dtype=float)

    def fit(self, X, y=None):
        categories, numbers = self.rows(X)
        self.vectorizer_ = DictVectorizer().fit(categories)
        self.scaler_ = StandardScaler().fit(numbers)
        return self

    def transform(self, X):
        check_is_fitted(self, ["vectorizer_", "scaler_"])
        categories, numbers = self.rows(X)
        return sparse.hstack(
            [
                self.vectorizer_.transform(categories),
                sparse.csr_matrix(self.scaler_.transform(numbers)),
            ],
            format="csr",
        )

    def get_feature_names_out(self, input_features=None):
        numbers = ["movie_minutes", "tv_seasons"]
        if self.advanced:
            numbers += [
                "log_movie_minutes",
                "log_tv_seasons",
                "country_count",
                "genre_count",
                "director_count",
                "country_missing",
                "director_missing",
            ]
        return np.append(self.vectorizer_.get_feature_names_out(), numbers)
