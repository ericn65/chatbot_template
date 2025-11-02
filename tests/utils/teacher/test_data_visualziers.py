import pandas as pd
import pytest

from chatbot_template.utils.teacher.data_visualizers import DataVisualizer


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "city": ["Madrid", "Sevilla", "Valencia", "Madrid", "Sevilla"],
            "sales": [100, 120, 150, 130, 200],
            "profit": [10, 15, 20, 12, 30],
            "date": pd.date_range("2024-01-01", periods=5),
        }
    )


def test_init_accepts_dataframe(sample_df):
    viz = DataVisualizer(sample_df)
    assert isinstance(viz.data, pd.DataFrame)


def test_init_rejects_non_dataframe():
    with pytest.raises(TypeError):
        DataVisualizer("not a df")


def test_plot_distribution_invalid_column(sample_df):
    viz = DataVisualizer(sample_df)
    with pytest.raises(ValueError):
        viz.plot_distribution("nonexistent")


def test_plot_distribution_non_numeric(sample_df):
    viz = DataVisualizer(sample_df)
    with pytest.raises(TypeError):
        viz.plot_distribution("city")


def test_plot_boxplot_invalid_columns(sample_df):
    viz = DataVisualizer(sample_df)
    with pytest.raises(ValueError):
        viz.plot_boxplot("wrong", "profit")


def test_plot_correlation_matrix_no_numeric():
    df = pd.DataFrame({"city": ["A", "B"], "country": ["X", "Y"]})
    viz = DataVisualizer(df)
    with pytest.raises(ValueError):
        viz.plot_correlation_matrix()


def test_auto_visualize_runs(sample_df):
    viz = DataVisualizer(sample_df)
    viz.auto_visualize()  # Should not raise
