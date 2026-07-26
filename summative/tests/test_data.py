import pandas as pd

from API.config import MODEL_FEATURES, TARGET
from API.training import DATA_PATH, validate_training_data


def test_prepared_data_is_ready_for_training() -> None:
    data = pd.read_csv(DATA_PATH)

    assert list(data.columns) == MODEL_FEATURES + [TARGET]
    assert len(data) == 1_655
    assert data.isna().sum().sum() == 0
    assert len(validate_training_data(data)) == 1_655
