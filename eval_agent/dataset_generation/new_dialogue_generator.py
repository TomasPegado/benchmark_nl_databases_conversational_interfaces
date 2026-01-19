import os
import sys
from pathlib import Path
from typing import Dict, List, Any

root_path = Path().absolute().parent.parent.parent.parent
sys.path.append(str(root_path))

from functions.llm_config import LLMConfig
from functions.sqldatabase_langchain_utils import SQLDatabaseLangchainUtils
from pydantic import BaseModel, Field
from typing import List
import json
import oracledb
import random

class GroundTruth(BaseModel):
    tables_from_schema_linking: List[str] = Field(..., description="List of tables involved in the query.")
    golden_sql: str = Field(..., description="Valid SQL query corresponding to the question.")

class Interaction(BaseModel):
    interaction_id: str = Field(..., description="ID of the interaction.")
    speaker: str = Field(..., description="Who is speaking (always 'User').")
    utterance: str = Field(..., description="The natural language question.")
    intention: str = Field(..., description="Is the real intention of the user, it must be a natural language version of the question, considering that you don't now the global context of the dialogue or database information. Basically a compact version of the question, that agent must infer from the global context.")
    ground_truths: GroundTruth = Field(..., description="Details of the ground truth for the query.")

class Experiment(BaseModel):
    experiment_id: str = Field(..., description="Unique ID of the experiment.")
    total_expected_interactions: int = Field(..., description="Total number of interactions in the dialogue.")
    interactions: List[Interaction] = Field(..., description="List of interactions in the dialogue.")

