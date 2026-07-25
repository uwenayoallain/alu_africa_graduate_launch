# African Graduate Launch Benchmark

> Our mission is to help young Africans enter technology through practical training, internships, and mentorship.
> This project studies how education, job-ready skills, and first-job pathways relate to graduate income.
> It estimates a historical first-employment income benchmark for program planning, not a person's worth.
> The evidence can help youth programs prioritize experiences that make the transition into work more effective.

## Dataset

The project uses the real [Nigerian Graduate Report 2018 survey](https://www.kaggle.com/datasets/stutern/nigerian-gradaute-report-2018)
published by Stutern. The source contains **5,219 recent Nigerian graduates and
36 variables**. After keeping respondents with a reported first-employment
income and engineering the modelling fields, the included Africa-specific
dataset has **1,656 rows and 13 columns**; 277 rows describe technology or
telecommunications pathways.

The continuous target is the midpoint of the respondent's first monthly income
band, measured in **2018 Nigerian naira (NGN)**. Predictors cover graduation
year, education, course group, first-job level and sector, qualification
requirements, NYSC entry, employer-valued experience, course preparation, and
employability skills.

The notebook explains every transformation. Sensitive gender data, timestamps,
free-text answers, identifiers, current salary, and post-outcome variables are
dropped to reduce leakage and avoid turning a program-planning tool into a
demographic valuation tool. Categorical fields are one-hot encoded and every
numeric input is standardized inside leakage-safe scikit-learn pipelines.

This is Nigerian evidence, not a representative sample of every African
country. Income is self-reported and banded, and the survey is historical.
Predictions must therefore be interpreted as pathway benchmarks. A future
upgrade can retrain the same architecture with authenticated 2024 national
labour-force microdata.

## Visual analysis and model comparison

`summative/linear_regression/multivariate.ipynb` includes:

- target and predictor distributions with written interpretations;
- a numeric correlation heatmap;
- income comparisons by first-job sector and employer-valued factor;
- feature-engineering, encoding, standardization, and leakage decisions;
- Ordinary Linear Regression, tuned SGD Linear Regression, Decision Tree, and
  Random Forest implementations;
- SGD train and test loss curves;
- before/after scatter plots with a fitted linear projection; and
- one held-out-row prediction using the saved best model.

Lowest held-out RMSE is the primary selection rule because large income errors
are especially costly for planning. MAE and R² are reported as supporting
metrics.

| Model | Test RMSE (NGN) | Test MAE (NGN) | R² |
|---|---:|---:|---:|
| Ordinary Linear Regression | **43,830.24** | **30,329.20** | **0.132** |
| SGD Linear Regression | 43,900.98 | 30,378.74 | 0.129 |
| Random Forest | 44,474.95 | 30,638.19 | 0.106 |
| Decision Tree | 46,868.47 | 32,641.04 | 0.008 |
| Median baseline | 50,561.61 | 29,066.27 | -0.155 |

Ordinary Linear Regression is saved because it has the lowest test RMSE.
Its low R² shows that the survey features explain only a modest share of
individual income variation. The model improves RMSE over the baseline but not
MAE, so it is useful as a broad cohort benchmark rather than a precise promise.

## Public API

Swagger UI: **`https://REPLACE-WITH-YOUR-RENDER-SERVICE.onrender.com/docs`**

Prediction endpoint:

```text
POST https://REPLACE-WITH-YOUR-RENDER-SERVICE.onrender.com/predict
```

Example request:

```json
{
  "graduation_year": 2017,
  "education_level": "bachelors",
  "course_group": "technology",
  "first_job_level": "entry",
  "first_job_sector": "technology_telecommunications",
  "qualification_requirement": "degree_related",
  "first_job_via_nysc": 0,
  "employer_valued_factor": "internship_practical_experience",
  "course_preparation_score": 4,
  "employability_skill_count": 5,
  "problem_solving_skill": 1,
  "communication_skill": 1
}
```

Each field has an enforced Pydantic type, realistic range or enum, and a
description visible in Swagger. The response returns a predicted historical
monthly income in 2018 NGN, the matching survey band, model details, and an
interpretation warning.

## Repository layout

```text
summative/
├── linear_regression/multivariate.ipynb
├── API/
│   ├── prediction.py
│   ├── schemas.py
│   ├── training.py
│   └── config.py
├── FlutterApp/
├── data/africa_graduate_first_income.csv
├── models/
├── scripts/
├── tests/
├── pyproject.toml
├── uv.lock
└── requirements.txt
```

## Run the Python project

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
cd summative
uv sync
uv run uvicorn API.prediction:app --reload
```

Open <http://127.0.0.1:8000/docs>.

Reproduce the data and models:

```bash
uv run python scripts/download_data.py
uv run python scripts/prepare_data.py
uv run python scripts/retrain.py
uv run python scripts/build_notebook.py
```

The download command uses the Kaggle API and requires Kaggle credentials.
The prepared modelling CSV is committed so the notebook, API, and tests run
without downloading the raw survey.

Verify:

```bash
uv run ruff check API scripts tests
uv run pytest -q
```

## Model retraining

`POST /retrain` accepts a labelled CSV containing the 12 public input columns
plus `first_monthly_income_ngn`. It validates the schema, appends valid new
rows, retrains and compares all four algorithms, atomically replaces the
lowest-RMSE artifact, and reloads the model without restarting the service.

When `RETRAIN_API_KEY` is configured, callers must send it as
`X-Retrain-Key`. Uploads are limited to 5 MB, only CSV is accepted, and the
combined valid dataset must contain at least 1,000 rows. Manual fallback:

```bash
uv run python scripts/retrain.py
```

## CORS reasoning

CORS uses exact origins instead of `*`. It permits origins supplied through
`ALLOWED_ORIGINS`, the Render service origin, and local Flutter-web development
origins. Only `GET`, `POST`, and `OPTIONS` methods and `Content-Type` and
`X-Retrain-Key` headers are accepted. Credentials are disabled because the API
does not use browser cookies or session authentication. Native Flutter is not
restricted by browser CORS, but these rules protect Swagger and any web client.

## Run the Flutter mobile app

```bash
cd summative/FlutterApp
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

For a physical device or production build, replace the URL with the publicly
routable Render service. The one-page app contains exactly 12 model inputs, a
`Predict` button, validation, loading feedback, and a prediction/error display.

## Deploy to Render

1. Push the repository to GitHub.
2. Create a Render Blueprint from the repository.
3. Render reads `render.yaml`, uses `summative` as its root, and checks
   `/health`.
4. Set any additional exact browser origins in `ALLOWED_ORIGINS`.
5. Test a valid request plus datatype, range, and missing-field errors at
   `/docs`.
6. Replace the public URL placeholders in this README and the Flutter build.

## Video demonstration

YouTube: **`https://youtube.com/REPLACE-WITH-YOUR-VIDEO`**

Keep the recording at seven minutes or less. Keep the camera on and the entire
screen shared. Demonstrate the mobile prediction and Swagger tests within the
first two minutes, then explain the notebook, loss, model choice,
hyperparameters, retraining, and CORS decisions.
