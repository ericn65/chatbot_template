from chatbot_template.config.config_dashboard import DashboardConfig
from chatbot_template.dashboard.training_dashboard import run_training_dashboard


def run_runing_training_dashboard(config: DashboardConfig | None = None):
    """
    Runs the correlation visualization dashboard.

    Parameters
    ----------
    config : DashboardConfig
        Dashboard configuration (title, default data path, layout…).
    """
    # config = config or DashboardConfig()
    run_training_dashboard()


if __name__ == "__main__":
    run_runing_training_dashboard()
