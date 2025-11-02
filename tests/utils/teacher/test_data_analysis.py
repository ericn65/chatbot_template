from enum import Enum

import pandas as pd
import pytest

from chatbot_template.utils.teacher.data_analysis import (
    _enum_to_dict,
    _get_basic_stats,
    _get_column_info,
    _get_numeric_summary,
    _get_value_counts,
    _inverse_map_enum_to_labels,
    _map_column_to_enum,
    analyse_data,
    decode_column,
    encode_column,
)


# ---------------------------------------------------------------------
# MOCK ENUM
# ---------------------------------------------------------------------
class CityEnum(Enum):
    BARCELONA = 1
    MADRID = 2
    VALENCIA = 3
    UNKNOWN = 0


# ---------------------------------------------------------------------
# FIXTURE DATA
# ---------------------------------------------------------------------
@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample example for the tests."""
    return pd.DataFrame(
        {
            "city": ["Barcelona", "Madrid", "Valencia", "Madrid", None],
            "age": [25, 30, 22, 30, 25],
            "gender": ["M", "F", "M", "F", "F"],
        }
    )


# ---------------------------------------------------------------------
# TESTS FOR ANALYSIS FUNCTIONS
# ---------------------------------------------------------------------
def test_get_column_info(sample_df):
    """Tests the column getter."""
    info = _get_column_info(sample_df)
    assert isinstance(info, dict)
    assert "city" in info
    assert info["age"] in ["int64", "int32"]


def test_get_basic_stats(sample_df):
    """Tests the basic stats getter."""
    stats = _get_basic_stats(sample_df)
    assert stats["n_rows"] == 5
    assert stats["n_columns"] == 3
    assert isinstance(stats["missing_values"], int)
    assert "memory_usage_MB" in stats


def test_get_value_counts(sample_df):
    """Tests the value counter."""
    counts = _get_value_counts(sample_df, max_unique=10)
    assert "gender" in counts
    assert isinstance(counts["gender"], dict)
    assert counts["gender"]["F"] == 3


def test_get_numeric_summary(sample_df):
    """Tests the numeric summary getter."""
    summary = _get_numeric_summary(sample_df)
    assert "age" in summary
    assert all(k in summary["age"] for k in ["mean", "std", "min", "max"])
    assert isinstance(summary["age"]["mean"], float)


def test_analyse_data_returns_all_keys(sample_df):
    """Tests the data returning all keys."""
    analysis = analyse_data(sample_df)
    expected_keys = {"basic_stats", "column_info", "numeric_summary", "value_counts"}
    assert expected_keys.issubset(analysis.keys())
    assert isinstance(analysis["basic_stats"], dict)
    assert isinstance(analysis["column_info"], dict)


# ---------------------------------------------------------------------
# TESTS FOR ENUM AND MAPPING FUNCTIONS
# ---------------------------------------------------------------------
def test_enum_to_dict():
    """Tests the enums to dict."""
    mapping = _enum_to_dict(CityEnum)
    assert mapping["barcelona"] == 1
    assert mapping["unknown"] == 0


def test_map_column_to_enum_overwrites(sample_df):
    """Tests the enum overwrites."""
    df_encoded = _map_column_to_enum(
        sample_df.copy(), "city", CityEnum, default_value=CityEnum.UNKNOWN.value
    )
    assert "city" in df_encoded.columns
    assert all(df_encoded["city"].isin([0, 1, 2, 3]))  # All valid enum values


def test_map_column_to_enum_creates_new_col(sample_df):
    """Tests the column to enum new column creator."""
    df_encoded = _map_column_to_enum(
        sample_df.copy(), "city", CityEnum, new_column="city_code", default_value=0
    )
    assert "city_code" in df_encoded.columns
    assert len(df_encoded["city_code"]) == len(sample_df)
    assert df_encoded["city_code"].isna().sum() == 0


def test_map_column_to_enum_invalid_col_raises(sample_df):
    """Tests an invalid raiser for columns."""
    with pytest.raises(ValueError):
        _map_column_to_enum(sample_df.copy(), "nonexistent", CityEnum)


def test_inverse_map_enum_to_labels(sample_df):
    """Tests an inverse map enum to labels."""
    data = pd.DataFrame({"city": [1, 2, 0]})
    df_decoded = _inverse_map_enum_to_labels(data, "city", CityEnum)
    assert "city" in df_decoded.columns
    assert all(isinstance(val, str) for val in df_decoded["city"])
    assert set(df_decoded["city"]) <= {"Barcelona", "Madrid", "Unknown"}


def test_encode_column_and_decode_column(sample_df):
    """Tests column encoders."""
    df_encoded = encode_column(
        sample_df.copy(), "city", CityEnum, default_value=CityEnum.UNKNOWN.value
    )
    assert df_encoded["city"].isin([0, 1, 2, 3]).all()

    df_decoded = decode_column(df_encoded, "city", CityEnum)
    assert all(isinstance(v, str) for v in df_decoded["city"])


def test_case_insensitive_mapping(sample_df):
    """Tests case mappings."""
    data = pd.DataFrame({"city": ["madrid", "MADRID", "Barcelona", "unknown"]})
    df_encoded = encode_column(
        data, "city", CityEnum, default_value=CityEnum.UNKNOWN.value
    )
    assert df_encoded["city"].tolist() == [2, 2, 1, 0]
