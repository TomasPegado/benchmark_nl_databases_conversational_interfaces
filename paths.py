import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()


PROJECT_ROOT = Path(__file__).parent.absolute()
experiment_root_path = str(PROJECT_ROOT)
run_environment = os.getenv("RUN_ENVIRONMENT", "")


#Database
SCHEMA = os.getenv("EXPERIMENT_SCHEMA")
PREFIX = os.getenv("EXPERIMENT_NAME")

DB_INFO_PATH = os.path.join(experiment_root_path, "connections")
DB_CONNECTION_FILE = os.path.join(DB_INFO_PATH, f"{run_environment}{PREFIX}_db_connection.json")

#Text-to-sql Tool
PROMPT_DECOMPOSER_FILE= os.path.join(experiment_root_path, "eval_agent", "text2sql_agent", "text_to_sql",  "prompts", "prompt_decomposer.txt")
EXTENDED_SCHEMA_PROMPT= os.path.join(experiment_root_path, "eval_agent", "text2sql_agent", "text_to_sql", "prompts", f"rag_prompt_view_sql_queries_{SCHEMA.lower()}.txt")
NUMBER_OF_SAMPLES = 8

DATASET_SYNTHETIC = os.getenv("DATASET_SYNTHETIC", "")
EMBEDDINGS = os.getenv("EMBEDDINGS_FILE", "")

if DATASET_SYNTHETIC == "":
    DATASET_SYNTHETIC_PATH = ""
else:
    DATASET_SYNTHETIC_PATH = os.path.join(experiment_root_path, "eval_agent", "text2sql_agent", "text_to_sql", DATASET_SYNTHETIC)

if EMBEDDINGS == "":
    EMBEDDINGS_PATH = ""
else:
    EMBEDDINGS_PATH = os.path.join(experiment_root_path, "eval_agent", "text2sql_agent", "text_to_sql", EMBEDDINGS)

# User Agent
CHATBOT_PROMPT_PATH= os.path.join(experiment_root_path, "eval_agent", "user_agent", "chat_prompts", "chatbot_prompt_v2_english.txt")


ENVIRONMENT = run_environment

from functions.dataset_utils import DatasetEvaluator

dataset_eval = DatasetEvaluator(
    dataset_file_path="",
    dataset_tables_path="",
    db_connection_file=DB_CONNECTION_FILE,
    dataset_name=PREFIX
)


if __name__ == "__main__":
    print(experiment_root_path)
    print(DB_CONNECTION_FILE)
    print(PROMPT_DECOMPOSER_FILE)
    print(CHATBOT_PROMPT_PATH)
    print(ENVIRONMENT)



