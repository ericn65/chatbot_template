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
from chatbot_template.utils.teacher.data_analysis import analyse_data
from chatbot_template.utils.teacher.data_loaders import (
    load_data,
    safe_concat_dataframes,
    tag_df_with_metadata,
)
from chatbot_template.utils.teacher.data_visualizers import DataVisualizer
from chatbot_template.utils.teacher.enums import DataTypesEnum


def run_bcn_example():
    """Main script."""
    base_dir = Path(__file__).resolve().parents[1]
    data_dir = base_dir / "chatbot_template" / "data"
    path_2023 = data_dir / "2023_pad_mdb_nacionalitat-regio_sexe.csv"
    path_2024 = data_dir / "2024_pad_mdb_nacionalitat-regio_sexe.csv"

    # 1️⃣ Load datasets
    df_2023 = load_data(DataTypesEnum.CSV, path_to_data=path_2023)
    df_2024 = load_data(DataTypesEnum.CSV, path_to_data=path_2024)

    # 2️⃣ Tag and merge
    df_2023 = tag_df_with_metadata(df_2023, "year", 2023)
    df_2024 = tag_df_with_metadata(df_2024, "year", 2024)
    df_all = safe_concat_dataframes([df_2023, df_2024])

    # 3️⃣ Analyse
    analysis = analyse_data(df_all)
    print("\n📊 BASIC STATS:")
    print(analysis["basic_stats"])

    print("\n🧩 COLUMN INFO:")
    print(analysis["column_info"])

    print("\n📈 NUMERIC SUMMARY:")
    print(analysis["numeric_summary"])

    print("\n📦 VALUE COUNTS:")
    print(analysis["value_counts"])

    # 4️⃣ Aggregate
    aggregator = DataAggregator(df_all)
    summary = aggregator.get_numeric_summary()
    print("\n📈 Numeric Summary:")
    print(summary)

    # 5️⃣ Visualize
    viz = DataVisualizer(df_all)
    viz.plot_correlation_matrix()
    viz.plot_by_category("Nom_Districte", "Valor")
    viz.auto_visualize()


if __name__ == "__main__":
    run_bcn_example()
