from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from API.config import (
    CATEGORICAL_FEATURES,
    COURSE_GROUPS,
    EDUCATION_LEVELS,
    JOB_LEVELS,
    MODEL_FEATURES,
    NUMERIC_FEATURES,
    NYSC_PATHWAYS,
    QUALIFICATION_REQUIREMENTS,
    SECTOR_GROUPS,
    TARGET,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "africa_graduate_first_income.csv"
MODEL_PATH = PROJECT_DIR / "models" / "best_model.joblib"
METADATA_PATH = PROJECT_DIR / "models" / "model_metadata.json"
LOSS_CURVE_PATH = PROJECT_DIR / "models" / "sgd_loss_curve.csv"
RANDOM_STATE = 42
MIN_INCOME = 10_000.0
MAX_INCOME = 275_000.0

CATEGORY_RULES = {
    "education_level": EDUCATION_LEVELS,
    "course_group": COURSE_GROUPS,
    "first_job_level": JOB_LEVELS,
    "first_job_sector": SECTOR_GROUPS,
    "qualification_requirement": QUALIFICATION_REQUIREMENTS,
    "first_job_via_nysc": NYSC_PATHWAYS,
}

NUMBER_RULES = {
    "graduation_year": (2013, 2017),
    "course_preparation_score": (1, 4),
    "employability_skill_count": (0, 6),
    "problem_solving_skill": (0, 1),
    "communication_skill": (0, 1),
    TARGET: (MIN_INCOME, MAX_INCOME),
}


def make_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=3)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ]
    )


def make_pipeline(regressor: Any) -> Pipeline:
    return Pipeline(
        [
            ("preprocessor", make_preprocessor()),
            (
                "regressor",
                TransformedTargetRegressor(
                    regressor=regressor,
                    transformer=StandardScaler(),
                ),
            ),
        ]
    )


def model_definitions() -> dict[str, Any]:
    return {
        "LinearRegression": LinearRegression(),
        "SGDRegressor": SGDRegressor(
            random_state=RANDOM_STATE,
            max_iter=8_000,
            tol=1e-6,
            penalty="l2",
            learning_rate="adaptive",
            eta0=0.001,
            alpha=0.001,
            average=True,
        ),
        "DecisionTreeRegressor": DecisionTreeRegressor(
            random_state=RANDOM_STATE,
            max_depth=8,
            min_samples_leaf=15,
        ),
        "RandomForestRegressor": RandomForestRegressor(
            random_state=RANDOM_STATE,
            n_estimators=180,
            max_depth=12,
            min_samples_leaf=6,
            max_features=0.8,
            n_jobs=-1,
        ),
    }


def calculate_metrics(y_true: pd.Series | np.ndarray, predictions: np.ndarray) -> dict[str, float]:
    predictions = np.clip(np.asarray(predictions), MIN_INCOME, MAX_INCOME)
    return {
        "rmse_ngn": float(np.sqrt(mean_squared_error(y_true, predictions))),
        "mae_ngn": float(mean_absolute_error(y_true, predictions)),
        "r2": float(r2_score(y_true, predictions)),
    }


