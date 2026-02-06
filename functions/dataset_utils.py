from typing import List, Tuple
import pandas as pd
import json
import os
import re
import requests
import oracledb
import math

import time
from datetime import datetime
from collections import Counter
from io import StringIO
from dotenv import load_dotenv
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.api.types import is_numeric_dtype
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from functions.langchain_utils import get_llm

def clean_sql(sql_query):
    sql_query = sql_query.strip()
    if sql_query[-1] == ";":
        sql_query = sql_query[:-1]
    return sql_query


def string_jaccard(str_1: str, str_2: str):
    """
    Calculates string similarity using Jaccard (intersection / union), including repeated characters.
    """

    char_count_1 = Counter(str_1)
    char_count_2 = Counter(str_2)

    common_chars = set(char_count_1.keys()) & set(char_count_2.keys())
    intersection = sum([min(char_count_1[key], char_count_2[key]) for key in common_chars])

    sum_1 = sum(char_count_1.values())
    sum_2 = sum(char_count_2.values())

    union = sum_1 + sum_2 - intersection
    return intersection / union


def column_similarity(col1: pd.Series, col2: pd.Series, metric: str="jaccard", verbose=False) -> float:
    """
    Calculates similarity between two columns (pandas Series) based on the specified similarity metric.

    The available metrics are:
        - "jaccard": Jaccard coefficient (intersection / union)
        - "set1": Set containment w.r.t. column 1 (intersection / col1)
        - "set2": Set containment w.r.t. colunn 2 (intersection / col2)

    Args:
        - col1 (pandas.Series): Column 1
        - col2 (pandas.Series): Column 2
        - metric (str, optional): Similarity metric to use. Defaults to "jaccard".

    Returns:
        float: Similarity value
    """

    col_count1 = Counter(col1.fillna(""))
    col_count2 = Counter(col2.fillna(""))

    common_keys = set(col_count1.keys()) & set(col_count2.keys())

    intersection = sum([min(col_count1[key], col_count2[key]) for key in common_keys])

    sum_1 = sum(col_count1.values())
    sum_2 = sum(col_count2.values())

    if metric == "set1":
        denominator = sum_1
    elif metric == "set2":
        denominator = sum_2
    elif metric == "jaccard":
        denominator = sum_1 + sum_2 - intersection # union
    else:
        raise Exception(f"Invalid metric: \"{metric}\". Possible values are \"jaccard\", \"set1\" and \"set2\".")

    similarity = intersection / denominator if denominator > 0 else 0.0
    if verbose:
        print(f"C1: {col1.name} ({col1.dtype}), C2: {col2.name} ({col2.dtype}), sim.: {similarity}")
    return similarity


def table_similarity(table_1: pd.DataFrame, table_2: pd.DataFrame, metric: str="jaccard"):
    """
    Calculates the similarity between two pandas DataFrames based on the specified metric.

    The available metrics are:
        - "jaccard": Jaccard coefficient (intersection / union)
        - "set1": Set containment w.r.t. table 1 (intersection / table_1)
        - "set2": Set containment w.r.t. table 2 (intersection / table_2)

    Args:
        - table_1 (pd.DataFrame): Table 1
        - table_2 (pd.DataFrame): Table 2
        - metric (str, optional): Similarity metric to use. Defaults to "jaccard".

    Returns:
        float: Similarity between two tables
    """

    table_1 = table_1.fillna("")
    table_2 = table_2.fillna("")

    table_count_1 = Counter(table_1.itertuples(index=False, name=None))
    table_count_2 = Counter(table_2.itertuples(index=False, name=None))

    common_rows = set(table_count_1.keys()) & set(table_count_2.keys())

    intersection = sum([min(table_count_1[key], table_count_2[key]) for key in common_rows])

    sum_1 = sum(table_count_1.values())
    sum_2 = sum(table_count_2.values())

    if metric == "set1":
        denominator = sum_1
    elif metric == "set2":
        denominator = sum_2
    elif metric == "jaccard":
        denominator = sum_1 + sum_2 - intersection # union
    else:
        raise Exception(f"Invalid metric: \"{metric}\". Possible values are \"jaccard\", \"set1\" and \"set2\".")
    
    return intersection / denominator if denominator > 0 else 0.0


