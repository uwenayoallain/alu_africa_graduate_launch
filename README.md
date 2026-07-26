# African Youth Career Income Model

> Our mission is to help young Africans enter technology and other skilled careers.
> We support practical learning, bootcamps, mentorship, internships, and career guidance.
> This project studies how education and work pathways relate to employee income.
> The result helps programs compare pathways; it does not judge a person's potential.

## Dataset

The project uses the official
[Rwanda Labour Force Survey 2024](https://microdata.statistics.gov.rw/index.php/catalog/114)
from the National Institute of Statistics of Rwanda. The prepared project data
is in
[`summative/data/rwanda_youth_employee_income.csv`](summative/data/rwanda_youth_employee_income.csv).

The target is monthly employee cash income in Rwandan francs. The model uses
age, education level, career field, economic sector, employer type, contract
type, weekly hours, residence, and province.

The downloaded Stata file was exported to CSV. The data was limited to
employees aged 16–30 with a reported cash amount. Repeated respondents were
reduced to one observation, and the smallest and largest income tails were
removed so extreme reports did not dominate the loss.

Detailed occupation values were grouped into understandable career fields,
including ICT. Numeric fields are standardized and text categories are
converted to numeric columns inside the saved model pipeline. Identifiers,
gender, district, and unrelated survey questions are not model inputs.

## Limitations

- This is a Rwanda case study, not a model for every African country.
- It describes employed youth and cannot predict whether someone will get a job.
- It does not directly measure bootcamps, internships, certifications, or
  detailed digital skills.
- ICT observations are fewer than broad fields such as agriculture and
  elementary work, so ICT estimates require caution.
- Earnings are self-reported, and removing extreme values narrows the model's
  valid income range.
- The relationships are not proof that a feature causes higher income, and a
  prediction is not a guaranteed salary.

## Notebook and model results

The executed notebook is
[`summative/linear_regression/multivariate.ipynb`](summative/linear_regression/multivariate.ipynb).
It contains the data checks, feature decisions, income distribution,
correlation heatmap, career comparison, standardization, four models, loss
curve, fitted line, and one test-row prediction.

| Model | RMSE | MAE | R² |
|---|---:|---:|---:|
| Random Forest | **about 30,900 RWF** | **about 16,900 RWF** | **0.556** |
| Stochastic Gradient Descent | about 31,000 RWF | about 18,000 RWF | 0.553 |
| Ordinary Linear Regression | about 31,000 RWF | about 17,900 RWF | 0.551 |
| Decision Tree | about 31,800 RWF | about 17,700 RWF | 0.529 |
| Median baseline | about 49,500 RWF | about 26,100 RWF | -0.140 |

RMSE is a prediction error that gives large mistakes extra weight. MAE is the
average size of the mistakes. Lower RMSE and MAE are better. R² shows how much
of the income variation the model explains; higher is better.

Random Forest is saved because it has the lowest test RMSE. The result is
better than the simple median baseline, but the remaining error is still large
enough that the output should be treated as a broad planning estimate.

## API

The FastAPI service includes:

- `GET /health` to check that the model is loaded.
- `POST /predict` to validate inputs and return an income estimate.
- `POST /retrain` to upload labelled CSV data and replace the model after a new
  four-model comparison.
- `GET /docs` to open Swagger UI.

Example prediction body:

```json
{
  "age": 23,
  "education_level": "Primary education",
  "career_field": "Agriculture",
  "main_sector": "Agriculture",
  "employer_type": "Private business or VUP",
  "contract_type": "Oral agreement",
  "weekly_hours": 36,
  "residence": "Rural",
  "province": "Eastern Province"
}
```

Pydantic enforces the datatype, range, or accepted category for every input.
It also rejects education, career, sector, employer, and contract combinations
that have too little coverage in the survey.
The deployed retraining endpoint is protected by the `X-Retrain-Key` header.

## CORS

CORS uses named origins instead of `*`. It allows the Render service, origins
listed in `ALLOWED_ORIGINS`, and only `localhost` or `127.0.0.1` for browser
development. Only `GET`, `POST`, and `OPTIONS` are permitted. Credentials are
disabled because this API does not use browser cookies or sessions.

## Run the API

Install [uv](https://docs.astral.sh/uv/), then run:

```bash
cd summative
uv sync
uv run uvicorn API.prediction:app --reload
```

Open <http://127.0.0.1:8000/docs>.

## Deploy on Render

Deployment is required because the assignment asks for a publicly routable
Swagger URL and the Flutter app must call the hosted API. The included
[`render.yaml`](render.yaml) contains the build, start, health check, CORS, and
retraining-key settings.

- Create a Render Blueprint from this GitHub repository.
- Wait for the `/health` check to pass.
- Open <https://alu-africa-youth-income.onrender.com/docs>.
- Test a valid prediction and invalid datatype, range, and missing-field cases.
- Use the same Render service URL when running Flutter.

Public Swagger URL:
**<https://alu-africa-youth-income.onrender.com/docs>**

## Run the Flutter app

```bash
cd summative/FlutterApp
flutter pub get
flutter run
```

For a browser-based mobile preview:

```bash
flutter run -d web-server --web-hostname 0.0.0.0 --web-port 3000
```

For local Android emulator testing, use
`--dart-define=API_BASE_URL=http://10.0.2.2:8000`. The app has one page, one
input control for every model feature, a `Predict` button, and a result or error
area. Related dropdowns update together, while both rural and urban remain
available for every province.

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
├── data/rwanda_youth_employee_income.csv
├── models/
│   ├── best_model.joblib
│   └── model_metadata.json
├── pyproject.toml
├── uv.lock
└── requirements.txt
```

## Video

YouTube: **`https://youtube.com/REPLACE-WITH-YOUR-VIDEO`**

The video must remain within seven minutes. Show the mobile prediction and
Swagger tests within the first two minutes, then explain the notebook, model
loss, hyperparameters, retraining, and CORS choices.
