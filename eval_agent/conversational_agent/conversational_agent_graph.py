from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import START, END, StateGraph, MessagesState
from typing import Literal
from langchain_core.messages import HumanMessage
from eval_agent.conversational_agent.nodes import ConversationalAgentNodes
from langgraph.checkpoint.memory import MemorySaver

from eval_agent.conversational_agent.tool import TOOLS, RAW_LLM_SQL_EXECUTION_TOOL

memory = MemorySaver()

def build_graph(have_memory: bool = True, env: Literal["tec"] = "tec") -> StateGraph:
    nodes = ConversationalAgentNodes(env=env)

    match env:
        case "tec":
            ASSISTANT_TOOLS = TOOLS
        case _:
            raise ValueError(f"Invalid environment: {env}")

    # Build graph
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", nodes.assistant)
    builder.add_node("tools", ToolNode(ASSISTANT_TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    # Compile graph
    return builder.compile(checkpointer=memory) if have_memory else builder.compile()

def build_graph_raw_llm(have_memory: bool = True, env: Literal["tec"] = "tec") -> StateGraph:
    nodes = ConversationalAgentNodes(env=env)

    match env:
        case "tec":
            RAW_LLM_SQL_EXECUTION_TOOLS = RAW_LLM_SQL_EXECUTION_TOOL
        case _:
            raise ValueError(f"Invalid environment: {env}")

    # Build graph
    builder = StateGraph(MessagesState)
    builder.add_node("raw_llm", nodes.raw_llm)
    builder.add_node("tools", ToolNode(RAW_LLM_SQL_EXECUTION_TOOLS))
    builder.add_edge(START, "raw_llm")
    builder.add_edge("raw_llm", END)
    builder.add_conditional_edges(
        "raw_llm",
        # If the latest message (result) from raw_llm is a tool call -> tools_condition routes to tools
        # If the latest message (result) from raw_llm is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "raw_llm")

    # Compile graph
    return builder.compile(checkpointer=memory) if have_memory else builder.compile()
