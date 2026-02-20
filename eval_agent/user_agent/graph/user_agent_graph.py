from eval_agent.user_agent.states.user_agent_state import UserState
from eval_agent.user_agent.nodes.user_agent_nodes import EvaluatorNodes
from typing import Literal
from langgraph.graph import StateGraph, START

import os
import json
from dotenv import load_dotenv
load_dotenv()

def build_graph(conversational_agent_memory: bool = True, env: Literal["tec"] = "tec") -> StateGraph:
    evaluator_nodes = EvaluatorNodes(agent_memory=conversational_agent_memory, env=env)

    graph_builder = StateGraph(UserState)
    graph_builder.add_node("Setup", evaluator_nodes.setup)
    graph_builder.add_node("User Interaction", evaluator_nodes.user_node)
    graph_builder.add_node("Check Response", evaluator_nodes.check_response)

    graph_builder.add_edge(START, "Setup")
    graph_builder.add_edge("Setup", "User Interaction")
    graph_builder.add_edge("User Interaction", "Check Response")
    graph_builder.add_conditional_edges("Check Response", evaluator_nodes.keep_going)

    return graph_builder.compile()

if __name__ == "__main__":
    dataset = os.getenv("EXPERIMENT_DATASET_NAME")
    with open(f"../dataset_generation/dialogue_dataset/{dataset}_dialogue_dataset.json", "r", encoding="utf-8") as f:
      experiment = json.load(f)[0]

    eval_graph = build_graph(env="tec")
    eval_result = eval_graph.invoke({
      "experiment": experiment,
      "max_retries": 1,
      "debug_mode": True
    })

    print(eval_result["experiment_eval"])
