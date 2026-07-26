# African Graduate Launch Benchmark

> Our mission is to help young Africans enter technology through practical learning and career support.
> Many graduates struggle to connect education and employability skills with their first job.
> This project studies how education, skills, and first-job pathways relate to early income.
> The result is a planning benchmark for youth programs, not a judgement about a person.

## Dataset

The project uses the real
[Nigerian Graduate Report 2018](https://www.kaggle.com/datasets/stutern/nigerian-gradaute-report-2018)
published by Stutern. It contains thousands of graduate responses covering
education, employment, skills, job level, sector, and income. The prepared data
used by this project is available in
[`summative/data/nigerian_graduate_first_income.csv`](summative/data/nigerian_graduate_first_income.csv).

The regression target is the graduate's first monthly income in 2018 Nigerian
naira. Because the survey reports income ranges, each range is converted to its
midpoint. The model uses graduation year, education level, course group,
first-job level and sector, qualification requirement, NYSC pathway, course
preparation, and employability skills.

The notebook explains the feature engineering. Identifiers, free text, gender,
current salary, current-job answers, and other information collected after the
first-job outcome are excluded. Categorical values are one-hot encoded and
numeric values are standardized inside the model pipeline.

## Important limitations

- The survey is Nigeria-specific and cannot represent every African country.
- The data is historical and should not be read as a current salary guide.
- Income midpoints approximate ranges; they are not exact salaries.
- The online survey is self-reported and may not represent every graduate.
- The low R² shows that many important income factors are not available.
- The prediction is useful for comparing broad pathways, not deciding who
  deserves an opportunity or guaranteeing individual income.

## Notebook and models

The executed notebook is
[`summative/linear_regression/multivariate.ipynb`](summative/linear_regression/multivariate.ipynb).
It includes data checks, feature interpretation, a target distribution,
correlation heatmap, pathway comparisons, standardization, loss curves, a
fitted-line projection, and a prediction for one held-out row.

Four scikit-learn models are compared with the same train/test split:

| Model | RMSE | MAE | R² |
|---|---:|---:|---:|
| SGD Linear Regression | **≈ ₦43,320** | **≈ ₦29,812** | **0.137** |
| Ordinary Linear Regression | ≈ ₦43,792 | ≈ ₦29,979 | 0.118 |
| Random Forest | ≈ ₦43,799 | ≈ ₦30,071 | 0.118 |
| Decision Tree | ≈ ₦46,110 | ≈ ₦32,351 | 0.023 |
| Median baseline | ≈ ₦50,050 | ≈ ₦28,731 | -0.152 |

RMSE and MAE are prediction errors, so lower values are better. R² shows how
much variation the model explains, so higher values are better. Tuned SGD
Linear Regression is saved because it has the lowest test RMSE.

## API

The FastAPI service provides:

- `GET /health` — confirms that the saved model is loaded.
- `POST /predict` — validates inputs and returns a prediction.
- `POST /retrain` — accepts a labelled CSV and trains the models again.
- `GET /docs` — opens the Swagger UI.

Example prediction:

```json
{
  "graduation_year": 2017,
  "education_level": "Bachelor's degree",
  "course_group": "Technology and computing",
  "first_job_level": "Entry level",
  "first_job_sector": "Technology and telecommunications",
  "qualification_requirement": "Gave an advantage",
  "first_job_via_nysc": "No",
  "course_preparation_score": 3,
  "employability_skill_count": 5,
  "problem_solving_skill": true,
  "communication_skill": true
}
```

Pydantic enforces the datatype and accepted range or category for every field.
The retraining endpoint validates the uploaded columns and compares all four
models again before replacing the saved model. On Render, include the generated
retraining key in the `X-Retrain-Key` header.

## CORS

CORS uses explicit origins instead of `*`. It permits the Render service,
configured origins, and local development origins. Only `GET`, `POST`, and
`OPTIONS` are allowed. Credentials are disabled because the API does not use
browser cookies or sessions.

## Run the API

Requirements: Python and [uv](https://docs.astral.sh/uv/).

```bash
cd summative
uv sync
uv run uvicorn API.prediction:app --reload
```

Open <http://127.0.0.1:8000/docs>.

## Deploy on Render

The included [`render.yaml`](render.yaml) deploys the API from the `summative`
directory.

1. Create a Render Blueprint from this GitHub repository.
2. Wait for the `/health` check to pass.
3. Open `https://YOUR-SERVICE.onrender.com/docs`.
4. Test a valid request and invalid datatype, range, and missing-field requests.
5. Replace the placeholder below and use the same service URL in Flutter.

Public Swagger URL:
**`https://REPLACE-WITH-YOUR-RENDER-SERVICE.onrender.com/docs`**

## Run the Flutter app

```bash
cd summative/FlutterApp
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

For the submitted mobile build, replace the local address with the Render
service URL. The single page has one input control for every model feature, a
`Predict` button, validation, and a prediction or error display.

## Project structure

```text
summative/
├── linear_regression/multivariate.ipynb
├── API/
│   ├── prediction.py
│   ├── schemas.py
│   ├── training.py
│   └── config.py
├── FlutterApp/
├── data/nigerian_graduate_first_income.csv
├── models/
│   ├── best_model.joblib
│   └── model_metadata.json
├── pyproject.toml
├── uv.lock
└── requirements.txt
```

## Video

YouTube: **`https://youtube.com/REPLACE-WITH-YOUR-VIDEO`**

The video must stay within seven minutes, show the mobile app and public
Swagger tests within the first two minutes, and explain the notebook, model
loss, hyperparameters, retraining, and CORS decisions.