def create_adjusted_tables(true_table: pd.DataFrame,
                           predicted_table: pd.DataFrame,
                           similarity_matrix: List[List[float]],
                           column_similarity_threshold: float=0.5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Creates an adjusted predicted table by rearranging columns in the predicted table to match the ground truth table based on the similarity matrix between columns in the true_table and predicted_table. Drops columns that are not present in both tables.

    Args:
        true_table (pd.DataFrame): Ground truth table.
        predicted_table (pd.DataFrame): Predicted table.
        similarity_matrix (List[List[float]]): Similarity between each pair of columns in the true and predicted tables.
        column_similarity_threshold (float, optional): Threshold to consider two columns as matching. Defaults to 0.5.

    Returns:
        pd.DataFrame: Adjusted ground truth table.
        pd.DataFrame: Adjusted predicted table.
    """

    if len(similarity_matrix) != len(true_table.columns):
        raise Exception(f"Similarity matrix height did not match ground truth table columns.")
        
    if any(len(row) != len(predicted_table.columns) for row in similarity_matrix):
        raise Exception(f"Similarity matrix width did not match predicted table columns.")

    true_column_map = []
    predicted_column_map = []

    for i, true_column in enumerate(true_table.columns):
        max_similarity = 0
        max_similarity_column = ""

        for j, predicted_column in enumerate(predicted_table.columns):
            similarity = similarity_matrix[i][j]

            new_max_found = False
            if max_similarity == 0:
                new_max_found

            if similarity == max_similarity:
                # use string similarity as a tie-breaker
                previous_string_similarity = string_jaccard(max_similarity_column, true_column)
                current_string_similarity = string_jaccard(predicted_column, true_column)
                if current_string_similarity > previous_string_similarity:
                    new_max_found = True

            if similarity > max_similarity and predicted_column not in predicted_column_map:
                new_max_found = True

            if new_max_found:
                max_similarity = similarity
                max_similarity_column = predicted_column

        if max_similarity >= column_similarity_threshold:
            true_column_map.append(true_column)
            predicted_column_map.append(max_similarity_column)

    adjusted_true_table = true_table[true_column_map]
    adjusted_predicted_table = predicted_table[predicted_column_map]

    return adjusted_true_table, adjusted_predicted_table


def calculate_similarity(true_table: pd.DataFrame, predicted_table: pd.DataFrame, metric: str="jaccard", column_match_threshold: float=0.9):
    
    similarity_matrix = [[0 for _ in predicted_table.columns] for _ in true_table.columns]

    for i, true_column_name in enumerate(true_table.columns):
        for j, predicted_column_name in enumerate(predicted_table.columns):
            similarity_matrix[i][j] = column_similarity(true_table[true_column_name], predicted_table[predicted_column_name])

    adjusted_true_table, adjusted_predicted_table = create_adjusted_tables(true_table,
                                                                           predicted_table,
                                                                           similarity_matrix,
                                                                           column_similarity_threshold=column_match_threshold)

    column_matching_index = len(adjusted_true_table.columns) / len(true_table.columns)

    print(f"True cols: {true_table.columns}")
    print(f"Adj. True cols: {adjusted_true_table.columns}")
    print(f"Predicted cols: {predicted_table.columns}")
    print(f"Adj. Predicted cols: {adjusted_predicted_table.columns}")

    similarity_score = table_similarity(adjusted_true_table, adjusted_predicted_table, metric=metric)

    return similarity_score, column_matching_index


def calculate_all_scores(true_table: pd.DataFrame, predicted_table: pd.DataFrame, column_match_threshold: float=0.9):
    """
    Calculates similarity scores using Jaccard and set containment w.r.t. each table.
    """

    scores = {}

    for metric in ["jaccard", "set1", "set2"]:
        similarity_score, column_matching_index = calculate_similarity(true_table, predicted_table, metric, column_match_threshold=column_match_threshold)

        scores[metric] = {
            "column_match": column_matching_index,
            "similarity": similarity_score
        }
    
    return scores


class DatasetEvaluator:
    def __init__(self,
                 dataset_file_path='/datasets/mondial/mondial_dataset.json',
                 dataset_tables_path='/datasets/mondial/result_tables/',
                 db_connection_file='/datasets/mondial_db_connection.json',
                 dataset_name='mondial'):
        
        
        self.dataset_file_path = dataset_file_path
        self.dataset_tables_path = dataset_tables_path
        self.timer = 0.0

        load_dotenv()

        # Connection Info
        with open(db_connection_file, 'r', encoding="utf8") as f:
            db_connection_data = json.load(f)

        self.need_auth = False
        self.dataset_name = dataset_name
      


        # SQL
        self.db_username = db_connection_data['DB_USER_NAME']
        self.db_password = db_connection_data['DB_PASS']
        hostname = db_connection_data['DB_HOST']
        port = db_connection_data['DB_PORT']
        database = db_connection_data['DB_NAME']
        sqldriver = db_connection_data['SQL_DRIVER']
        servicename = db_connection_data['SERVICE_NAME']

        # self.dsnStr = cx_Oracle.makedsn(host = hostname,
        #                                 port = port,
        #                                 service_name = servicename).replace("SID", "SERVICE_NAME")
        
        self.dsnStr = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={hostname})(PORT={port}))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME={servicename})))"
        self.db_connection = None

        # Load dataset
        self.load_and_index_dataset()


    def load_and_index_dataset(self):
        """
        Loads the dataset from the path specified when instancing the class and indexes the dataset, so that the elements can be accessed using their IDs.
        """
        self.dataset = None
        self.id_to_index_map = {}
        try:
            with open(self.dataset_file_path, 'r', encoding="utf8") as f:
                self.dataset = json.load(f)["dataset"]
            
            for i, instance in enumerate(self.dataset):
                self.id_to_index_map[instance["id"]] = i
        except: 
           pass


    def try_datetime_format(self, column, date_format):
        """
        Tries to convert a pandas series to datetime using a specified format.
        If any conversion fails, returns the original series.
        
        Args:
            column (pd.Series): The column (series) to convert
            date_format (str): The date format to use for conversion
        
        Returns:
            pd.Series: The converted column or the original column if conversion fails
        """
        try:
            converted_column = column.apply(lambda x: datetime.strptime(str(x), date_format))
            converted_column = converted_column.apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime) else x)
            return converted_column
        except ValueError:
            return column

    def run_sql_query(self, SQL_query: str, close_connection: bool=False) -> pd.DataFrame:
        """
        Runs an SQL query using the specified database connection info.

        Args:
            SQL_query (string): The SQL query to run

        Returns:
            pandas.DataFrame: DataFrame containing the results
        """

        # Conects to the database if not already connected
        if self.db_connection is None:
            self.db_connection = oracledb.connect(
                user=self.db_username,
                password=self.db_password,
                dsn=self.dsnStr)
        
        if SQL_query.endswith(';'):
            SQL_query = SQL_query[:-1]
            

        # Basic security checks
        if "DROP" in SQL_query or "DELETE" in SQL_query or "TRUNCATE" in SQL_query or "UPDATE" in SQL_query or "INSERT" in SQL_query:
            return None

        result_df = pd.read_sql(SQL_query, con=self.db_connection)

        for col in result_df.columns:
            # result_df[col] = pd.to_datetime(result_df[col], format="%d-%b-%y", errors="ignore", infer_datetime_format=False)
            result_df[col] = self.try_datetime_format(result_df[col], "%d-%b-%y")
            try:
                result_df[col] = result_df[col].astype(float)
            except:
                result_df[col] = result_df[col].astype(str)

        # Close cursor and connection
        if close_connection:
            self.db_connection.close()
            self.db_connection = None

        return result_df
    
    def run_sql_query_by_id(self, instance_id: str, close_connection: bool=False) -> pd.DataFrame:
        return self.run_sql_query(self.dataset[self.id_to_index_map[instance_id]]["query"], close_connection=close_connection)

    def df_content_equal(self, df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
        """
        Checks if two DataFrames contain exactly the same rows, regardless of the order of rows and columns.

        Args:
            df1 (pandas.DataFrame): DataFrame 1
            df2 (pandas.DataFrame): DataFrame 2

        Returns:
            bool: Whether the two DataFrames contain the same rows
        """
        sorted_df1 = df1.sort_values(by=list(df1.columns)).reset_index(drop=True)
        sorted_df2 = df2.sort_values(by=list(df2.columns)).reset_index(drop=True)

        sorted_df1 = sorted_df1.sort_index(axis=1)
        sorted_df2 = sorted_df2.sort_index(axis=1)

        return sorted_df1.equals(sorted_df2)
    

    def rename_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renames columns with the same name in a DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame with duplicate column names

        Returns:
            pandas.DataFrame: The DataFrame with renamed columns
        """

        column_count = {}
        new_columns = []
        for column in df.columns:
            if column in column_count:
                column_count[column] += 1
                new_columns.append(f"{column}{column_count[column]}")
            else:
                column_count[column] = 0
                new_columns.append(column)

        df.columns = new_columns
        return df


    def calculate_similarities(self, query_df: pd.DataFrame, true_df: pd.DataFrame) -> float:
        """
        Calculates the similarity between a ground truth DataFrame (true_df) and a query DataFrame (query_df).
        The similarity score represents how well the query dataframe matches the true dataframe.
        The similarity score is equal to the minimum similarity found for any column in the true dataframe.
        The similarity between two columns is calculated as len(intersection) / len(union).

        Args:
            true_df (pandas.DataFrame): The ground truth DataFrame
            query_df (pandas.DataFrame): The DataFrame to evaluate

        Returns:
            float: The similarity value
        """
        
        min_total_similarity = 1.0
        print(true_df.head())
        for true_column in true_df.columns:
            max_similarity = 0.0
            for query_column in query_df.columns:
                similarity = column_similarity(query_df[query_column], true_df[true_column])
                if similarity > max_similarity:
                    max_similarity = similarity
            print(max_similarity)
            if max_similarity < min_total_similarity:
                min_total_similarity = max_similarity

        return min_total_similarity


    def df_rows_equal(self, query_df: pd.DataFrame, true_df: pd.DataFrame) -> bool:
        """
        Checks if query_df has the exact same rows as true_df, and the same or more columns as true_df.
        That is, returns true if all columns in true_df are present in query_df, and both DataFrames contain the same rows (regardless of index).

        Args:
            true_df (pandas.DataFrame): Ground truth dataframe.
            query_df (pandas.DataFrame): Evaluated dataframe.

        Returns:
            bool: Whether the conditions above are met.
        """

        true_df = self.rename_duplicate_columns(true_df)
        query_df = self.rename_duplicate_columns(query_df)

        sorted_true_columns = []
        for true_column in true_df.columns:
            print(true_df[true_column])
            sorted_true_columns.append(true_df[true_column].sort_values(ascending=True).reset_index(drop=True))

        sorted_query_columns = []
        for query_column in query_df.columns:
            print(query_df[query_column])
            sorted_query_columns.append(query_df[query_column].sort_values(ascending=True).reset_index(drop=True))

        for sorted_true_column in sorted_true_columns:
            matched = False
            for sorted_query_column in sorted_query_columns:
                columns_equal = False
                try:
                    pd.testing.assert_series_equal(sorted_true_column, sorted_query_column,
                                                   check_dtype=False,
                                                   check_series_type=False,
                                                   check_names=False)
                    columns_equal = True
                except AssertionError as e:
                    pass

                if columns_equal:
                    query_df.rename(columns={sorted_query_column.name: sorted_true_column.name})
                    matched = True
                    break
            if not matched:
                print(f"Column {sorted_true_column.name} (dtype: {sorted_true_column.dtype}) could not be matched")
                return False
        return True


    def compare_keyword_query(self,
                              result_table: pd.DataFrame,
                              true_table: pd.DataFrame,
                              verbose: bool=False,
                              similarity_threshold: float=0.95,
                              column_matching_threshold: float=0.8,
                              similarity_metric: str="jaccard") -> bool:
        """
        Compares a keyword query to ground truth.
        First, checks if keyword query strings are equal, and returns True if they are.
        If not, compares the result tables and returns True if they contain the same columns and rows.

        Args:
            result_table (pandas.DataFrame): The query result DataFrame
            true_table (pandas.DataFrame): The ground truth result DataFrame
            similarity_threshold (float, optional): Similarity value below which query is classified as incorrect. Default: 0.95
            column_matching_threshold (float, optional): Minimum fraction of ground truth table columns that has to be present in predicted table. Default: 0.8
            similarity_metric (str, optional): Similarity metric to use when comparing columns and tables.
                Possible values:
                - "jaccard": Jaccard index (intersection / union)
                - "set1": Set containment w.r.t. ground truth table (intersection / true_table)
                - "set2": Set containment w.r.t. predicted table (intersection / predicted_table)

        Returns:
            bool: Whether the two queries are equal
            float: Similarity value
            float: Column matching index
        """

        similarity, column_matching_index = calculate_similarity(true_table, result_table, metric=similarity_metric)

        query_correct = True
        if similarity < similarity_threshold or column_matching_index < column_matching_threshold:
            query_correct = False

        return query_correct, similarity, column_matching_index
    

    def compare_sql_query(self,
                          generated_query: str,
                          result_table: pd.DataFrame,
                          true_query: str,
                          true_table: pd.DataFrame,
                          similarity_threshold: float=0.95,
                          column_matching_threshold: float=0.8,
                          similarity_metric: str="jaccard") -> bool:
        """
        Compares an SQL query to ground truth.
        First, checks if SQL query strings are equal, and returns True if they are.
        If not, compares the result tables and returns True if they contain the same columns and rows.

        Args:
            generated_query (str): The input SQL query string
            result_table (pandas.DataFrame): The query result DataFrame
            true_query (str): The ground truth SQL query string
            true_table (pandas.DataFrame): The ground truth result DataFrame
            similarity_threshold (float, optional): Similarity value below which query is classified as incorrect. Default: 0.95
            column_matching_threshold (float, optional): Minimum fraction of ground truth table columns that has to be present in predicted table. Default: 0.8
            similarity_metric (str, optional): Similarity metric to use when comparing columns and tables.
                Possible values:
                - "jaccard": Jaccard index (intersection / union)
                - "set1": Set containment w.r.t. ground truth table (intersection / true_table)
                - "set2": Set containment w.r.t. predicted table (intersection / predicted_table)

        Returns:
            bool: Whether the two queries are equal
            float: Similarity value
            float: Column matching index
        """

        generated_query = generated_query.strip()
        if generated_query == "":
            return False, -1, -1

        if generated_query == true_query.strip():
            return True, 1.0, 1.0
        
        similarity, column_matching_index = calculate_similarity(true_table, result_table, metric=similarity_metric)

        query_correct = True
        if similarity < similarity_threshold or column_matching_index < column_matching_threshold:
            query_correct = False

        return query_correct, similarity, column_matching_index

    def compare_sql_query_similarity_and_semantic(self,
                          user_query: str,
                          generated_query: str,
                          result_table: pd.DataFrame,
                          true_query: str,
                          true_table: pd.DataFrame,
                          similarity_threshold: float=0.95,
                          column_matching_threshold: float=0.8,
                          similarity_metric: str="jaccard",
                          debug_mode: bool=False) -> bool:

        query_correct, similarity, column_matching_index = self.compare_sql_query(
            generated_query, result_table,
            true_query, true_table,
            similarity_threshold, column_matching_threshold, similarity_metric
        )

        if query_correct == False:
            query_correct = self.ai_as_judge_comparation(user_query, generated_query, true_query, result_table, true_table, debug_mode=debug_mode)

        return query_correct, similarity, column_matching_index

    def ai_as_judge_comparation(self,
                                user_query,
                                generated_query: str, true_query: str,
                                result_table: pd.DataFrame, true_table: pd.DataFrame,
                                debug_mode=True,
                                sample_size: int=5,
                                random_state: int=42):
        
        # # ---------- Sampling helper ----------
        def sample_df(df: pd.DataFrame) -> pd.DataFrame:
            if df is None or df.empty:
                return df

            return df.sample(sample_size, random_state=random_state)
        
        # ---------- Apply sampling ----------
        result_sample = sample_df(result_table)
        true_sample = sample_df(true_table)

        # # Convert to compact string
        # result_str = result_sample.to_markdown(index=False)
        # true_str = true_sample.to_markdown(index=False)
        
        prompt = f"""
# User Question Context:
The original user question is:
{user_query}
        
# Generated SQL Query:
The SQL query produced by the text-to-SQL agent is:
{generated_query}

# Generated Query Result:
The execution of the generated query returned the following data:
{result_sample}

# Ground Truth SQL Query:
The ground truth (correct) SQL query is:
{true_query}

# Ground Truth Query Result:
The execution of the ground truth query returned the following data:
{true_sample}

# Evaluation Question:
Based on the information provided above, do both SQL queries answer the user question? 
Even if the resulting dataframes have minor differences in ordering, formatting, or other formal aspects, do they produce equivalent responses to the original question?

# Tips:
If both the generated SQL query/Query Result have more information than the user question, please consider it as correct.
If both return empty dataframes, please consider it as correct, but the columns should be the same (consider also True if the ordering is different, or have more than expected).

Answer with a single character only, don't include any explanation or justification:
T = True
F = False


"""
        llm = get_llm(logprobs=True)

        result = llm.invoke(prompt)

        confidence = math.exp(result.response_metadata['logprobs']['content'][0]['logprob'])

        if debug_mode: print(f"[AI as JUDGE sql query correctness] Result: {result.content} with {confidence} of confidence. And result metadata: {result.response_metadata}")
        return result.content.strip().lower() == "t" and confidence >= 0.90

    def evaluate_query_batch(self,
                             queries: list[dict],
                             query_type: str="keyword",
                             verbose: bool=False,
                             delay: int=0,
                             similarity_metric: str="jaccard"):
        """
        Runs a batch of queries (keyword or sql) and compares the results to ground truth.

        Args:
            queries (list[dict]): Queries to evaluate (Keyword or SQL). Should be formatted as a list of dictionaries:
            {
                "id": ID of the corresponding query in the dataset,
                "query_string": Query string to evaluate
            }
            query_type (str): Type of query ("keyword" or "sql"). Default: "keyword"
            verbose (bool): Print debug info
            delay (int, optional): Seconds to sleep between queries. Default: 0
            similarity_metric (str, optional): Similarity metric to use when comparing columns and tables.
                Possible values:
                - "jaccard": Jaccard index (intersection / union)
                - "set1": Set containment w.r.t. ground truth table (intersection / true_table)
                - "set2": Set containment w.r.t. predicted table (intersection / predicted_table)
        """

        self.timer = 0.0

        for i, query in enumerate(queries):
            if verbose:
                print(f"Running query {i + 1}/{len(queries)}...\nQuery: {query['query_string']}")

            query["complexity"] = self.dataset[self.id_to_index_map[query["id"]]]["type"]
            query["correct"], query["similarity"], query["column_match"] = self.evaluate_dataset_query(query["query_string"],
                                                                            query["id"],
                                                                            query_type=query_type,
                                                                            verbose=verbose,
                                                                            similarity_metric=similarity_metric)

            if verbose:
                print(f"Correct: {query['correct']}")

            time.sleep(delay)

        if verbose:
            correct = 0
            for query in queries:
                if query["correct"]:
                    correct += 1
            print(f"Done.\nTotal correct queries: {correct/len(queries)}")

        print(f"Total time: {self.timer}")
        print(f"Time per query: {self.timer / len(queries)}")
        return queries

    def evaluate_dataset_query(self,
                       query_string: str,
                       dataset_instance_id: str,
                       query_type: str="keyword",
                       verbose: bool=False,
                       similarity_metric: str="jaccard") -> bool:
        """
        Runs a single query (keyword or sql) and compares the result to ground truth.
        
        Args:
            query_string (str): The keyword or SQL query
            dataset_instance_id (str): The ID of the corresponding database instance
            query_type (str): The type of query ("keyword" or "sql"). Default: "keyword"
            verbose (bool),
            similarity_metric (str, optional): Similarity metric to use when comparing columns and tables.
                Possible values:
                - "jaccard": Jaccard index (intersection / union)
                - "set1": Set containment w.r.t. ground truth table (intersection / true_table)
                - "set2": Set containment w.r.t. predicted table (intersection / predicted_table)

        Returns:
            bool: Whether the query is correct
            float: Similarity value
            float: Column matching index
        """
        dataset_instance = self.dataset[self.id_to_index_map[dataset_instance_id]]

        ground_truth_sql_query = self.dataset[self.id_to_index_map[dataset_instance_id]]["query"]
        print(ground_truth_sql_query)
        ground_truth_sql_result = self.run_sql_query(ground_truth_sql_query)

        return self.evaluate_query(query_string=query_string,
                                   ground_truth_sql_query=ground_truth_sql_query,
                                   query_type=query_type,
                                   verbose=verbose,
                                   similarity_metric=similarity_metric)
    
    def evaluate_query(self,
                       query_string: str,
                       ground_truth_sql_query: str,
                       query_type: str="keyword",
                       verbose: bool=False,
                       similarity_metric: str="jaccard") -> Tuple[bool, float, float]:
        """
        Runs a single query (keyword or sql) and compares the result to ground truth.
        
        Args:
            query_string (str): The predicted keyword or SQL query
            ground_truth_sql_query (str): The ground truth SQL query
            query_type (str): The type of query ("keyword" or "sql"). Default: "keyword"
            verbose (bool),
            similarity_metric (str, optional): Similarity metric to use when comparing columns and tables.
                Possible values:
                - "jaccard": Jaccard index (intersection / union)
                - "set1": Set containment w.r.t. ground truth table (intersection / true_table)
                - "set2": Set containment w.r.t. predicted table (intersection / predicted_table)

        Returns:
            bool: Whether the query is correct
            float: Similarity value
            float: Column matching index
        """
        
        ground_truth_sql_query = clean_sql(ground_truth_sql_query)
        ground_truth_sql_result = self.run_sql_query(ground_truth_sql_query)

        if verbose:
            print("Ground truth SQL result:")
            print(ground_truth_sql_result)

        if query_type == "sql":
            print(query_string)
            query_string = clean_sql(query_string)
            try:
                result_table = self.run_sql_query(query_string)
            except Exception as e:
                print(f"Error: {e}")
                return False, -1, -1

            query_matches_sql, similarity, column_matching_index = self.compare_sql_query(
                                                                            query_string,
                                                                            result_table,
                                                                            ground_truth_sql_query,
                                                                            ground_truth_sql_result,
                                                                            similarity_metric=similarity_metric)
            
            if query_matches_sql:
                print(f"True: query matches sql (Similarity: {similarity}, column match: {column_matching_index})")
                return True, similarity, column_matching_index
            
        print("False: no match found")
        return False, similarity, column_matching_index

