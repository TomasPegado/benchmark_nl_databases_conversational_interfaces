from eval_agent.text2sql_agent.kaggle_agent_graph import build_graph
from functions.llm_config import LLMConfig
from eval_agent.user_agent.states.user_agent_state import UserState
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from functions.dataset_utils import DatasetEvaluator
import json
from typing import Literal, Dict, Any, Optional
from langgraph.graph import END
from collections import deque
from pathlib import Path
import time
from datetime import datetime
import paths  
# from functions.sqldatabase_langchain_utils import SQLDatabaseLangchainUtils
import eval_agent.user_agent.prompts as prompts
from functions.gptconfig import MODEL_4O

# root_path = Path().absolute().parent.parent.parent.parent

class EvaluatorNodes:
    def __init__(self, agent_memory: bool = True, env: Literal[ "tec"] = "tec"):

        if env == "tec":
           
            self.EVALUATOR = DatasetEvaluator(
                dataset_file_path='',
                dataset_tables_path='',
                db_connection_file=paths.DB_CONNECTION_FILE,
                dataset_name='mondial'
            ) 
    
        else:
            self.EVALUATOR = None
  
        self.AGENT = build_graph(have_memory=agent_memory, env=env)
        self.llm = LLMConfig(provider="azure", environment=env).get_llm(model=MODEL_4O, max_tokens=2000)

    def classify_query_complexity(self, sql: Optional[str]) -> str:
        """Classifica a complexidade de uma query SQL baseada em heurísticas simples"""
        if sql is None:
            return "unknown"
        
        sql = sql.lower()
        
        # Contar joins
        joins = sql.count("join")
        
        # Contar condições where
        where_clauses = 0
        if "where" in sql:
            where_part = sql.split("where")[1].split("order by")[0].split("group by")[0]
            where_clauses = where_part.count("and") + where_part.count("or") + 1
        
        # Verificar uso de operações complexas
        has_aggregation = any(agg in sql for agg in ["count(", "sum(", "avg(", "min(", "max("])
        has_grouping = "group by" in sql
        has_ordering = "order by" in sql
        has_limit = "limit" in sql
        
        # Calcular score de complexidade
        complexity_score = joins + where_clauses
        if has_aggregation: complexity_score += 1
        if has_grouping: complexity_score += 1
        if has_ordering: complexity_score += 0.5
        if has_limit: complexity_score += 0.5
        
        # Classificar baseado no score
        if complexity_score <= 1:
            return "simples"
        elif complexity_score <= 3:
            return "média"
        else:
            return "complexa"

    def evaluate_turn(self, state: UserState, response: dict) -> dict:

        function_input = response["input"] if response["input"] else ""
        tables_from_schema_linking = response["schema_linking"] if response["schema_linking"] else []
        answer = response["answer"] if response["answer"] else ""
        golden_sql = response["sql"].replace("\n", " ") if response["sql"] else ""
        ground_truths = state["actual_turn"]["ground_truths"]

        tables_ground_truth = ground_truths["tables_from_schema_linking"]
        recall = self.calculate_tables_recall(tables_ground_truth, tables_from_schema_linking)

        intention = state["actual_turn"]["intention"]
        alignment = self.compare_intentions(function_input, intention, state["interaction_history"])

        evaluator = state.get("evaluator", None)
        ground_truth_golden_sql = ground_truths.get("golden_sql", None)
        if golden_sql == "":
            correctness = False
        else:
            if evaluator and ground_truth_golden_sql and golden_sql:
                try:
                    result_table = evaluator.run_sql_query(golden_sql)
                    true_table = evaluator.run_sql_query(ground_truth_golden_sql)
                    correctness, sim, col_match = evaluator.compare_sql_query_similarity_and_semantic(
                        user_query=function_input,
                        generated_query=golden_sql,
                        result_table=result_table,
                        true_query=ground_truth_golden_sql,
                        true_table=true_table,
                        similarity_threshold=0.8,
                        column_matching_threshold=0.5,
                        debug_mode=True
                    )
                except Exception as e:
                    print(f"[ERROR] Erro ao executar a query: {e}")
                    correctness = False
            else:
                
                correctness = True

        turn_eval = {
            "user_query": state["last_user_input"],
            "agent_reply": answer,
            "evaluation": {
                "text_to_sql_input": function_input,
                "user_intention": intention,
                "recall": recall,
                "alignment": alignment,
                "correctness": correctness,
                "expected_sql": ground_truth_golden_sql,
                "generated_sql": golden_sql
            }
        }

        return alignment, turn_eval

    def setup(self, state: UserState) -> UserState:
        """
        Start node, get all data from experiment structure and setup graph variables.
        """
        print("[NODE] Setup Node entered.")

        state["evaluator"] = self.EVALUATOR
        state["experiment_eval"] = []
        
        # Nova configuração do experimento
        state["experiment_config"] = {
            "max_retries": state.get("max_retries", 2),
            "model_version": state.get("model_version", "default"),
            "timestamp": datetime.now().isoformat(),
            "experiment_type": state.get("experiment_type", "standard")
        }
        
        # Inicializar dicionário de métricas de interação
        state["interaction_metrics"] = {}
        state["query_complexity"] = "unknown"
        state["retry_reason"] = None

        # Configuração existente
        state["turns"] = deque(state['experiment']["interactions"])
        state["max_retries"] = 2 if "max_retries" not in state else state["max_retries"]
        state["debug_mode"] = False if "debug_mode" not in state else state["debug_mode"]

        state["actual_number_of_retries"] = 0

        state["proceed"] = True
        state["go_next_interaction"] = True
        state["interactions_counting"] = 0

        state["dialogue_agent_config"] = {
            # Pattern will be dialogue_agent_<id>
            "configurable": {"thread_id": "dialogue_agent_" + state["experiment"]["experiment_id"]}
        }
        print("----" * 10)
        return state

    def user_node(self, state: UserState) -> UserState:
        """
        User Interaction node, this node simulate a real user behavior. We send a message to the agent and wait for a response, if the answer is the expected, we go to next turn. If not, we reply using feedbacks until get the expected answer (limited by a max of retries).
        """
        print("[NODE] User Interaction Node entered.")
        nl_query = ""

        # Check if we can go to next interaction.
        if state["go_next_interaction"]:
            state["interactions_counting"] += 1
            current_interaction_id = state["interactions_counting"]
            
            # Iniciar rastreamento de tempo da interação
            state["current_interaction_start_time"] = time.time()
            
            # Inicializar métricas para esta interação
            state["actual_number_of_retries"] = 0
            state["actual_turn"] = state["turns"].popleft() if state["turns"] else None

            if state["actual_turn"] is None:
                state["proceed"] = False
                return state
            
            if "intention" in state["actual_turn"]:
                original_intent = state["actual_turn"]["intention"]
            else:
                original_intent = "Unknown intent"
                
            state["interaction_metrics"][current_interaction_id] = {
                "original_intent": original_intent,
                "total_retries_needed": 0,
                "success_without_retry": True,
                "start_time": state["current_interaction_start_time"],
                "end_time": None
            }
            
            nl_query = state["actual_turn"]["utterance"]

        # If we can't go to next interaction, we will use the last user input and the chat history to generate a new feedback query.
        else:
            # Atualizar métricas da interação atual quando usamos feedback
            current_interaction_id = state["interactions_counting"]
            if current_interaction_id in state["interaction_metrics"]:
                state["interaction_metrics"][current_interaction_id]["total_retries_needed"] += 1
                state["interaction_metrics"][current_interaction_id]["success_without_retry"] = False
            
            prompt = prompts.USER_INTERACTION_PROMPT.format(
                chat_history=self.messages_to_string_list(state["last_response"]["messages"]), user_intention=state["actual_turn"]["intention"]
            )

            msg = HumanMessage(content=prompt)
            feedback_chain = self.llm | StrOutputParser()
            feedback = feedback_chain.invoke([msg])

            nl_query = feedback

        state["last_user_input"] = nl_query

        if state["debug_mode"]: print("[INFO] Enviando a query para o agente: ", nl_query)

        state["last_response"] = self.text_to_sql_agent(nl_query, state["dialogue_agent_config"])

        state["interaction_history"] = state["last_response"]["messages"]

        if "```json" in state["last_response"]["messages"][-1].content:
            state["last_response"]["messages"][-1].content = state["last_response"]["messages"][-1].content.replace(
                "```json", "").replace("```", "")

        if state["debug_mode"]: print(f"[INFO] O resultado da execução foi: {state['last_response']['messages'][-1].content}.\n")

        print("----" * 10)
        return state

    def check_response(self, state: UserState) -> UserState:
        """
        Nó que avalia se a resposta do agente está conforme o esperado.
        Caso o JSON não seja decodificado corretamente, tenta novamente,
        até atingir o número máximo de retries.
        """
        print("[NODE] Check Response Node entered.")
        
        # Obter o ID da interação atual
        current_interaction_id = state["interactions_counting"]

        try:
            print(f"[INFO] O resultado da execução foi: {state['last_response']['messages'][-1].content}.\n")
            json_str = self.extract_outer_json(state["last_response"]["messages"][-1].content)
            response = json.loads(json_str)

            answer = response["answer"]
            function_input = response["input"]
            golden_sql = response["sql"].replace("\n", " ")
            tables_from_schema_linking = response["schema_linking"]
        except json.JSONDecodeError as e:
            print(f"[ERROR] Erro ao decodificar JSON: {e}. Iniciando retry.")
            # Registrar razão do retry
            state["retry_reason"] = "json_decode_error"
            
            # Atualizar métricas da interação
            if current_interaction_id in state["interaction_metrics"]:
                state["interaction_metrics"][current_interaction_id]["total_retries_needed"] += 1
                state["interaction_metrics"][current_interaction_id]["success_without_retry"] = False
            
            state["actual_number_of_retries"] += 1
            return state

        chat_history = state["interaction_history"]
        ground_truths = state["actual_turn"]["ground_truths"]

        if state["debug_mode"]: print(f"[INFO] Avaliando o resultado: {response}.\n")

        need_user_feedback = self.need_feedback(chat_history)
        
        if need_user_feedback:
            # Realizar a avaliação para verificar alignment e correctness
            alignment, turn_eval = self.evaluate_turn(state, response)
            
            # Adicionar campo específico para feedback
            turn_eval["evaluation"]["needs_feedback"] = True
            turn_eval["evaluation"]["is_retry"] = state["actual_number_of_retries"] > 0
            turn_eval["evaluation"]["retry_count"] = state["actual_number_of_retries"]
            turn_eval["evaluation"]["retry_reason"] = "feedback_needed"
            turn_eval["evaluation"]["execution_time"] = time.time() - state["current_interaction_start_time"]
            turn_eval["evaluation"]["query_complexity"] = self.classify_query_complexity(
                turn_eval["evaluation"].get("expected_sql")
            )
            
            # Verificar se o alignment ou correctness é true
            correctness = turn_eval["evaluation"].get("correctness", False)
            
            # Se alignment for true, não tratamos como retry (removendo a condição "or correctness")
            if alignment:
                # Finalizar métricas da interação com sucesso
                if current_interaction_id in state["interaction_metrics"]:
                    state["interaction_metrics"][current_interaction_id]["end_time"] = time.time()
                
                state["go_next_interaction"] = True
                state["proceed"] = True if len(state["turns"]) > 0 else False
                state["retry_reason"] = None  # Resetar razão de retry
            else:
                # Registrar razão do retry
                state["retry_reason"] = "feedback_needed"
                
                # Atualizar métricas de retentativa
                state["actual_number_of_retries"] += 1
                if current_interaction_id in state["interaction_metrics"]:
                    state["interaction_metrics"][current_interaction_id]["total_retries_needed"] += 1
                    state["interaction_metrics"][current_interaction_id]["success_without_retry"] = False
                
                state["go_next_interaction"] = False
                state["proceed"] = state["actual_number_of_retries"] <= state["max_retries"]
            
            self.append_turn_evaluation(state, turn_eval)
            return state
        
        # Avaliação completa quando não precisa de feedback
        tables_ground_truth = ground_truths["tables_from_schema_linking"]
        recall = self.calculate_tables_recall(tables_ground_truth, tables_from_schema_linking)
        
        intention = state["actual_turn"]["intention"]
        alignment = self.compare_intentions(function_input, intention, chat_history)
        
        # Determinar complexidade da query
        ground_truth_golden_sql = ground_truths.get("golden_sql", None)
        query_complexity = self.classify_query_complexity(ground_truth_golden_sql)
        state["query_complexity"] = query_complexity
        
        # Calcular tempo de execução
        execution_time = time.time() - state["current_interaction_start_time"]
        
        # Verificar corretude
        evaluator = state.get("evaluator", None)
        correctness = True
        
        if evaluator and ground_truth_golden_sql and golden_sql != "":
            try:
                result_table = evaluator.run_sql_query(golden_sql)
                true_table = evaluator.run_sql_query(ground_truth_golden_sql)
                correctness, sim, col_match = evaluator.compare_sql_query_similarity_and_semantic(
                    user_query=function_input,
                    generated_query=golden_sql,
                    result_table=result_table,
                    true_query=ground_truth_golden_sql,
                    true_table=true_table,
                    similarity_threshold=0.8,
                    column_matching_threshold=0.5,
                    debug_mode=True
                )
            except Exception as e:
                print(f"[ERROR] Erro ao executar a query: {e}")
                correctness = False
                state["retry_reason"] = "query_execution_error"
        else:
            correctness = False
        
        # Construir o objeto de avaliação do turno com as novas métricas
        turn_eval = {
            "user_query": state["last_user_input"],
            "agent_reply": answer,
            "evaluation": {
                "text_to_sql_input": function_input,
                "user_intention": intention,
                "recall": recall,
                "alignment": alignment,
                "correctness": correctness,
                "expected_sql": ground_truth_golden_sql,
                "generated_sql": golden_sql,
                
                # Novos campos
                "is_retry": state["actual_number_of_retries"] > 0,
                "retry_count": state["actual_number_of_retries"],
                "retry_reason": state["retry_reason"],
                "execution_time": execution_time,
                "query_complexity": query_complexity
            }
        }
        
        self.append_turn_evaluation(state, turn_eval)

        if state["debug_mode"]: print("[INFO] A avaliação para esse turno foi: ", state["experiment_eval"][-1])

        # Se está alinhado com o que o usuário esperava e query está correta, podemos seguir para o próximo turno
        if alignment:
            # Finalizar métricas da interação com sucesso
            if current_interaction_id in state["interaction_metrics"]:
                state["interaction_metrics"][current_interaction_id]["end_time"] = time.time()
            
            state["go_next_interaction"] = True
            state["proceed"] = True if len(state["turns"]) > 0 else False
            state["retry_reason"] = None  # Resetar razão de retry
        else:
            # Registrar razão do retry
            if not alignment and not correctness:
                state["retry_reason"] = "alignment_and_correctness_failure"
            elif not alignment:
                state["retry_reason"] = "alignment_failure"
            elif not correctness:
                state["retry_reason"] = "correctness_failure"
                
            # Incrementar contador de retries
            state["actual_number_of_retries"] += 1
            
            # Atualizar métricas da interação
            if current_interaction_id in state["interaction_metrics"]:
                state["interaction_metrics"][current_interaction_id]["total_retries_needed"] += 1
                state["interaction_metrics"][current_interaction_id]["success_without_retry"] = False

            if state["actual_number_of_retries"] <= state["max_retries"]:
                state["go_next_interaction"] = False
                state["proceed"] = True
                
            elif state["turns"]:
                # Finalizando métricas desta interação mesmo com falha
                if current_interaction_id in state["interaction_metrics"]:
                    state["interaction_metrics"][current_interaction_id]["end_time"] = time.time()
                
                state["go_next_interaction"] = True
                state["proceed"] = True
                state["retry_reason"] = None  # Resetar razão de retry
            else:
                # Finalizando métricas desta interação na última tentativa
                if current_interaction_id in state["interaction_metrics"]:
                    state["interaction_metrics"][current_interaction_id]["end_time"] = time.time()
                
                state["proceed"] = False

        print("----" * 10)
        return state

    def keep_going(self, state: UserState) -> Literal["User Interaction", END]:
        """
        Function that serves as conditional edge, if state["proceed"] == True, we continue to the next node, otherwise we end the evaluation.
        Motives to end the evaluation:
        No more turns at experiment, or the last turn was not properly answered. Also decide to finish evaluation if max retries on a tool is reached.
        """
        print(f"[Conditional Edge] Continuamos a avaliação? {state['proceed']}")
        print("----" * 10)
        if state["proceed"]:
            return "User Interaction"
        else:
            return END

    # ===== Util functions =====
    def calculate_tables_recall(self, tables_ground_truth, tables_from_schema_linking):
        # True Positives / False negatives + True Positives = Recall
        TP, FN = 0, 0

        # Verificar se tables_from_schema_linking é uma string e tentar convertê-la para lista
        if isinstance(tables_from_schema_linking, str):
            try:
                import ast
                tables_from_schema_linking = ast.literal_eval(tables_from_schema_linking)
            except (ValueError, SyntaxError):
                # Se falhar na conversão, trate como uma lista com um único item
                tables_from_schema_linking = [tables_from_schema_linking]
        
        # Se ainda for uma string depois da tentativa de conversão, ou se for uma lista vazia
        if not tables_from_schema_linking:
            tables_from_schema_linking = []

        # normalizing tables names for lowercase
        tables_ground_truth = [table.replace("MONDIAL_", "").lower() for table in tables_ground_truth]
        tables_from_schema_linking = [table.replace("MONDIAL_", "").lower() for table in tables_from_schema_linking]

        for table in tables_ground_truth:
            if table in tables_from_schema_linking:
                TP += 1
            else:
                FN += 1

        print(
            f"[Schema Linking Recall calculus]\n Ground Truths: {tables_ground_truth}\n Tables from Schema Linking: {tables_from_schema_linking}\n Recall = True Positives / (False Negatives + True Positives) = {TP} / ({FN} + {TP}) = {TP / (FN + TP)}.")

        return TP / (FN + TP)

    def messages_to_string_list(self, messages):
        string = ""
        for msg in messages:
            # Obtem o nome da classe (ex: "HumanMessage", "AIMessage", "ToolMessage")
            msg_type = msg.__class__.__name__

            if msg_type == "AIMessage" and msg.content == "":
                continue
            else:
                # Cria uma string combinando o tipo e o conteúdo da mensagem
                string += f"{msg_type}: {msg.content}" + "\n"

        return string


    def compare_intentions(self, function_input, intention, chat_history):
        # Check if the function input is aligned with the intentions
        prompt = prompts.AI_JUDGE_INTENTION_PROMPT.format(
            function_input=function_input,
            ground_truth=intention,
            chat_history=self.messages_to_string_list(chat_history)
        )

        print(
            f"[AI as JUDGE] Comparing intention between queries '{function_input}' and '{intention}' using AI as Judge method.")
        input = HumanMessage(content=prompt)

        chain = self.llm | StrOutputParser()

        result = chain.invoke([input])
        print(f"[AI as JUDGE] Result: {result}.")

        return "true" in result.lower()

    def extract_outer_json(self, text):
        """
        Utility function to avoid cases when llm answers like:
        "No results found.
        {
            "input": "Query.",
            "schema_linking": [],
            "answer": "No results found.",
            "sql": ""
        }"
        In benchmark it was a case of hallucination, this function mitigates this problem.
        """
        start_index = None
        brace_count = 0
        for i, char in enumerate(text):
            if char == '{':
                if start_index is None:
                    start_index = i  # marca o início do JSON
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_index is not None:
                    # Encontrou o fechamento do objeto externo
                    end_index = i
                    return text[start_index:end_index + 1]
        return None

    def need_feedback(self, chat_history):
        prompt = prompts.FEEDBACK_CLASSIFICATION_PROMPT.format(chat_history=self.convert_story_to_string(chat_history))

        print(f"[AI as JUDGE] Judging if a feedback is needed for the last message in chat history.")
        msg = HumanMessage(content=prompt)

        chain = self.llm | StrOutputParser()

        result = chain.invoke([msg])
        print(f"[AI as JUDGE] Result: {result}.")

        return result.strip().lower() == "true"

    def convert_story_to_string(self, chat_history):
        return "\n".join([msg.content for msg in chat_history])

    def append_turn_evaluation(self, state: UserState, turn_eval: dict) -> None:
        """
        Agrupa o turno na interação atual.
        Se já existir uma interação com o interaction_id atual, adiciona o turno (com turn_id relativo);
        caso contrário, cria uma nova interação com as métricas coletadas.
        """
        current_interaction_id = state["interactions_counting"]
        found = None
        for interaction in state["experiment_eval"]:
            if interaction["interaction_id"] == current_interaction_id:
                found = interaction
                break
                
        if found:
            turn_eval["turn_id"] = len(found["turns"]) + 1
            found["turns"].append(turn_eval)
            
            # Atualizar métricas da interação se necessário
            metrics = state["interaction_metrics"].get(current_interaction_id, {})
            found["total_retries_needed"] = metrics.get("total_retries_needed", 0)
            found["success_without_retry"] = metrics.get("success_without_retry", True)
            
            # Se a interação foi finalizada, calcular o tempo total
            if metrics.get("end_time"):
                found["execution_time"] = metrics.get("end_time") - metrics.get("start_time", 0)
        else:
            turn_eval["turn_id"] = 1
            
            # Obter métricas da interação atual
            metrics = state["interaction_metrics"].get(current_interaction_id, {})
            
            new_interaction = {
                "interaction_id": current_interaction_id,
                "original_intent": metrics.get("original_intent", "Unknown"),
                "total_retries_needed": metrics.get("total_retries_needed", 0),
                "success_without_retry": metrics.get("success_without_retry", True),
                "turns": [turn_eval]
            }
            
            # Se a interação foi finalizada, incluir o tempo de execução
            if metrics.get("end_time"):
                new_interaction["execution_time"] = metrics.get("end_time") - metrics.get("start_time", 0)
            
            state["experiment_eval"].append(new_interaction)

    def text_to_sql_agent(self, nl_query: str, memory_config: dict) -> str:
        """
        This function calls a text-to-sql agent that use a natural language question (nl_query) and process it to a SQL query. The agent will return the SQL query executed and some observations about it.
        Args:
            nl_query (str): Natural language question that will be inputed to agent.
            memory_config (dict): An object with agent memory configuration.
        """

        messages = [HumanMessage(content=nl_query)]
        return self.AGENT.invoke({"messages": messages}, memory_config)


