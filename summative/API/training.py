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
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from API.config import (
    CAREER_FIELDS,
    CATEGORICAL_FEATURES,
    CONTRACT_TYPES,
    EDUCATION_LEVELS,
    EMPLOYER_TYPES,
    MAIN_SECTORS,
    MODEL_FEATURES,
    NUMERIC_FEATURES,
    PROVINCES,
    RESIDENCE_TYPES,
    TARGET,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "rwanda_youth_employee_income.csv"
MODEL_PATH = PROJECT_DIR / "models" / "best_model.joblib"
METADATA_PATH = PROJECT_DIR / "models" / "model_metadata.json"
RANDOM_STATE = 42
MIN_INCOME = 6_000.0
MAX_INCOME = 370_000.0

CATEGORY_RULES = {
    "education_level": EDUCATION_LEVELS,
    "career_field": CAREER_FIELDS,
    "main_sector": MAIN_SECTORS,
    "employer_type": EMPLOYER_TYPES,
    "contract_type": CONTRACT_TYPES,
    "residence": RESIDENCE_TYPES,
    "province": PROVINCES,
}

NUMBER_RULES = {
    "age": (16, 30),
    "weekly_hours": (1, 118),
    TARGET: (MIN_INCOME, MAX_INCOME),
}


def make_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
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
        "Ordinary Linear Regression": LinearRegression(),
        "Stochastic Gradient Descent": SGDRegressor(
            random_state=RANDOM_STATE,
            max_iter=5_000,
            tol=1e-5,
            average=True,
        ),
        "Decision Tree": DecisionTreeRegressor(
            random_state=RANDOM_STATE,
            max_depth=8,
            min_samples_leaf=15,
        ),
        "Random Forest": RandomForestRegressor(
            random_state=RANDOM_STATE,
            n_estimators=150,
            max_depth=12,
            min_samples_leaf=6,
            n_jobs=-1,
        ),
    }


def calculate_metrics(
    y_true: pd.Series | np.ndarray,
    predictions: np.ndarray,
) -> dict[str, float]:
    predictions = np.clip(np.asarray(predictions), MIN_INCOME, MAX_INCOME)
    return {
        "rmse_rwf": float(np.sqrt(mean_squared_error(y_true, predictions))),
        "mae_rwf": float(mean_absolute_error(y_true, predictions)),
        "r2": float(r2_score(y_true, predictions)),
    }


def tune_sgd(x_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
    search = GridSearchCV(
        make_pipeline(
            SGDRegressor(
                random_state=RANDOM_STATE,
                max_iter=5_000,
                tol=1e-5,
                average=True,
            )
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
    random = np.random.default_rng(RANDOM_STATE)
    regressor = SGDRegressor(
        random_state=RANDOM_STATE,
        alpha=0.001,
        learning_rate="constant",
        eta0=0.001,
        average=True,
    )
    rows = []
    for epoch in range(1, epochs + 1):
        order = random.permutation(len(train_target))
        regressor.partial_fit(train_matrix[order], train_target[order])
        train_predictions = (
            regressor.predict(train_matrix) * target_std + target_mean
        )
        test_predictions = regressor.predict(test_matrix) * target_std + target_mean
        rows.append(
            {
                "epoch": epoch,
                "train_rmse_rwf": calculate_metrics(
                    y_train, train_predictions
                )["rmse_rwf"],
                "test_rmse_rwf": calculate_metrics(
                    y_test, test_predictions
                )["rmse_rwf"],
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

    if len(clean) < 500:
        raise ValueError("At least 500 valid rows are required for retraining.")
    return clean


def split_data(data: pd.DataFrame):
    x = data[MODEL_FEATURES]
    y = data[TARGET]
    income_groups = pd.qcut(y, q=10, duplicates="drop")
    return train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=income_groups,
    )


def train_and_save(data: pd.DataFrame | None = None) -> dict[str, Any]:
    dataset = pd.read_csv(DATA_PATH) if data is None else data.copy()
    dataset = validate_training_data(dataset)
    x_train, x_test, y_train, y_test = split_data(dataset)

    trained = {}
    metrics = {}
    for name, estimator in model_definitions().items():
        model = (
            tune_sgd(x_train, y_train)
            if name == "Stochastic Gradient Descent"
            else make_pipeline(estimator)
        )
        model.fit(x_train, y_train)
        trained[name] = model
        metrics[name] = calculate_metrics(y_test, model.predict(x_test))

    best_name = min(metrics, key=lambda name: metrics[name]["rmse_rwf"])
    joblib.dump(trained[best_name], MODEL_PATH)

    timestamp = datetime.now(UTC)
    metadata = {
        "model_name": best_name,
        "model_version": timestamp.strftime("%Y%m%dT%H%M%SZ"),
        "trained_at": timestamp.isoformat(),
        "selection_metric": "lowest test RMSE in Rwandan francs",
        "training_rows": len(x_train),
        "test_rows": len(x_test),
        "total_rows": len(dataset),
        "target": TARGET,
        "features": MODEL_FEATURES,
        "metrics": metrics,
        "baseline": {
            "training_median_rwf": float(y_train.median()),
            "test_median_baseline": calculate_metrics(
                y_test,
                np.repeat(y_train.median(), len(y_test)),
            ),
        },
        "limitations": [
            "The model is a Rwanda case study and cannot represent every African country.",
            "The survey records employment conditions, not a person's full skill portfolio.",
            "The smallest and largest one percent of reported incomes were removed.",
            "The estimate describes an association and is not a guaranteed salary.",
        ],
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    print(json.dumps(train_and_save(), indent=2))
