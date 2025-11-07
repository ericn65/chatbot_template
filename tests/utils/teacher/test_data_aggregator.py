import pandas as pd
import pytest

from chatbot_template.utils.teacher.data_aggregator import DataAggregator


# ---------------------------------------------------------------------
# FIXTURE BASE
# ---------------------------------------------------------------------
@pytest.fixture
def sample_df():
    """Sample example mocked for the tests."""
    return pd.DataFrame(
        {
            "city": ["Madrid", "Sevilla", "Madrid", "Sevilla", "Valencia"],
            "sales": [100, 120, 150, 130, 200],
            "profit": [10, 15, 20, 12, 30],
        }
    )


@pytest.fixture
def aggregator(sample_df):
    """Aggregator of data."""
    return DataAggregator(sample_df)


# ---------------------------------------------------------------------
# INIT AND BASIC VALIDATIONS
# ---------------------------------------------------------------------
def test_init_accepts_dataframe(sample_df):
    """Tests init accepts dataframe."""
    agg = DataAggregator(sample_df)
    assert isinstance(agg.data, pd.DataFrame)
    assert agg.data is not sample_df


def test_init_rejects_non_dataframe():
    """Tests inits rejections non dataframes."""
    with pytest.raises(TypeError):
        DataAggregator([1, 2, 3])


# ---------------------------------------------------------------------
# NUMERIC SUMMARY
# ---------------------------------------------------------------------
def test_get_numeric_summary(aggregator):
    """Tests getter numeric summaries."""
    summary = aggregator.get_numeric_summary()
    assert isinstance(summary, pd.DataFrame)
    assert all(
        col in summary.columns for col in ["mean", "median", "std", "min", "max"]
    )
    assert "sales" in summary.index
    assert "profit" in summary.index


def test_get_numeric_summary_raises_if_no_numeric():
    """Tests numeric sumaries getters issues."""
    data = pd.DataFrame({"city": ["Madrid", "Sevilla"]})
    with pytest.raises(ValueError):
        DataAggregator(data).get_numeric_summary()


# ---------------------------------------------------------------------
# GROUPING
# ---------------------------------------------------------------------
def test_group_by_and_aggregate_default(aggregator):
    """Tests groups by and aggregations defaults."""
    grouped = aggregator.group_by_and_aggregate("city")
    assert "city" in grouped.columns
    assert any("sales_mean" in col for col in grouped.columns)
    assert len(grouped) == 3  # 3 cities


def test_group_by_and_aggregate_custom_map(aggregator):
    """Tests groups and aggregations custom."""
    agg_map = {"sales": ["sum", "mean"]}
    grouped = aggregator.group_by_and_aggregate("city", agg_map)
    assert "sales_sum" in grouped.columns
    assert "sales_mean" in grouped.columns


def test_group_by_and_aggregate_invalid_column(aggregator):
    """Tests groups and aggregations."""
    with pytest.raises(ValueError):
        aggregator.group_by_and_aggregate("not_a_col")


# ---------------------------------------------------------------------
# FILTERING
# ---------------------------------------------------------------------
@pytest.mark.parametrize(
    "condition,value,expected_len",
    [
        (">", 120, 3),
        ("<", 130, 2),
        ("==", 100, 1),
        (">=", 150, 2),
        ("<=", 120, 2),
    ],
)
def test_filter_by_condition_valid(aggregator, condition, value, expected_len):
    """Tests filter by conditions valids."""
    result = aggregator.filter_by_condition("sales", condition, value)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == expected_len


def test_filter_by_condition_invalid_column(aggregator):
    """Tests filter by coditions with invalid columns."""
    with pytest.raises(ValueError):
        aggregator.filter_by_condition("unknown", ">", 10)


def test_filter_by_condition_invalid_operator(aggregator):
    """Tests filtering by conditions."""
    with pytest.raises(ValueError):
        aggregator.filter_by_condition("sales", "!=", 100)


# ---------------------------------------------------------------------
# SPLITTING
# ---------------------------------------------------------------------
def test_split_by_column_returns_dict(aggregator):
    """Tests for splitting by column returns."""
    splits = aggregator.split_by_column("city")
    assert isinstance(splits, dict)
    assert set(splits.keys()) == {"Madrid", "Sevilla", "Valencia"}
    for df in splits.values():
        assert isinstance(df, pd.DataFrame)


def test_split_by_column_invalid(aggregator):
    """Tests split by columns invalids."""
    with pytest.raises(ValueError):
        aggregator.split_by_column("not_exists")


# ---------------------------------------------------------------------
# OUTLIER DETECTION
# ---------------------------------------------------------------------
def test_detect_outliers_finds_extreme_values(sample_df):
    """Testing outliers crazy values."""
    sample_df.loc[len(sample_df)] = ["Madrid", 9999, 1000]
    agg = DataAggregator(sample_df)
    outliers = agg.detect_outliers("sales", z_threshold=2.0)
    assert not outliers.empty
    assert 9999 in outliers["sales"].to_numpy()


def test_detect_outliers_non_numeric(aggregator):
    """Tests detects outilers non numeric."""
    with pytest.raises(TypeError):
        aggregator.detect_outliers("city")


def test_detect_outliers_invalid_column(aggregator):
    """Tests detects outilers invalid columns."""
    with pytest.raises(ValueError):
        aggregator.detect_outliers("unknown_col")
