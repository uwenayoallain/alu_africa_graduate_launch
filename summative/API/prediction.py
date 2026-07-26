from __future__ import annotations

import io
import json
import os
import threading
from contextlib import asynccontextmanager
from typing import Annotated, Any

import joblib
import pandas as pd
from fastapi import FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from API.config import MODEL_FEATURES, TARGET
from API.schemas import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    RetrainResponse,
)
from API.training import DATA_PATH, METADATA_PATH, MODEL_PATH, train_and_save

model_state: dict[str, Any] = {"model": None, "metadata": {}}
retrain_lock = threading.Lock()


def load_model() -> None:
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        model_state.update({"model": None, "metadata": {}})
        return
    model_state["model"] = joblib.load(MODEL_PATH)
    model_state["metadata"] = json.loads(METADATA_PATH.read_text(encoding="utf-8"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_model()
    yield
    model_state.clear()


app = FastAPI(
    title="African Graduate Launch API",
    version="1.0.0",
    description=(
        "Estimates a historical first-job monthly income benchmark from education, "
        "skills, internship signals, and a chosen early-career pathway."
    ),
    lifespan=lifespan,
)

default_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}
render_origin = os.getenv("RENDER_EXTERNAL_URL")
if render_origin:
    default_origins.add(render_origin.rstrip("/"))
configured_origins = {
    origin.strip().rstrip("/")
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(default_origins | configured_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Retrain-Key"],
)


def income_band(prediction: float) -> str:
    if prediction < 20_000:
        return "Under ₦20,000"
    if prediction < 50_000:
        return "₦20,000–₦49,999"
    if prediction < 100_000:
        return "₦50,000–₦99,999"
    if prediction < 150_000:
        return "₦100,000–₦149,999"
    if prediction < 200_000:
        return "₦150,000–₦199,999"
    if prediction < 250_000:
        return "₦200,000–₦249,999"
    return "₦250,000 and above"


@app.get("/health", response_model=HealthResponse, tags=["Service"])
def health() -> HealthResponse:
    metadata = model_state.get("metadata", {})
    return HealthResponse(
        status="ok" if model_state.get("model") is not None else "model unavailable",
        model_loaded=model_state.get("model") is not None,
        model_name=metadata.get("model_name"),
        model_version=metadata.get("model_version"),
    )


def request_frame(payload: PredictionRequest) -> pd.DataFrame:
    row = payload.model_dump(mode="json")
    return pd.DataFrame([row], columns=MODEL_FEATURES)


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(payload: PredictionRequest) -> PredictionResponse:
    model = model_state.get("model")
    metadata = model_state.get("metadata", {})
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available. Train it before requesting predictions.",
        )
    prediction = float(model.predict(request_frame(payload))[0])
    prediction = min(275_000.0, max(10_000.0, prediction))
    return PredictionResponse(
        predicted_first_monthly_income_ngn_2018=round(prediction, 2),
        income_band=income_band(prediction),
        model_name=metadata["model_name"],
        model_version=metadata["model_version"],
    )


def authorize_retraining(provided_key: str | None) -> None:
    expected_key = os.getenv("RETRAIN_API_KEY")
    if expected_key and provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-Retrain-Key header is required.",
        )


@app.post("/retrain", response_model=RetrainResponse, tags=["Model lifecycle"])
def retrain(
    file: Annotated[UploadFile, File(description="Labelled CSV with model inputs and target")],
    x_retrain_key: Annotated[str | None, Header()] = None,
) -> RetrainResponse:
    authorize_retraining(x_retrain_key)
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload must be a CSV file.")
    if not retrain_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="A retraining job is already running.")
    try:
        contents = file.file.read(5_000_001)
        if len(contents) > 5_000_000:
            raise HTTPException(status_code=413, detail="CSV must be 5 MB or smaller.")
        try:
            new_rows = pd.read_csv(io.BytesIO(contents))
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Could not parse CSV: {exc}") from exc

        required = set(MODEL_FEATURES + [TARGET])
        missing = required - set(new_rows.columns)
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"CSV is missing columns: {sorted(missing)}",
            )
        existing = pd.read_csv(DATA_PATH)
        combined = pd.concat(
            [existing, new_rows[MODEL_FEATURES + [TARGET]]],
            ignore_index=True,
        )
        metadata = train_and_save(combined)
        load_model()
        return RetrainResponse(
            message=f"Model retrained with {len(new_rows)} uploaded rows.",
            model_name=metadata["model_name"],
            model_version=metadata["model_version"],
            total_rows=metadata["total_rows"],
            metrics=metadata["metrics"],
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        retrain_lock.release()
