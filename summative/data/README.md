# Data

`africa_graduate_first_income.csv` is the modelling table. It contains 1,656
recent Nigerian graduates with a reported first-employment income, 12 input
features, and one continuous regression target.

The source is Stutern's real
[Nigerian Graduate Report 2018 survey](https://www.kaggle.com/datasets/stutern/nigerian-gradaute-report-2018):
5,219 respondents and 36 original variables. Download and prepare it with:

```bash
cd summative
uv run python scripts/download_data.py
uv run python scripts/prepare_data.py
```

The downloader requires Kaggle credentials. The ignored raw CSV is retained
locally; the prepared table is committed so all submitted work runs
reproducibly without those credentials.

The target is the midpoint of each first-monthly-income band in 2018 Nigerian
naira. This approximation preserves ordering but not exact income. The sample
is voluntary, self-reported, historical, and Nigeria-specific. It supports an
African graduate-program case study but cannot represent every country or
guarantee an individual's earnings.
