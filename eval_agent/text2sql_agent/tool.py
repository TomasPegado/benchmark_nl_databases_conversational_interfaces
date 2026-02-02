import json
# import sys
# from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()



# root_path = Path().absolute().parent.parent
# sys.path.append(str(root_path))
# print()
from functions.llm_config import LLMConfig
from eval_agent.text2sql_agent.text_to_sql.text_to_sql_extended_schema import TextToSQLExtendedSchema
from functions.retrieval import QuestionRetriever
from functions.query_decomposer import QueryDecomposer

import paths as paths


experiment = os.getenv("EXPERIMENT_NAME")

GPT4O = LLMConfig(provider="azure").get_llm(model="gpt-4o")

prompt_path = paths.EXTENDED_SCHEMA_PROMPT
DATASET_SYNTHETIC_PATH = paths.DATASET_SYNTHETIC_PATH
EMBEDDINGS_PATH = paths.EMBEDDINGS_PATH

decomposer = QueryDecomposer(
    GPT4O,
    paths.PROMPT_DECOMPOSER_FILE,
    False
)

with open(paths.DB_CONNECTION_FILE, "r") as f:
    db_connection = json.load(f)

if DATASET_SYNTHETIC_PATH == "" or EMBEDDINGS_PATH == "":
    print("Dataset path or embeddings path is not set. Please check the .env configuration.")
    retriever = None

else:   
    retriever = QuestionRetriever(
        dataset_path=DATASET_SYNTHETIC_PATH,
        vectors_path=EMBEDDINGS_PATH,
        # vectorize=True
    )
    retriever.remove_duplicates()


text_to_sql =  TextToSQLExtendedSchema(GPT4O, decomposer, retriever, prompt_path, debug=False)

def execute_sql_query(sql_query):
    try:
        result = paths.dataset_eval.run_sql_query(sql_query)
        # result = '''
        #     prop, value, description
        #     p-1, as, asasasasa
        #     p-2, as, saddds
        #     p-3, cd, asasas
        # '''
        return result
    except Exception as e:
        return str(e)
    
def convert_text_to_sql_and_execute(query, limit=3) -> str:
    """
    Converts a natural language query to an SQL query based on the current database schema and execute the sql
    generated on database.
    Args:
        query (str): natural language query.
    """
    text_to_sql_result = text_to_sql.translate_text_to_sql(query)

    text_to_sql_result.sql_query = text_to_sql_result.sql_query.replace("```sql", "").replace("```", "")

    if not text_to_sql_result.sql_query.strip().upper().startswith("SELECT"):
        text_to_sql_result.sql_query = "SELECT " + text_to_sql_result.sql_query

    # if not "FETCH FIRST" in ["query_string"]:
    #     text_to_sql_result.sql_query = text_to_sql_result.sql_query.replace(";", f" FETCH FIRST {limit} ROWS ONLY;")

    if "DISTINCT" in text_to_sql_result.sql_query:
        text_to_sql_result.sql_query = text_to_sql_result.sql_query.replace("DISTINCT", "")


    try:
        result = {
            "input": query,
            "schema_linking": text_to_sql_result.schema_linking_tables,
            "answer": execute_sql_query(text_to_sql_result.sql_query),
            "sql": text_to_sql_result.sql_query
        }

        return result
    
    except Exception as e:
        result = {
            "input": query,
            "schema_linking": text_to_sql_result.schema_linking_tables,
            "answer": e,
            "sql": text_to_sql_result.sql_query
        }

        return result

TOOLS = [convert_text_to_sql_and_execute]

#============================================== TESTING ==============================================

def test_retriever_output(test_query: str):
    """
    Test the retriever by showing the top k most similar questions and their answers.
    
    Args:
        query (str): The natural language query to test
        top_k (int): Number of similar questions to retrieve
        
    Returns:
        dict: Dictionary containing the query and retrieved similar questions with their metadata
    """

    print("\n====== TESTING RETRIEVER OUTPUT ======")

    result = retriever.get_similar_examples(text=test_query, n=3)

    print(f"Few-shot examples: \n{result}")

    print("====== END OF TESTING RETRIEVER OUTPUT ======\n")

def test_decomposer_output(test_query: str):
    """
    Test the decomposer by showing the decomposed questions and their answers.
    """
    print("\n====== TESTING DECOMPOSER OUTPUT ======")

    result = decomposer.decompose(test_query)

    print(f"Decomposed questions: \n{result}")

    print("====== END OF TESTING DECOMPOSER OUTPUT ======\n")

if __name__ == "__main__":

    test_query = "Detailed information about the river Alz, including its length, area, estuary elevation, and the country it belongs to."
    if retriever is not None:
        test_retriever_output(test_query)
    test_decomposer_output(test_query)
