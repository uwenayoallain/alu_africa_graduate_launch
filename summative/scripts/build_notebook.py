"""Generate and execute the submitted regression notebook."""

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

PROJECT_DIR = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_DIR / "linear_regression" / "multivariate.ipynb"

nb = nbf.v4.new_notebook()
nb["metadata"]["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb["metadata"]["language_info"] = {"name": "python", "version": "3.12"}

nb["cells"] = [
    nbf.v4.new_markdown_cell(
        """# African Graduate Launch Benchmark

**Mission:** Help young Africans enter technology careers through teaching, bootcamps,
practical training, mentorship, internships, and employer partnerships.
**Problem:** Program teams need evidence about which learning and first-job pathways are
associated with stronger early-career outcomes.
**Model use:** Estimate a historical first monthly income benchmark for a graduate pathway.
**Decision:** Compare pathways and improve program design; never rank a person's worth.

This is a specific graduate-transition regression task, not a generic salary
or house-price model."""
    ),
    nbf.v4.new_markdown_cell(
        """## Dataset and target

The source is the **Stutern Nigerian Graduate Report 2018**, a real survey of 5,219
Nigerian graduates from the 2013–2017 cohorts. Stutern created it to improve African
graduate employment and employer matching. It covers education, skills,
employment status, first jobs, sectors, qualification relevance, and income.

- Source: https://www.kaggle.com/datasets/stutern/nigerian-gradaute-report-2018
- Survey rows: 5,219 with 36 original variables
- Labelled first-employment rows after preparation: 1,655
- Continuous target: midpoint of the reported first monthly income range in Nigerian naira

The source is Nigeria-specific. It provides valuable African evidence, but the results
must not be presented as representative of every African country."""
    ),
    nbf.v4.new_code_cell(
        """from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split

from API.config import MODEL_FEATURES, NUMERIC_FEATURES, TARGET
from API.training import (
    RANDOM_STATE, build_sgd_loss_curve, calculate_metrics, make_pipeline,
    model_definitions, tune_sgd,
)

sns.set_theme(style="whitegrid", palette="crest")
DATA_PATH = Path("data/africa_graduate_first_income.csv")
data = pd.read_csv(DATA_PATH)
print(f"Prepared shape: {data.shape[0]:,} rows × {data.shape[1]} columns")
tech_rows = (data["first_job_sector"] == "Technology and telecommunications").sum()
print(f"Technology and telecommunications pathways: {tech_rows:,}")
data.head()"""
    ),
    nbf.v4.new_markdown_cell(
        """## Feature engineering and interpretation

The source income is categorical ranges. Each range is converted to its midpoint:
`Under ₦20,000 → ₦10,000`, `₦20,000–₦49,999 → ₦35,000`, through to a documented
`₦275,000` assumption for the open-ended `₦250,000 and more` band.

The following decisions make the model useful and safer:

- duplicate source submissions, timestamp, institution name, employer name, transport,
  free-text role, and survey
  commentary are dropped because they are identifiers, high-cardinality text, or unrelated;
- gender is deliberately excluded from prediction because it is sensitive and not an
  intervention a youth program should optimize;
- 114 course names become nine teachable course families;
- 30 sectors become nine pathway groups, including technology and telecommunications;
- multi-select skills become a numeric count plus problem-solving and communication flags;
- course-preparation responses become an ordinal 1–4 score;
- the first-job qualification response becomes a stable category;
- current-job fields are dropped because they happen after the first-income outcome.

Numeric fields are median-imputed and standardized with `StandardScaler`. Categorical
fields are most-frequent-imputed and one-hot encoded. All transformations are fitted only
on training data inside each pipeline, preventing leakage."""
    ),
    nbf.v4.new_code_cell(
        """quality = pd.DataFrame({
    "dtype": data.dtypes.astype(str),
    "missing": data.isna().sum(),
    "unique": data.nunique(),
})
print(f"Duplicate prepared rows: {data.duplicated().sum():,}")
quality"""
    ),
    nbf.v4.new_markdown_cell(
        """## Visualization 1: target distribution

Most reported first incomes are in the lower bands, with a long upper tail. This imbalance
means a median baseline is strong on MAE, while RMSE heavily penalizes mistakes on the
smaller high-income groups. Stratifying the split by target band preserves this structure."""
    ),
    nbf.v4.new_code_cell(
        """plt.figure(figsize=(10, 5))
order = sorted(data[TARGET].unique())
sns.countplot(data=data, x=TARGET, order=order, color="#c86545")
plt.xticks(
    range(len(order)),
    [f"₦{value/1000:.0f}k" for value in order],
)
plt.xlabel("First monthly income band midpoint")
plt.ylabel("Graduates")
plt.title("Distribution of labelled first-employment income")
plt.tight_layout()
plt.show()"""
    ),
    nbf.v4.new_markdown_cell(
        """## Visualization 2: numeric relationships

The heatmap checks whether preparation and skill measures carry linear signal. Correlations
are modest, warning us not to overclaim that training alone determines income. Graduation
year, role, sector, credentials, networks, and unmeasured employer conditions also matter."""
    ),
    nbf.v4.new_code_cell(
        """corr = data[NUMERIC_FEATURES + [TARGET]].corr(method="spearman")
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0)
plt.title("Spearman correlation of numeric variables")
plt.tight_layout()
plt.show()"""
    ),
    nbf.v4.new_markdown_cell(
"""## Visualization 3: pathways that affect training decisions

Sector and course-preparation comparisons can guide curriculum and career preparation.
They describe groups in this survey and must not be treated as promises to individuals."""
    ),
    nbf.v4.new_code_cell(
        """fig, axes = plt.subplots(1, 2, figsize=(15, 6))
sector_order = data.groupby("first_job_sector")[TARGET].median().sort_values().index
sns.boxplot(
    data=data, y="first_job_sector", x=TARGET, order=sector_order,
    showfliers=False, ax=axes[0], color="#e6b557"
)
axes[0].set(title="Income by first-job sector", xlabel="Monthly income midpoint (₦)", ylabel="")
sns.boxplot(
    data=data, x="course_preparation_score", y=TARGET,
    showfliers=False, ax=axes[1], color="#7fa496"
)
axes[1].set(
    title="Income by course-preparation score",
    xlabel="Course preparation score",
    ylabel="Monthly income midpoint (₦)",
)
plt.tight_layout()
plt.show()"""
    ),
    nbf.v4.new_markdown_cell(
        """## Four regression implementations

The comparison uses the same stratified 80/20 split:

1. ordinary `LinearRegression`;
2. stochastic-gradient `SGDRegressor`, tuned with five-fold cross-validation;
3. `DecisionTreeRegressor`;
4. ensemble `RandomForestRegressor`.

RMSE in original 2018 naira is the selection loss because large pathway-estimation errors
matter. MAE and R² are reported so a low-looking single metric cannot hide weak fit."""
    ),
    nbf.v4.new_code_cell(
        """X = data[MODEL_FEATURES]
y = data[TARGET]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

trained_models = {}
metric_rows = []
for name, estimator in model_definitions().items():
    model = tune_sgd(X_train, y_train) if name == "SGDRegressor" else make_pipeline(estimator)
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    trained_models[name] = model
    metric_rows.append({"model": name, **calculate_metrics(y_test, prediction)})

metrics = pd.DataFrame(metric_rows).set_index("model").sort_values("rmse_ngn")
baseline = calculate_metrics(y_test, np.repeat(y_train.median(), len(y_test)))
display(metrics)
display(pd.DataFrame([baseline], index=["Median baseline"]))"""
    ),
    nbf.v4.new_markdown_cell(
        """## SGD train and test loss

The target is standardized during optimization so stochastic gradient descent is stable.
The curve is transformed back to naira RMSE for interpretation. The learning-rate schedule,
initial step size, L2 regularization strength, and epochs are tunable hyperparameters."""
    ),
    nbf.v4.new_code_cell(
        """loss_curve = build_sgd_loss_curve(X_train, X_test, y_train, y_test)
loss_curve.plot(
    x="epoch", y=["train_rmse_ngn", "test_rmse_ngn"],
    figsize=(10, 5), color=["#173d34", "#c86545"]
)
plt.ylabel("RMSE (2018 NGN)")
plt.title("SGD train and test loss")
plt.tight_layout()
plt.show()
loss_curve.tail()"""
    ),
    nbf.v4.new_markdown_cell(
        """## Before and after: fitted linear projection

This is multivariate regression, so a single chart cannot show all dimensions. The right
panel varies employability-skill count from 0–6 while holding other features at representative
values. It shows where the ordinary linear model passes through that one-feature projection."""
    ),
    nbf.v4.new_code_cell(
        """linear = trained_models["LinearRegression"]
sample = data.sample(min(900, len(data)), random_state=RANDOM_STATE).copy()
sample["skill_jitter"] = (
    sample["employability_skill_count"]
    + np.random.default_rng(42).normal(0, .08, len(sample))
)
representative = {}
for column in MODEL_FEATURES:
    representative[column] = (
        data[column].median() if column in NUMERIC_FEATURES else data[column].mode().iat[0]
    )
skill_grid = np.linspace(0, 6, 100)
projection = pd.DataFrame([representative] * len(skill_grid))
projection["employability_skill_count"] = skill_grid
fitted = linear.predict(projection)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].scatter(sample["skill_jitter"], sample[TARGET], s=12, alpha=.22, color="#607d75")
axes[0].set(
    title="Before training: observed pathways",
    xlabel="Employability skill count",
    ylabel="First monthly income (₦)",
)
axes[1].scatter(sample["skill_jitter"], sample[TARGET], s=12, alpha=.12, color="#607d75")
axes[1].plot(skill_grid, fitted, color="#c86545", linewidth=3, label="Linear fit projection")
axes[1].legend()
axes[1].set(
    title="After training: fitted linear projection",
    xlabel="Employability skill count",
    ylabel="First monthly income (₦)",
)
plt.tight_layout()
plt.show()"""
    ),
    nbf.v4.new_markdown_cell(
        """## Save the winner and predict one held-out row

The full winning pipeline is saved, not only the estimator. This preserves imputation,
numeric standardization, category conversion, and the model as one deployable artifact."""
    ),
    nbf.v4.new_code_cell(
        """best_name = metrics.index[0]
joblib.dump(trained_models[best_name], "models/best_model.joblib")
loss_curve.to_csv("models/sgd_loss_curve.csv", index=False)
print("Saved:", best_name)
print("Selection rule: lowest held-out RMSE in 2018 Nigerian naira")

saved_model = joblib.load("models/best_model.joblib")
one_row = X_test.iloc[[0]]
actual = float(y_test.loc[one_row.index[0]])
predicted = float(saved_model.predict(one_row)[0])
display(one_row)
print(f"Actual band midpoint: ₦{actual:,.0f}")
print(f"Predicted benchmark: ₦{predicted:,.0f}")"""
    ),
    nbf.v4.new_markdown_cell(
        """## Interpretation, limitations, and new data

The winning model beats the median RMSE baseline, but R² remains low. That is an important
finding: education and observable skill pathways explain only a limited share of first-income
variation. Loss could be reduced with exact income, portfolio quality, internship duration,
technical assessment scores, location, employer size, and newer multi-country African data.

The result should guide questions for teaching, bootcamps, training, internships, and employer
partnerships. It must not decide who deserves an opportunity. The source is self-selected,
income is midpoint-coded, values are historical 2018 naira, and Nigeria cannot represent the
whole continent.

`POST /retrain` accepts new labelled rows, validates the same schema, compares all four
algorithms again, saves the lowest-RMSE pipeline, and reloads it for prediction."""
    ),
]

NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
executed = NotebookClient(nb, timeout=900, kernel_name="python3").execute(
    cwd=str(PROJECT_DIR)
)
nbf.write(executed, NOTEBOOK_PATH)
print(f"Wrote executed notebook to {NOTEBOOK_PATH}")