def tune_sgd(x_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
    search = GridSearchCV(
        make_pipeline(
            SGDRegressor(random_state=RANDOM_STATE, max_iter=8_000, tol=1e-6, average=True)
        ),
        {
            "regressor__regressor__alpha": [0.0001, 0.001, 0.01],
            "regressor__regressor__eta0": [0.0001, 0.001, 0.01],
            "regressor__regressor__learning_rate": ["constant", "adaptive"],
        },
        scoring="neg_root_mean_squared_error",
        cv=5,
        n_jobs=-1,
    )
    search.fit(x_train, y_train)
    return search.best_estimator_


def build_sgd_loss_curve(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    epochs: int = 120,
) -> pd.DataFrame:
    preprocessor = make_preprocessor()
    train_matrix = preprocessor.fit_transform(x_train)
    test_matrix = preprocessor.transform(x_test)
    target_mean = float(y_train.mean())
    target_std = float(y_train.std())
    train_target = (y_train.to_numpy() - target_mean) / target_std
    rng = np.random.default_rng(RANDOM_STATE)
    regressor = SGDRegressor(
        random_state=RANDOM_STATE,
        penalty="l2",
        alpha=0.001,
        learning_rate="constant",
        eta0=0.001,
        average=True,
    )
    rows: list[dict[str, float | int]] = []
    for epoch in range(1, epochs + 1):
        order = rng.permutation(len(train_target))
        regressor.partial_fit(train_matrix[order], train_target[order])
        rows.append(
            {
                "epoch": epoch,
                "train_rmse_ngn": calculate_metrics(
                    y_train, regressor.predict(train_matrix) * target_std + target_mean
                )["rmse_ngn"],
                "test_rmse_ngn": calculate_metrics(
                    y_test, regressor.predict(test_matrix) * target_std + target_mean
                )["rmse_ngn"],
            }
        )
    return pd.DataFrame(rows)


def validate_training_data(data: pd.DataFrame) -> pd.DataFrame:
    required = set(MODEL_FEATURES + [TARGET])
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Training data is missing columns: {sorted(missing)}")
    clean = data[MODEL_FEATURES + [TARGET]].copy()
    for column in NUMERIC_FEATURES + [TARGET]:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    if clean.isna().any().any():
        raise ValueError("Training data contains missing or invalid values.")

    for column, (minimum, maximum) in NUMBER_RULES.items():
        if not clean[column].between(minimum, maximum).all():
            raise ValueError(f"{column} must be between {minimum} and {maximum}.")

    for column, allowed in CATEGORY_RULES.items():
        if not clean[column].isin(allowed).all():
            raise ValueError(f"{column} contains an unsupported value.")

    selected_skills = clean["problem_solving_skill"] + clean["communication_skill"]
    if (clean["employability_skill_count"] < selected_skills).any():
        raise ValueError("Skill count cannot be lower than the selected skills.")

    if len(clean) < 500:
        raise ValueError("At least 500 valid labelled rows are required for retraining.")
    return clean


def train_and_save(data: pd.DataFrame | None = None) -> dict[str, Any]:
    dataset = pd.read_csv(DATA_PATH) if data is None else data.copy()
    dataset = validate_training_data(dataset)
    x = dataset[MODEL_FEATURES]
    y = dataset[TARGET]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    trained: dict[str, Pipeline] = {}
    metrics: dict[str, dict[str, float]] = {}
    for name, estimator in model_definitions().items():
        pipeline = (
            tune_sgd(x_train, y_train)
            if name == "SGDRegressor"
            else make_pipeline(estimator)
        )
        pipeline.fit(x_train, y_train)
        trained[name] = pipeline
        metrics[name] = calculate_metrics(y_test, pipeline.predict(x_test))

    best_name = min(metrics, key=lambda name: metrics[name]["rmse_ngn"])
    loss_curve = build_sgd_loss_curve(x_train, x_test, y_train, y_test)
    LOSS_CURVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    loss_curve.to_csv(LOSS_CURVE_PATH, index=False)
    joblib.dump(trained[best_name], MODEL_PATH)

    timestamp = datetime.now(UTC)
    metadata: dict[str, Any] = {
        "model_name": best_name,
        "model_version": timestamp.strftime("%Y%m%dT%H%M%SZ"),
        "trained_at": timestamp.isoformat(),
        "selection_metric": "lowest held-out RMSE in 2018 Nigerian naira",
        "training_rows": len(x_train),
        "test_rows": len(x_test),
        "total_rows": len(dataset),
        "target": TARGET,
        "features": MODEL_FEATURES,
        "metrics": metrics,
        "baseline": {
            "training_median_ngn": float(y_train.median()),
            "test_median_baseline": calculate_metrics(
                y_test, np.repeat(y_train.median(), len(y_test))
            ),
        },
        "limitations": [
            "The online survey is self-selected and is not a census of Nigerian graduates.",
            "Income was reported in ranges and converted to documented band midpoints.",
            (
                "The 2018 naira benchmark is historical and must not be treated "
                "as a current salary quote."
            ),
            (
                "Nigeria provides African evidence, but results cannot represent "
                "every African country."
            ),
        ],
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    print(json.dumps(train_and_save(), indent=2))


if __name__ == "__main__":
    main()
