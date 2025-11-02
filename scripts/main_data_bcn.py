"""
Main entrypoint for the full data pipeline.

Steps:
1. Load multiple datasets
2. Merge and tag them
3. Analyse and aggregate
4. Visualize summaries
"""

from pathlib import Path

from chatbot_template.utils.teacher.data_aggregator import DataAggregator
from chatbot_template.utils.teacher.data_analysis import DataAnalyser
from chatbot_template.utils.teacher.data_loaders import (
    load_data,
    safe_concat_dataframes,
    tag_df_with_metadata,
)
from chatbot_template.utils.teacher.data_visualizers import DataVisualizer
from chatbot_template.utils.teacher.enums import DataTypesEnum


def run_bcn_example():
    """Main script."""
    data_dir = Path("data/")
    path_2023 = data_dir / "sales_2023.csv"
    path_2024 = data_dir / "sales_2024.csv"

    # 1️⃣ Load datasets
    df_2023 = load_data(DataTypesEnum.CSV, path_to_data=path_2023)
    df_2024 = load_data(DataTypesEnum.CSV, path_to_data=path_2024)

    # 2️⃣ Tag and merge
    df_2023 = tag_df_with_metadata(df_2023, "year", 2023)
    df_2024 = tag_df_with_metadata(df_2024, "year", 2024)
    df_all = safe_concat_dataframes([df_2023, df_2024])

    # 3️⃣ Analyse
    analyser = DataAnalyser(df_all)
    print("🔍 Basic stats:")
    print(analyser.get_basic_stats())
    print("\n📊 Column info:")
    print(analyser.get_column_info())

    # 4️⃣ Aggregate
    aggregator = DataAggregator(df_all)
    summary = aggregator.get_numeric_summary()
    print("\n📈 Numeric Summary:")
    print(summary)

    # 5️⃣ Visualize
    viz = DataVisualizer(df_all)
    viz.plot_correlation_matrix()
    viz.plot_by_category("city", "sales")
    viz.auto_visualize()


if __name__ == "__main__":
    run_bcn_example()
