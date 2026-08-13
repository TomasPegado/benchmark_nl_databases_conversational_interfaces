from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from functions.llm_config import LLMConfig

import os
from dotenv import load_dotenv
load_dotenv()
import importlib

experiment = os.getenv("EXPERIMENT_NAME")

class ConversationalAgentNodes:
    def __init__(self, env: str, provider: str):
        self.env = env
        self.provider = provider
        match self.env:
            case "tec":
                # Importing the prompt for the experiment environment
                prompt_module_path = f"eval_agent.conversational_agent.prompts"
                prompt_module = importlib.import_module(prompt_module_path)
                self.ASSISTANT_PROMPT = prompt_module.ASSISTANT_PROMPT
                self.RAW_LLM_PROMPT = prompt_module.RAW_LLM_PROMPT
                
                # Importing the tools
                from eval_agent.conversational_agent.tool import TOOLS, RAW_LLM_SQL_EXECUTION_TOOL
                self.TOOLS = TOOLS
                self.RAW_LLM_SQL_EXECUTION_TOOL = RAW_LLM_SQL_EXECUTION_TOOL
            case _:
                raise ValueError(f"Invalid environment: {self.env}")
   
        self.LLM = LLMConfig(provider=self.provider, environment=self.env).get_llm(model=os.getenv("CONVERSATIONAL_AGENT_MODEL"))
   
    def assistant(self, state: MessagesState) -> MessagesState:
        """
        This function representes the single node on graph, is a ReAct assistant.
        It receives a query, decides if it is a NL question about database or not and returns a response
        based on that
        """
        
        
        if self.provider == "aws_bedrock":
            llm_with_tools = self.LLM.bind_tools(self.TOOLS)
        else:
            llm_with_tools = self.LLM.bind_tools(self.TOOLS, parallel_tool_calls=False)

        # llm_with_tools = self.LLM.bind_tools(self.TOOLS, parallel_tool_calls=False)
        
        feedback_error = ""
        if ("retry_reason" in state and state["retry_reason"] == "json_decode_error") and state["actual_number_of_retries"] < state["max_retries"]:
            feedback_error = "\n\nThe previous response was not in a valid JSON format. Please ensure that your response strictly adheres to the specified JSON structure and does not include any additional text or formatting outside of the JSON."

        prompt_with_schema = self.ASSISTANT_PROMPT+ feedback_error

        sys_msg = SystemMessage(content=prompt_with_schema)

        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}
    
    def raw_llm(self, state: MessagesState) -> MessagesState:
        """
        This function representes the single node on graph, is a Raw LLM assistant.
        It receives a query, decides if it is a NL question about database or not and returns a response
        based on that
        """
        if self.provider == "aws_bedrock":
            llm_with_tools = self.LLM.bind_tools(self.RAW_LLM_SQL_EXECUTION_TOOL)
        else:
            llm_with_tools = self.LLM.bind_tools(self.RAW_LLM_SQL_EXECUTION_TOOL, parallel_tool_calls=False)
        # llm_with_tools = self.LLM.bind_tools(self.RAW_LLM_SQL_EXECUTION_TOOL, parallel_tool_calls=False)
        
        feedback_error = ""
        if ("retry_reason" in state and state["retry_reason"] == "json_decode_error") and state["actual_number_of_retries"] < state["max_retries"]:
            feedback_error = "\n\nThe previous response was not in a valid JSON format. Please ensure that your response strictly adheres to the specified JSON structure and does not include any additional text or formatting outside of the JSON."

        prompt_with_schema = self.RAW_LLM_PROMPT+ feedback_error

        sys_msg = SystemMessage(content=prompt_with_schema)

        print("Raw LLM invoked")
        result = {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

        print("Raw LLM Result:")
        print(result)

        return result
    
