import pandas as pd
import pytest

from chatbot_template.utils.teacher.data_loaders import (
    _load_data_csv,
    _load_data_excel,
    _load_from_json,
    _load_from_sql,
    load_data,
    safe_concat_dataframes,
    save_dataframe_to_csv,
    tag_df_with_metadata,
)
from chatbot_template.utils.teacher.enums import DataTypesEnum


@pytest.fixture
def sample_df():
    """Sample example for the tests."""
    return pd.DataFrame({"city": ["Madrid", "Sevilla"], "sales": [100, 120]})


# ---------------------------------------------------------------------
# TESTS: CSV / EXCEL / JSON / SQL LOADERS
# ---------------------------------------------------------------------
def test_load_data_csv(tmp_path, sample_df):
    """Tests loading from csv."""
    csv_path = tmp_path / "data.csv"
    sample_df.to_csv(csv_path, index=False)

    result = _load_data_csv(csv_path)
    pd.testing.assert_frame_equal(result, sample_df)


def test_load_data_excel(tmp_path, sample_df):
    """Tests loading from excel."""
    excel_path = tmp_path / "data.xlsx"
    sample_df.to_excel(excel_path, index=False)

    result = _load_data_excel(excel_path)
    pd.testing.assert_frame_equal(result, sample_df)

    result_sheet = _load_data_excel(excel_path, sheet_to_read=0)
    pd.testing.assert_frame_equal(result_sheet, sample_df)


def test_load_data_json(tmp_path, sample_df):
    """Tests loading data from json."""
    json_path = tmp_path / "data.json"
    sample_df.to_json(json_path, orient="records")

    result = _load_from_json(json_path)
    assert list(result.columns) == list(sample_df.columns)
    assert len(result) == len(sample_df)


def test_load_from_sql(monkeypatch, sample_df):
    """Simulate pandas.read_sql call."""

    def fake_read_sql(query, db):
        assert query == "SELECT * FROM test_table"
        return sample_df

    monkeypatch.setattr(pd, "read_sql", fake_read_sql)
    result = _load_from_sql("fake_db", "SELECT * FROM test_table")
    pd.testing.assert_frame_equal(result, sample_df)


# ---------------------------------------------------------------------
# TESTS: LOAD_DATA ORCHESTRATOR
# ---------------------------------------------------------------------
def test_load_data_csv_mode(tmp_path, sample_df):
    """Tests loading data with csv modes."""
    csv_path = tmp_path / "data.csv"
    sample_df.to_csv(csv_path, index=False)
    result = load_data(DataTypesEnum.CSV, path_to_data=csv_path)
    pd.testing.assert_frame_equal(result, sample_df)


def test_load_data_excel_mode(tmp_path, sample_df):
    """Tests loading data with Excel."""
    excel_path = tmp_path / "data.xlsx"
    sample_df.to_excel(excel_path, index=False)
    result = load_data(DataTypesEnum.EXCEL, path_to_data=excel_path)
    pd.testing.assert_frame_equal(result, sample_df)


def test_load_data_json_mode(tmp_path, sample_df):
    """Tests loading data with JSON."""
    json_path = tmp_path / "data.json"
    sample_df.to_json(json_path, orient="records")
    result = load_data(DataTypesEnum.JSON, path_to_data=json_path)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(sample_df)


def test_load_data_sql_mode(monkeypatch, sample_df):
    """Tests loading data with SQL."""

    def fake_read_sql(query, db):
        return sample_df

    monkeypatch.setattr(pd, "read_sql", fake_read_sql)
    result = load_data(DataTypesEnum.SQL, db="fake_db", query="SELECT * FROM x")
    pd.testing.assert_frame_equal(result, sample_df)


@pytest.mark.parametrize("mode", ["not_enum", 123, None])
def test_load_data_invalid_type_raises(mode):
    """Tests loading data with invalid types."""
    with pytest.raises(TypeError):
        load_data(mode)


def test_load_data_missing_path_raises():
    """Tests dloading data with missing paths."""
    with pytest.raises(ValueError):
        load_data(DataTypesEnum.CSV)

    with pytest.raises(ValueError):
        load_data(DataTypesEnum.EXCEL)

    with pytest.raises(ValueError):
        load_data(DataTypesEnum.JSON)

    with pytest.raises(ValueError):
        load_data(DataTypesEnum.SQL, db=None, query=None)


def test_load_data_not_implemented():
    """Tests loading data."""
    with pytest.raises(NotImplementedError):
        load_data(DataTypesEnum.OTHER)


# ---------------------------------------------------------------------
# TESTS: METADATA TAGGING
# ---------------------------------------------------------------------
def test_tag_df_with_metadata(sample_df):
    """Tests tags df with metadata."""
    tagged = tag_df_with_metadata(sample_df, "year", 2024)
    assert "year" in tagged.columns
    assert (tagged["year"] == 2024).all()
    # Ensure original not modified
    assert "year" not in sample_df.columns


# ---------------------------------------------------------------------
# TESTS: SAFE CONCAT
# ---------------------------------------------------------------------
def test_safe_concat_valid(sample_df):
    """Tests safe concats valids."""
    df2 = sample_df.copy()
    combined = safe_concat_dataframes([sample_df, df2])
    assert len(combined) == len(sample_df) * 2
    assert list(combined.columns) == list(sample_df.columns)


def test_safe_concat_different_columns_raises(sample_df):
    """Tests different columns issues on dataframes."""
    df_bad = pd.DataFrame({"city": ["Madrid"], "income": [500]})
    with pytest.raises(ValueError):
        safe_concat_dataframes([sample_df, df_bad])


def test_safe_concat_non_dataframe_raises(sample_df):
    """Tests error non dataframe on concat."""
    with pytest.raises(TypeError):
        safe_concat_dataframes([sample_df, "not_a_df"])


def test_safe_concat_empty_list_raises():
    """Tests safe concat."""
    with pytest.raises(ValueError):
        safe_concat_dataframes([])


# ---------------------------------------------------------------------
# TESTS: SAVE DATAFRAME TO CSV
# ---------------------------------------------------------------------
def test_save_dataframe_to_csv(tmp_path, sample_df):
    """Tests save dataframe."""
    file_path = tmp_path / "saved.csv"
    result_path = save_dataframe_to_csv(sample_df, file_path)
    assert result_path.exists()
    loaded = pd.read_csv(result_path)
    pd.testing.assert_frame_equal(loaded, sample_df)
