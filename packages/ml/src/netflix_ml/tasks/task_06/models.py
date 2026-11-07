"""Serializable baselines and nonnegative log-target metadata regressors."""

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.pipeline import Pipeline

from netflix_ml.tasks.task_06.features import AnalyticsEncoder


class MedianBaseline(RegressorMixin, BaseEstimator):
    def __init__(self, by_type=False):
        self.by_type = by_type

    def fit(self, X, y):
        y = np.asarray(y)
        self.median_ = float(np.median(y))
        self.groups_ = {kind: float(np.median(y[X.type.to_numpy() == kind])) for kind in X.type.unique()}
        return self

    def predict(self, X):
        return np.array(
            [self.groups_.get(kind, self.median_) if self.by_type else self.median_ for kind in X.type]
        )


class NonnegativeLogRegressor(RegressorMixin, BaseEstimator):
    def __init__(self, algorithm="ridge", advanced=False, alpha=1.0, depth=None, leaf=2, trees=200, seed=42):
        self.algorithm, self.advanced, self.alpha = algorithm, advanced, alpha
        self.depth, self.leaf, self.trees, self.seed = depth, leaf, trees, seed

    def fit(self, X, y):
        model = (
            Ridge(alpha=self.alpha, solver="lsqr")
            if self.algorithm == "ridge"
            else RandomForestRegressor(
                n_estimators=self.trees,
                max_depth=self.depth,
                min_samples_leaf=self.leaf,
                random_state=self.seed,
                n_jobs=1,
            )
        )
        self.pipeline_ = Pipeline(
            [
                ("features", AnalyticsEncoder(self.advanced)),
                ("model", TransformedTargetRegressor(regressor=model, func=np.log1p, inverse_func=np.expm1)),
            ]
        ).fit(X, y)
        return self

    def predict(self, X):
        return np.maximum(0.0, self.pipeline_.predict(X))


def metrics(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "median_absolute_error": float(median_absolute_error(actual, predicted)),
        "r2": float(r2_score(actual, predicted)) if len(actual) > 1 and np.var(actual) else None,
    }
