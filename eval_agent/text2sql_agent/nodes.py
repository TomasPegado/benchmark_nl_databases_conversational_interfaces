from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from functions.llm_config import LLMConfig

class TextToSQLAgentNodes:
    def __init__(self, env: str):
        self.env = env
        self.model = ""
        match self.env:
            case "tec":
                # Importing the prompt for the mondial environment
                from eval_agent.text2sql_agent.prompts_mondial import TEXT_TO_SQL_PROMPT as MONDIAL_TEXT_TO_SQL_PROMPT
                from functions.gptconfig import MODEL_4O
                self.model = MODEL_4O
                self.TEXT_TO_SQL_PROMPT = MONDIAL_TEXT_TO_SQL_PROMPT

                # Importing the tools for the mondial environment
                from eval_agent.text2sql_agent.tool_mondial import TOOLS as MONDIAL_TOOLS
                self.TOOLS = MONDIAL_TOOLS
            case _:
                raise ValueError(f"Invalid environment: {self.env}")
   
    def assistant(self, state: MessagesState) -> MessagesState:
        """
        This function representes the single node on graph, is a ReAct assistant.
        He receives a query, decides if it is a NL question about database or not and returns a response
        based on that
        """

        LLM = LLMConfig(provider="azure", environment=self.env).get_llm(model=self.model)

        llm_with_tools = LLM.bind_tools(self.TOOLS, parallel_tool_calls=False)

        prompt_with_schema = self.TEXT_TO_SQL_PROMPT.format(input=state["messages"][-1].content)

        sys_msg = SystemMessage(content=prompt_with_schema)

        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}