from chatbot_template.utils.workflow import WorkflowEngine
import pandas as pd
from typing import Any

# EJEMPLO CARGAR BBDD INFO
database_info = pd.read_csv("chatbot_template/data/bd_iabd.csv")

# ejemplo bbdd users
template_users: dict[str, Any] = {
    "user_id": "",
    "datetime": "",
    "user_name": "",
    "password": "",
    "favourite_animal": "",
    "loves_maths":"",
}

# EJEMPLO INICIALIZAR LA BBDD
dataframe_users: pd.DataFrame = pd.DataFrame(template_users)

