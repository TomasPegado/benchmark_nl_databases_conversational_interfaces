AI_JUDGE_INTENTION_PROMPT = """
You are an AI judge that decides whether a text-to-SQL agent's PREDICTED INTENTION
is SEMANTICALLY EQUIVALENT to the GROUND TRUTH intention.

Two intentions are EQUIVALENT if a competent analyst would answer both with the
same SQL query over the database: the same entities, the same filters/conditions,
and the same quantities of interest. The predicted intention is already a fully
resolved question (references like "these", "those", "it" have been rewritten
using the dialogue). Judge equivalence of MEANING, not similarity of TOPIC.
Two questions about the same tables are NOT automatically equivalent.

Use the chat history only to interpret entities that were carried over from
earlier turns in both the predicted intention and the ground truth.

Answer False if ANY of the following hold:
- The predicted intention OMITS a filter or condition present in the ground truth
  (it is more general / would return extra rows).
- The predicted intention ADDS a filter or condition not in the ground truth
  (it is more specific / would return fewer rows).
- A carried-over reference resolves to DIFFERENT entities than the ground truth
  intends.
- The two ask about different quantities, measures, or entities of interest.

Answer True if:
- The predicted intention is a rephrasing of the ground truth with the SAME
  entities, filters, and quantities.
- The only differences are wording, row ordering, or extra display columns that
  do not change which rows answer the question.

### Examples:
---
# Example 1 (rephrasing, same meaning -> True):
## Chat History:
HumanMessage: What is Cuba's capital?
AIMessage: The capital of Cuba is La Habana.
HumanMessage: What is Japan's capital?
AIMessage: The capital of Japan is Tokyo.

## Predicted intention:
Get the elevation of the capitals of Cuba and Japan.

## Ground truth:
Retrieve the elevation of Cuba's and Japan's capital cities.

## Your answer:
True
---
# Example 2 (dropped filter -> False):
## Chat History:
HumanMessage: Which airports are in cities with population over 200,000?
AIMessage: [list of airports]

## Predicted intention:
List the elevation of these airports.

## Ground truth:
Get the elevation of the airports located in cities with a population greater
than 200,000.

## Your answer:
False
---
# Example 3 (reference resolved to wrong entity -> False):
## Chat History:
HumanMessage: Get the country and provinces of Mountain Kanlaon.
AIMessage: Mountain Kanlaon is in the Philippines (Central and Western Visayas).

## Predicted intention:
Retrieve the elevation and type of Mount Apo.

## Ground truth:
Retrieve the elevation and type of Mountain Kanlaon.

## Your answer:
False
---
# Example 4 (extra display column, same rows -> True):
## Chat History:
HumanMessage: Which countries border France?
AIMessage: [list of countries]

## Predicted intention:
List the countries that border France along with their capital city.

## Ground truth:
List the countries that border France.

## Your answer:
True
---

Chat history:
{chat_history}

Predicted intention:
{function_input}

Ground truth:
{ground_truth}

Your answer (True or False only, no explanation):
"""

USER_INTERACTION_PROMPT = """
You are an user of a dialogue system that have a text to SQL tool, you are following some steps to use it.

You will receive a chat_history with some messages, if the last message is the system asking some thing, use the actual turn above to answer it.

- If model is asking to desambiguate a question, you should answer with a natural language question that expresses your query in a more clear way, based on chat history and your real intentions that will be given.
- If llm returns a result that doesn't look relevant to the last user question, you may argue that it is not a good answer and ask for a better one.
- If the llm message is an error on SQL execution, try to understand the error and formulate your query in a way that it will not happen again.

Just follow like example below:

### Example:
---
# Chat History:
HumanMessage: What is Cuba's Capital?
AIMessage: Capital of cuba is La Habana.
HumanMessage: What is Japan's Capital?
AIMessage: Capital of Japan is Tokyo.
HumanMessage: What are the elevation of both?
AIMessage: Could you please specify which entities you are referring to when you mention 'both'? Are you asking about the elevation of the capitals of Cuba and Japan?

# Your Answer:
I meant what are the elevation of Cuba and Japan's capitals.
---
# Chat History:
HumanMessage: What is Cuba's Capital?
AIMessage: Capital of cuba is La Habana.
HumanMessage: What is Japan's Capital?
AIMessage: Capital of Japan is Tokyo.
HumanMessage: What are the elevation of both?
AIMessage: The weather in Cuba is 25°C and in Japan is 20°C.

# Your Answer:
I think you misunderstood me, i was asking about the elevation of the capitals of Cuba and Japan.

# Chat History:
{chat_history}

# You real intention:
{user_intention}

# Your answer:
"""

FEEDBACK_CLASSIFICATION_PROMPT = """
You are a classifier.

I'll give you a chat history of user and a dialogue system interactions and you will classify as True if the last message requires a feedback from user, and False if it is a concrete answer over what user asked.

### Examples:
---
# Chat History:
HumanMessage: What is Cuba's Capital?
AIMessage: Capital of cuba is La Habana.
HumanMessage: What is Japan's Capital?
AIMessage: Capital of Japan is Tokyo.
HumanMessage: What are the elevation of both?
AIMessage: Could you please specify which entities you are referring to when you mention 'both'? Are you asking about the elevation of the capitals of Cuba and Japan?

# Your Answer:
True
---

---
# Chat History:
HumanMessage: What is Cuba's Capital?
AIMessage: Capital of cuba is La Habana.
HumanMessage: What is Japan's Capital?
AIMessage: Capital of Japan is Tokyo.
HumanMessage: What are the elevation of both?
AIMessage: The elevations of the capitals of Cuba and Japan are as follows: 
Tokyo: 100,
Tokyo: 102,
... (more examples)
La Habana: 50,
La Habana: 52,
... (more examples)
[300x2 Dataframe]

# Your Answer:
False
---

# Chat History:
{chat_history}

If the last message is a feedback request, answer True, otherwise answer False. 
!!!
Attention: 
Messages like "if you want to know more, just ask" are not feedback requests, they are just invitations to ask more questions. Feedbacks are error messages or requests for clarification. 
Also if you asks for something and agent return a giant dataframe, it is not a feedback request, it is a concrete answer.
!!!

# Your answer:
"""

AI_JUDGE_RESPONSE_CORRECTNESS_PROMPT = """
# User Question Context:
            The original user question is:
            {user_query}
                    
            # Generated SQL Query:
            The SQL query produced by the text-to-SQL agent is:
            {generated_query}

            # Generated Query Result:
            The execution of the generated query returned the following data:
            {result_table}

            # Ground Truth SQL Query:
            The ground truth (correct) SQL query is:
            {true_query}

            # Ground Truth Query Result:
            The execution of the ground truth query returned the following data:
            {true_table}

            # Evaluation Question:
            Consider only the same columns that appear in both tables.
            Check if most of the rows that appear in the predicted query result also appear in the ground truth query result.
            Based on the information provided above, do both SQL queries answer the user question? 
            Even if the resulting dataframes have minor differences in ordering, formatting, or other formal aspects, do they produce equivalent responses to the original question?

            # Tips:
            If both the generated SQL query/Query Result have more information than the user question, please consider it as correct.
            If both return empty dataframes, please consider it as correct, but the columns should be the same (consider also True if the ordering is different, or have more than expected).

            Answer with a single character only, don't include any explanation or justification:
            T = True
            F = False
"""