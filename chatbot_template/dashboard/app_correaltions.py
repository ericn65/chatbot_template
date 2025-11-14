from .layout import show_correlation_dashboard
from chatbot_template.config.config_dashboard import DashboardConfig


def run_correlations_dashboard(config: DashboardConfig | None = None):
    """
    Runs the correlation visualization dashboard.

    Parameters
    ----------
    config : DashboardConfig
        Dashboard configuration (title, default data path, layout…).
    """
    config = config or DashboardConfig()
    show_correlation_dashboard(config)


if __name__ == "__main__":
    run_correlations_dashboard()