class DialogueGenerator:
    def __init__(self, 
                 llm: LLMConfig,
                 database_name: str,
                 join_combination_data: list,
                 column_combination_data: list,
                 table_ddls_hashmap: dict,
                 output_file: str = "dialogue_dataset/{db_name}_dialogue_dataset.json",
                 database_connection: str = "datasets/{db_name}_db_connection.json",
                 sql_database_langchain: SQLDatabaseLangchainUtils = None,
                 language: str = "en",
                 interactions: int = 3,
                 max_columns_interactions: int = 2
                 ) -> None:
        
        self.join_combination_data = join_combination_data
        self.column_combination_data = column_combination_data
        self.table_ddls_hashmap = table_ddls_hashmap
        self.included_tables = list(table_ddls_hashmap.keys())
        self.tables_used = []
        self.dialogue_generator = llm.with_structured_output(Experiment)
        self.sql_database_langchain = sql_database_langchain
        self.interactions = interactions
        self.max_columns_interactions = max_columns_interactions
        self.max_column_combos_in_prompt = 10
        
        dialogue_generation_prompt_path = "prompts/new_dialogue_generation_prompt.txt"
        if language == "pt_br":
            dialogue_generation_prompt_path = "prompts/dialogue_generation_prompt_pt_br.txt"
        
        self.dialogue_generation_prompt = open(dialogue_generation_prompt_path, "r").read()
        self.output_file = output_file.format(db_name=database_name)
        self.database_connection = database_connection.format(db_name=database_name)

    def create_prompt_from_join_combination_data(self, i: int, join_combination_data: dict) -> str:
        """
        This function creates a personalized prompt for the dialogue generation. 

        The prompt contains the following information:
        - Experiment ID
        - Join tips str
        - Number of joins
        - Tables context (Create table clauses and column values examples)
        - Tables involved

        Args:
            i (int): Index of the join combination data
            join_combination_data (dict): Join combination data

        Returns:
            prompt (str): Prompt for the dialogue generation
        """

        experiment_id = str(i + 1)

        join_str = join_combination_data["combination_str"]
        tables_involved: List[str] = join_combination_data["tables"]
        
        target_table = tables_involved[0]

        tables_context = ""

        for table in tables_involved:
            ddl_text = self.table_ddls_hashmap.get(table, "DDL not found")

            tables_context += f"Table informations: {table}\nDDL:\n{ddl_text}"
        
        interaction_binary_list = self.random_binary_list(self.interactions, self.max_columns_interactions)
        
        # ---- Column combo context: pick combos that match the target table ----
        matching_column_combos = []

        for combo in self.column_combination_data:
            combo_tables = combo["tables"]

            # combo["tables"] may be a string or a list
            if isinstance(combo_tables, str):
                combo_tables = [t.strip() for t in combo_tables.split("|") if t.strip()]

            if target_table in combo_tables:
                matching_column_combos.append(combo)
        
        matching_column_combos = matching_column_combos[:self.max_column_combos_in_prompt]
        
        column_combo_str = "\n---\n".join(
            self.format_column_combo(c) for c in matching_column_combos
        )


        prompt = self.dialogue_generation_prompt.format(
        experiment_id=experiment_id,
        total_expected_interactions=self.interactions,
        interaction_binary_list=interaction_binary_list, 
        target_table=target_table,
        join_str=join_str,
        column_combo_str=column_combo_str,
        tables_involved=", ".join(tables_involved),
        tables_context=tables_context,
    )
        if target_table not in self.tables_used:
            self.tables_used.append(target_table)

        return prompt
    
    
    def create_prompt_from_column_combination_data(self, i: int, column_combination_data: dict) -> str:
        """
        Creates a dialogue-generation prompt based ONLY on a column combination.
        This is used to guarantee table coverage when a table does not appear
        in any join combination.

        - Uses the same dialogue_generation_prompt
        - Binary list is ALL 1s (column-only exploration)
        """

        experiment_id = str(i + 1)

        # ---- Target table ----
        # column_combination_data["tables"] may be a string or a list
        combo_tables = column_combination_data["tables"]
        if isinstance(combo_tables, str):
            combo_tables = [t.strip() for t in combo_tables.split("|") if t.strip()]

        # Use the first table as target (single-table combo expected here)
        target_table = combo_tables[0]

        # ---- Tables involved ----
        tables_involved = combo_tables

        # ---- Tables context (DDL only for involved tables) ----
        tables_context = ""
        for table in tables_involved:
            ddl_text = self.table_ddls_hashmap.get(table, "DDL not found")
            tables_context += f"Table informations: {table}\nDDL:\n{ddl_text}\n\n"

        # ---- Column combo context (single combo) ----
        column_combo_str = self.format_column_combo(column_combination_data)

        # ---- No joins in this mode ----
        join_str = "NO JOINS. THIS DIALOGUE MUST USE COLUMN COMBINATIONS ONLY."

        # ---- Binary list: all 1s ----
        interaction_binary_list = [1] * self.interactions

        # ---- Track table usage for coverage ----
        if target_table not in self.tables_used:
            self.tables_used.append(target_table)

        # ---- Format prompt ----
        prompt = self.dialogue_generation_prompt.format(
            experiment_id=experiment_id,
            total_expected_interactions=self.interactions,
            interaction_binary_list=interaction_binary_list,
            target_table=target_table,
            join_str=join_str,
            column_combo_str=column_combo_str,
            tables_involved=", ".join(tables_involved),
            tables_context=tables_context,
        )

        return prompt

        

    def generate_dialogue(self, prompt: str) -> str:
        return self.dialogue_generator.invoke(prompt)

    def create_dialogue_dataset(self) -> List[Experiment]:
        dialogues = []

        # Adicionar as tabelas para verificar coverage
        
        # Set k parameter to 3
        # Put the column combos and join combos in the prompt
        for i, join_combination_data in enumerate(self.join_combination_data):
            print(f" - Generating dialogue for combination {i+1} of {len(self.join_combination_data)}")

            if self.dialogue_exists_in_dataset(str(i + 1), self.output_file):
                print(f"[Using checkpoint]Dialogue for combination {i+1} already exists in {self.output_file}. Skipping...")
                continue
            
            prompt = self.create_prompt_from_join_combination_data(i, join_combination_data)

            dialogue = self.generate_dialogue(prompt)

            print(f"[Generated dialogue] {dialogue}")
            # Check the dialogue syntax, if it's not valid, retry up to 3 times using error messages as feedback
            retries = 0
            is_valid, feedback = self.check_dialogue_sintax(dialogue)
            while not is_valid and retries < 3:
                print(f"[Retrying] Dialogue for combination {i+1} is not valid. Retrying... ({retries+1}/3)")
                dialogue = self.generate_dialogue(prompt + feedback)

                is_valid, feedback = self.check_dialogue_sintax(dialogue)
                retries += 1

            if is_valid:
                self.save_dialogue_to_file(dialogue, self.output_file)
            
            dialogues.append(dialogue)
            
        # 2) Coverage pass: find tables not used in JOIN-based generation
        # -----------------------------
        used_tables_set = set(self.tables_used)  # self.tables_used is updated inside create_prompt_from_join_combination_data
        missing_tables = [t for t in self.included_tables if t not in used_tables_set]

        print(f"\n[Coverage] Included tables: {len(self.included_tables)}")
        print(f"[Coverage] Tables used so far: {len(used_tables_set)}")
        print(f"[Coverage] Missing tables: {len(missing_tables)}")

        if not missing_tables:
            return dialogues
        
        # 3) Generate dialogues for missing tables using COLUMN combos only
        table_to_column_combos = self.build_table_to_column_combos_map()
        print(table_to_column_combos)
        
        # Continue experiment ids after the join-combo loop to keep them unique
        next_experiment_id = len(self.join_combination_data) + 1

        for missing_table in missing_tables:
            print(f"[Coverage] Generating dialogue for missing table: {missing_table}")
            combos_for_table = table_to_column_combos.get(missing_table, [])

            if not combos_for_table:
                print(f"[Coverage] No column combos found for missing table: {missing_table}. Skipping...")
                continue

            # Pick one combo to generate a dialogue for this table (simple strategy: first one)
            column_combination_data = combos_for_table[0]

            exp_id_str = str(next_experiment_id)

            if self.dialogue_exists_in_dataset(exp_id_str, self.output_file):
                print(f"[Using checkpoint]Dialogue for coverage table {missing_table} (experiment {exp_id_str}) already exists. Skipping...")
                next_experiment_id += 1
                continue

            prompt = self.create_prompt_from_column_combination_data(
                next_experiment_id - 1,  # keep same "i+1" behavior as before
                column_combination_data,
            )

            dialogue = self.generate_dialogue(prompt)
            print(f"[Generated coverage dialogue] {dialogue}")

            retries = 0
            is_valid, feedback = self.check_dialogue_sintax(dialogue)
            while not is_valid and retries < 3:
                print(f"[Retrying] Coverage dialogue for table {missing_table} is not valid. Retrying... ({retries+1}/3)")
                dialogue = self.generate_dialogue(prompt + feedback)
                is_valid, feedback = self.check_dialogue_sintax(dialogue)
                retries += 1

            if is_valid:
                self.save_dialogue_to_file(dialogue, self.output_file)

            dialogues.append(dialogue)
            next_experiment_id += 1

        return dialogues

    def check_dialogue_sintax(self, dialogue: Experiment) -> tuple[bool, str]:
        if self.sql_database_langchain != None:
            return self.check_dialogue_sintax_all(dialogue)
        else:
            return self.check_dialogue_sintax_oracle(dialogue)
            
    def check_dialogue_sintax_all(self, dialogue: Experiment) -> tuple[bool, str]:
        """
        Verifies the SQL syntax of all queries in the dialogue.
        
        Args:
            dialogue (Experiment): The dialogue to be verified
            
        Returns:
            tuple[bool, str]: A tuple (success, feedback) where:
                - success: True if all queries are valid, False otherwise
                - feedback: Empty string if all queries are valid, or error message otherwise
        """
        
        sql_errors = []
        try:
                       
            # For each interaction in the dialogue
            for interaction in dialogue.interactions:
                sql = interaction.ground_truths.golden_sql
                interaction_id = interaction.interaction_id
                
                sql = sql.strip().rstrip(';')
                
                try:
                    print("SQL")
                    print(sql)
                    self.sql_database_langchain.run_in_database(sql)
                except Exception as e:
                    error_msg = f"Interaction {interaction_id}, SQL: '{sql}' - Error: {str(e)}"
                    print(error_msg)
                    sql_errors.append(error_msg)
            
            if not sql_errors:
                return True, ""
            
            feedback = "\n\n# Feedback: \nThe groundtruths SQLs that you generated gave me the following errors, try again but attention to the errors:\n"
            feedback += "\n".join(sql_errors)
            feedback += "\nDo it again fixing it please and you can maintain the same structure of everything except wrong SQLs."
            
            return False, feedback
            
        except Exception as e:
            error_msg = f"Error connecting to the database: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    
    def check_dialogue_sintax_oracle(self, dialogue: Experiment) -> tuple[bool, str]:
        """
        Verifies the SQL syntax of all queries in the dialogue.
        
        Args:
            dialogue (Experiment): The dialogue to be verified
            
        Returns:
            tuple[bool, str]: A tuple (success, feedback) where:
                - success: True if all queries are valid, False otherwise
                - feedback: Empty string if all queries are valid, or error message otherwise
        """
        # Loads the database connection settings
        with open(self.database_connection, "r") as file:
            db_config = json.load(file)
            
        db_host = db_config["DB_HOST"]
        db_port = db_config["DB_PORT"]
        db_user = db_config["DB_USER_NAME"]
        db_pass = db_config["DB_PASS"]
        service_name = db_config["SERVICE_NAME"]
        
        dsn = f"{db_host}:{db_port}/{service_name}"
        
        sql_errors = []
        
        try:
            # Connects to the database
            connection = oracledb.connect(
                user=db_user,
                password=db_pass,
                dsn=dsn
            )
            cursor = connection.cursor()
            
            # For each interaction in the dialogue
            for interaction in dialogue.interactions:
                sql = interaction.ground_truths.golden_sql
                interaction_id = interaction.interaction_id
                
                sql = sql.strip().rstrip(';')
                
                try:
                    cursor.execute(sql)
                    cursor.fetchall()
                except Exception as e:
                    error_msg = f"Interaction {interaction_id}, SQL: '{sql}' - Error: {str(e)}"
                    print(error_msg)
                    sql_errors.append(error_msg)
                    
            cursor.close()
            connection.close()
            
            if not sql_errors:
                return True, ""
            
            feedback = "\n\n# Feedback: \nThe groundtruths SQLs that you generated gave me the following errors, try again but attention to the errors:\n"
            feedback += "\n".join(sql_errors)
            feedback += "\nDo it again fixing it please and you can maintain the same structure of everything except wrong SQLs."
            
            return False, feedback
            
        except Exception as e:
            error_msg = f"Error connecting to the database: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def dialogue_exists_in_dataset(self, experiment_id: str, output_file: str) -> bool:
        """
        Verify if a dialogue with the specified experiment ID already exists in the output file.
        
        Args:
            experiment_id (str): Experiment ID to be verified
            output_file (str): Path to the output JSON file

        Returns:
            bool: True if the dialogue exists, False otherwise
        """
        try:
            if not os.path.exists(output_file):
                return False
                
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Garante que há uma chave 'dataset' no JSON
            if "dataset" not in existing_data:
                return False
                
            # Itera pelos experimentos na lista dataset
            for experiment in existing_data["dataset"]:
                if experiment.get("experiment_id") == experiment_id:
                    return True
                    
            return False
        except (json.JSONDecodeError, FileNotFoundError):
            # If the file is not a valid JSON or does not exist, return False
            return False
    
    def save_dialogue_to_file(self, dialogue: Experiment, output_file: str) -> None:
        """
        Adds a dialogue to the output JSON file in the format {"dataset": [...]}.
        If the file does not exist, it will be created with the correct structure.
        
        Args:
            dialogue (Experiment): Dialogue object to be added
            output_file (str): Path to the output JSON file
        """
        try:
            # Convert the dialogue to a dictionary
            # dialogue_dict = dialogue.model_dump()
            dialogue_dict = dialogue.dict()

            print(f"[Saving dialogue] {dialogue_dict}")
            
            # Verify if the file exists
            if os.path.exists(output_file):
                # Load existing data
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        
                    # Check if the existing data has the expected structure
                    if "dataset" not in existing_data:
                        # If not, create the correct structure
                        existing_data = {"dataset": []}
                except json.JSONDecodeError:
                    # If the file is not a valid JSON, start with the correct structure
                    existing_data = {"dataset": []}
            else:
                # If the file does not exist, start with the correct structure
                existing_data = {"dataset": []}
            
            # Add the new dialogue to the dataset array
            existing_data["dataset"].append(dialogue_dict)
            
            # Save the updated data to the file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
            print(f"Dialogue added successfully to {output_file}")
        except Exception as e:
            print(f"Error saving the dialogue: {str(e)}")
    
    def random_binary_list(self, n: int, k: int) -> List[int]:
        """
        Returns a list of length n containing random 0s and 1s
        with equal probability.
        n is supposed to be the number of iteractions in the dialogue.
        """
        list_result = []
        while n > 0:
            a = random.randint(0, 1)
            if a == 1:
                if k > 0:
                    list_result.append(1)
                    k -= 1
                else:
                    list_result.append(0)
            else:
                list_result.append(0)
            n -= 1

        return list_result
    
    def format_column_combo(self, combo: dict) -> str:
        """
        Convert a column-combo dict into a compact, readable string
        suitable for prompt inclusion.
        """

        def col(c):
            return f"{c['table']}.{c['column']}"

        select_str = ", ".join(col(c) for c in combo["select_columns"])

        agg_str = ", ".join(
            f"{a['func']}(*)"
            if a["column"] is None
            else f"{a['func']}({col(a['column'])})"
            for a in combo.get("aggregations", [])
        )

        group_by_str = ", ".join(col(c) for c in combo.get("group_by", []))

        filter_str = ", ".join(
            f"{col(f['column'])} {f['op']} {f['value_hint']}"
            for f in combo.get("filters", [])
        )

        order_by = combo.get("order_by")
        order_str = (
            f"{col(order_by)} {combo.get('order_dir', '')}".strip()
            if order_by
            else ""
        )

        return (
            f"COMBO_ID: {combo['combo_id']}\n"
            f"DB_ID: {combo['db_id']}\n"
            f"TABLES: {combo['tables']}\n"
            f"SELECT: {select_str}\n"
            f"AGGREGATIONS: {agg_str}\n"
            f"GROUP_BY: {group_by_str}\n"
            f"FILTERS: {filter_str}\n"
            f"ORDER_BY: {order_str}\n"
            f"RATIONALE: {combo['rationale']}\n"
        )
    
    def build_table_to_column_combos_map(self) -> Dict[str, List[dict]]:
        """
        Builds a lookup map:
            { table_name: [column_combo_dict, ...] }

        - Accepts combo["tables"] as either:
            - a list of table names, or
            - a '|' separated string of table names
        """
        table_to_column_combos: Dict[str, List[dict]] = {}

        for combo in self.column_combination_data:
            combo_tables = combo.get("tables", [])

            if isinstance(combo_tables, str):
                combo_tables = [t.strip() for t in combo_tables.split("|") if t.strip()]

            for t in combo_tables:
                table_to_column_combos.setdefault(t.lower(), []).append(combo)

        return table_to_column_combos