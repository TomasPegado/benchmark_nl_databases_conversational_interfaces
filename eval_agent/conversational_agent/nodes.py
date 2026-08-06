from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from functions.llm_config import LLMConfig

import os
from dotenv import load_dotenv
load_dotenv()
import importlib

experiment = os.getenv("EXPERIMENT_NAME")

class ConversationalAgentNodes:
    def __init__(self, env: str):
        self.env = env
        match self.env:
            case "tec":
                # Importing the prompt for the experiment environment
                prompt_module_path = f"eval_agent.conversational_agent.prompts"
                prompt_module = importlib.import_module(prompt_module_path)
                self.ASSISTANT_PROMPT = prompt_module.ASSISTANT_PROMPT
                
                
                # Importing the tools for the mondial environment
                from eval_agent.conversational_agent.tool import TOOLS
                self.TOOLS = TOOLS
            case _:
                raise ValueError(f"Invalid environment: {self.env}")
   
        self.LLM = LLMConfig(provider="azure", environment=self.env).get_llm(model=os.getenv("CONVERSATIONAL_AGENT_MODEL"))
   
    def assistant(self, state: MessagesState) -> MessagesState:
        """
        This function representes the single node on graph, is a ReAct assistant.
        It receives a query, decides if it is a NL question about database or not and returns a response
        based on that
        """
        
        

        llm_with_tools = self.LLM.bind_tools(self.TOOLS, parallel_tool_calls=False)
        
        feedback_error = ""
        if ("retry_reason" in state and state["retry_reason"] == "json_decode_error") and state["actual_number_of_retries"] < state["max_retries"]:
            feedback_error = "\n\nThe previous response was not in a valid JSON format. Please ensure that your response strictly adheres to the specified JSON structure and does not include any additional text or formatting outside of the JSON."

        prompt_with_schema = self.ASSISTANT_PROMPT+ feedback_error

        sys_msg = SystemMessage(content=prompt_with_schema)

        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}
    
    # def assistant_without_tools(self, state: MessagesState) -> MessagesState:
    #     """
    #     This function representes the single node on graph, is a ReAct assistant.
    #     It receives a query, decides if it is a NL question about database or not and returns a response
    #     based on that
    #     """
        
        
    #     feedback_error = ""
    #     if ("retry_reason" in state and state["retry_reason"] == "json_decode_error") and state["actual_number_of_retries"] < state["max_retries"]:
    #         feedback_error = "\n\nThe previous response was not in a valid JSON format. Please ensure that your response strictly adheres to the specified JSON structure and does not include any additional text or formatting outside of the JSON."

    #     prompt_with_schema = self.ASSISTANT_PROMPT+ feedback_error

    #     sys_msg = SystemMessage(content=prompt_with_schema)
    #     response = self.LLM.invoke([sys_msg] + state["messages"])
    #     sql = response.sql_query
    #     result = {"messages": [self.LLM.invoke([sys_msg] + state["messages"])]}

    #     try:
    #         result = {
    #             "input": query,
    #             "schema_linking": text_to_sql_result.schema_linking_tables,
    #             "answer": execute_sql_query(text_to_sql_result.sql_query),
    #             "sql": text_to_sql_result.sql_query
    #         }

    #         return result
    
    #     except Exception as e:
    #         result = {
    #             "input": query,
    #             "schema_linking": text_to_sql_result.schema_linking_tables,
    #             "answer": e,
    #             "sql": text_to_sql_result.sql_query
    #         }

    #         return result
    
