from eval_agent.user_agent.states.user_agent_state import UserState
from eval_agent.user_agent.nodes.user_agent_nodes import EvaluatorNodes
from typing import Literal
from langgraph.graph import StateGraph, START

def build_graph(text_to_sql_agent_memory: bool = True, env: Literal["tec"] = "tec") -> StateGraph:
    evaluator_nodes = EvaluatorNodes(agent_memory=text_to_sql_agent_memory, env=env)

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
    experiment = {
      "experiment_id": "17",
      "total_expected_interactions": 3,
      "interactions": [
        {
          "interaction_id": "1",
          "speaker": "User",
          "utterance": "Show me a list of all lakes along with their corresponding provinces.",
          "intention": "Show me a list of all lakes along with their corresponding provinces.",
          "ground_truths": {
            "tables_from_schema_linking": [
              "MONDIAL_GEO_LAKE",
              "MONDIAL_PROVINCE"
            ],
            "golden_sql": "SELECT l.LAKE, l.PROVINCE FROM MONDIAL_GEO_LAKE l JOIN MONDIAL_PROVINCE p ON l.PROVINCE = p.NAME AND l.COUNTRY = p.COUNTRY;"
          }
        },
        {
          "interaction_id": "2",
          "speaker": "User",
          "utterance": "Can you also include the population of each province?",
          "intention": "Show me the lakes with their provinces along with the population of the provinces.",
          "ground_truths": {
            "tables_from_schema_linking": [
              "MONDIAL_GEO_LAKE",
              "MONDIAL_PROVINCE"
            ],
            "golden_sql": "SELECT l.LAKE, l.PROVINCE, p.POPULATION FROM MONDIAL_GEO_LAKE l JOIN MONDIAL_PROVINCE p ON l.PROVINCE = p.NAME AND l.COUNTRY = p.COUNTRY;"
          }
        },
        {
          "interaction_id": "3",
          "speaker": "User",
          "utterance": "Now, limit the results to provinces with a population above 1,000,000 and show the area of these provinces as well.",
          "intention": "From the previous results, filter to include only provinces with a population greater than 1,000,000 and display the area of each province along with the lake and its province.",
          "ground_truths": {
            "tables_from_schema_linking": [
              "MONDIAL_GEO_LAKE",
              "MONDIAL_PROVINCE"
            ],
            "golden_sql": "SELECT l.LAKE, l.PROVINCE, p.AREA FROM MONDIAL_GEO_LAKE l JOIN MONDIAL_PROVINCE p ON l.PROVINCE = p.NAME AND l.COUNTRY = p.COUNTRY WHERE p.POPULATION > 1000000;"
          }
        }
      ]
    }

    eval_graph = build_graph(env="tec")
    eval_result = eval_graph.invoke({
      "experiment": experiment,
      "max_retries": 1,
      "debug_mode": True
    })

    print(eval_result["experiment_eval"])
