import dotenv
from pathlib import Path

env_variables = dotenv.dotenv_values()

OPEN_AI_KEY = env_variables.get('OPEN_AI_KEY')
ENV = env_variables.get('ENV', "dev")
DEFAULT_SQL_PATH = Path(__file__).parent / "dbSchema.sql"

OPEN_AI_MODEL = "gpt-4.1-mini"