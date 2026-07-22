from fastapi.testclient import TestClient

from API.prediction import app

VALID_PAYLOAD = {
    "graduation_year": 2017,
    "education_level": "Bachelor's degree",
    "course_group": "Technology and computing",
    "first_job_level": "Entry level",
    "first_job_sector": "Technology and telecommunications",
    "qualification_requirement": "Gave an advantage",
    "first_job_via_nysc": "No",
    "employer_valued_factor": "Internship or practical experience",
    "course_preparation_score": 3,
    "employability_skill_count": 5,
    "problem_solving_skill": True,
    "communication_skill": True,
}


def test_health_and_prediction() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["model_loaded"] is True

        response = client.post("/predict", json=VALID_PAYLOAD)
        assert response.status_code == 200
        body = response.json()
        assert body["predicted_first_monthly_income_ngn_2018"] >= 10_000
        assert body["income_band"]
        assert body["model_name"]


def test_numeric_range_validation() -> None:
    payload = {**VALID_PAYLOAD, "course_preparation_score": 5}
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_datatype_validation() -> None:
    payload = {**VALID_PAYLOAD, "graduation_year": "recently"}
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_missing_field_validation() -> None:
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "course_group"}
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_skill_count_consistency() -> None:
    payload = {
        **VALID_PAYLOAD,
        "employability_skill_count": 1,
        "problem_solving_skill": True,
        "communication_skill": True,
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_retraining_file_validation() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/retrain",
            files={"file": ("notes.txt", b"not,csv", "text/plain")},
        )
    assert response.status_code == 400


def test_cors_preflight_is_limited_to_known_origin() -> None:
    with TestClient(app) as client:
        allowed = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        blocked = client.options(
            "/predict",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert blocked.status_code == 400
