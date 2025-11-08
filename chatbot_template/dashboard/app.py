from .layout import show_dashboard
from chatbot_template.config.config_dashboard import DashboardConfig


def run_dashboard(config: DashboardConfig | None = None):
    """
    Running a dashboard for a desired configuration.

    Parameters
    ----------
    config : DashboardConfig
        The configuration archive of the dashbaord.
    """
    config = config or DashboardConfig()
    show_dashboard(config)


if __name__ == "__main__":
    run_dashboard()
