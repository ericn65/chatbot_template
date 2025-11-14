from pathlib import Path

from chatbot_template.config.config_dashboard import DashboardConfig
from chatbot_template.dashboard.app_correaltions import run_correlations_dashboard

if __name__ == "__main__":
    config = DashboardConfig(
        title="📈 Correlation Dashboard",
        default_data_path=Path(
            "chatbot_template/data/Datos Proyecto-20251108/observations.csv"
        ),
    )
    run_correlations_dashboard(config)
