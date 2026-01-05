
import json
import os
import sys

import paths as paths
from functions.llm_config import LLMConfig
from functions.retrieval import QuestionRetriever
from functions.query_decomposer import QueryDecomposer
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage


import re
from pydantic import BaseModel, Field
from typing import List

from pathlib import Path

from paths import EXTENDED_SCHEMA_PROMPT

class TextToSQLResult(BaseModel):
    sql_query: str = Field(..., description="The SQL query generated from the natural language input")
    schema_linking_tables: List[str] = Field(..., description="List of tables used in FROM clause .")


class TextToSQLExtendedSchema:
    def __init__(self,
                 llm, decomposer_module, retriever, prompt_path, debug=False
        ) -> None:
        
        self.llm = llm
        self.decomposer_module = decomposer_module
        self.retriever = retriever
        self.debug = debug
        
        try:

            with open(prompt_path, "r") as file:
                self.text_to_sql_prompt = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"O arquivo {prompt_path} não foi encontrado.")
            
    def translate_text_to_sql(self, question):
        if self.retriever is None:
            context = ""
        else:
            context = self.__build_context(question)

        llm_with_structured_output = self.llm.with_structured_output(TextToSQLResult)

        prompt = self.text_to_sql_prompt.format(input=question, samples=context)
        result = llm_with_structured_output.invoke([HumanMessage(content=prompt)])

        return result
    
    def __build_context(self, question):

        # Decompose the question
        sub_questions = self.decomposer_module.decompose(question)
        print("Decomposition")
        print(sub_questions)
        # creating a string of few-shot examples for each sub-question
        few_shot_examples = ""
        for sub_question in sub_questions:
            few_shot_examples += self.retriever.get_similar_examples(text=sub_question, n=5)
        
        print("DFE")
        print(few_shot_examples)
            
        context = f"""
        Here is extra context for you to solve this text to SQL translation:

        Original question can be decomposed into the following sub-questions: \n {sub_questions}.

        Here are some examples of how to write SQL queries on this schema: \n {few_shot_examples}
        
        """

        return context



