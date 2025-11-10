from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import START, StateGraph, MessagesState
from typing import Literal
from langchain_core.messages import HumanMessage
from eval_agent.text2sql_agent.nodes import TextToSQLAgentNodes
from langgraph.checkpoint.memory import MemorySaver

from eval_agent.text2sql_agent.tool_kaggle import TOOLS as TOOLS_KAGGLE

memory = MemorySaver()

def build_graph(have_memory: bool = True, env: Literal["tec"] = "tec") -> StateGraph:
    nodes = TextToSQLAgentNodes(env=env)

    match env:
        case "tec":
            TOOLS = TOOLS_KAGGLE
        case _:
            raise ValueError(f"Invalid environment: {env}")

    # Build graph
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", nodes.assistant)
    builder.add_node("tools", ToolNode(TOOLS))
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

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    messages = [HumanMessage(
        content="Tell about airports at elevations higher than 1,000 meters.")
    ]

    graph = build_graph(have_memory=True, env="tec")
    result = graph.invoke({"messages": messages}, config)

    for message in result["messages"]:
        print(message.content)
        print("-" * 50)