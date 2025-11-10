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
      "experiment_id": "7",
      "total_expected_interactions": 3,
      "interactions": [
        {
          "interaction_id": "1",
          "speaker": "User",
          "utterance": "Which players were inducted into the Hall of Fame in 1936?",
          "intention": "Which players were inducted into the Hall of Fame in 1936?",
          "ground_truths": {
            "tables_from_schema_linking": [
              "THEHISTORYOFBASEBALL_HALL_OF_FAME"
            ],
            "golden_sql": "SELECT PLAYER_ID FROM THEHISTORYOFBASEBALL_HALL_OF_FAME WHERE YEARID = 1936 AND INDUCTED = 'Y';"
          }
        },
        {
          "interaction_id": "2",
          "speaker": "User",
          "utterance": "What was the salary of those players in 1985?",
          "intention": "What was the salary of the players inducted into the Hall of Fame in 1936 during the year 1985?",
          "ground_truths": {
            "tables_from_schema_linking": [
              "THEHISTORYOFBASEBALL_HALL_OF_FAME",
              "THEHISTORYOFBASEBALL_SALARY"
            ],
            "golden_sql": "SELECT S.PLAYER_ID, S.SALARY FROM THEHISTORYOFBASEBALL_SALARY S JOIN THEHISTORYOFBASEBALL_HALL_OF_FAME H ON S.PLAYER_ID = H.PLAYER_ID WHERE H.YEARID = 1936 AND H.INDUCTED = 'Y' AND S.YEAR_ = 1985;"
          }
        },
        {
          "interaction_id": "3",
          "speaker": "User",
          "utterance": "And which teams did they play for in 1985?",
          "intention": "Which teams did the players inducted into the Hall of Fame in 1936 play for in 1985?",
          "ground_truths": {
            "tables_from_schema_linking": [
              "THEHISTORYOFBASEBALL_HALL_OF_FAME",
              "THEHISTORYOFBASEBALL_SALARY"
            ],
            "golden_sql": "SELECT S.PLAYER_ID, S.TEAM_ID FROM THEHISTORYOFBASEBALL_SALARY S JOIN THEHISTORYOFBASEBALL_HALL_OF_FAME H ON S.PLAYER_ID = H.PLAYER_ID WHERE H.YEARID = 1936 AND H.INDUCTED = 'Y' AND S.YEAR_ = 1985;"
          }
        }
      ]
    },

    eval_graph = build_graph(env="tec")
    eval_result = eval_graph.invoke({
      "experiment": experiment,
      "max_retries": 1,
      "debug_mode": True
    })

    print(eval_result["experiment_eval"])
