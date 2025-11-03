AI_JUDGE_INTENTION_PROMPT = """
You are an AI judge that decides if the input to a text to SQL tool is contextual related to the ground truth.

### Example:
---
# Example 1:
## Chat History:
HumanMessage: What is Cuba's Capital?
AIMessage: Capital of cuba is La Habana.
HumanMessage: What is Japan's Capital?
AIMessage: Capital of Japan is Tokyo.

## last user input:
What are the elevation of Japan and Cuba's capitals?

## ground truth:
Following my question about capitals, I want to know the elevation of that Cuba and Japan's capitals.

## Your Answer:
True

## Explaining (why you answered True, to you know):
The last user input is related to the ground truth, because the user is asking for the elevation of the capitals of Cuba and Japan.
---

# Example 2:
## Chat History:
HumanMessage: Get geographical details (country and province) for mountain Kanlaon.
AIMessage: The mountain Kanlaon is located in the Philippines, specifically in the provinces of Central Visayas and Western Visayas.

## last user input:
Great, now can you provide its elevation and what type of mountain it is?

## ground truth:
Retrieve the elevation and the type for mountain Kanlaon.

## Your Answer:
False

## Explaining (why you answered False, to you know):
The last user input is not related to the ground truth, because the user is asking for the elevation and type of the mountain but not being specific about which mountain. This will result in a feedback request.
---

Basic rules:
- Is the last user input related to the ground truth? So True.
- The last user input is included in the ground truth? So True.
- You need to use all global context to answer. Sometimes the user last input is explicit about what they want, but sometimes it is not. But always you can use the chat history to infer if the user intention is related to the ground truth.
- You just say False if the input and ground truth are completely different.
- If the last user input is not aligned with the ground truth, you should say False.

Chat history:
{chat_history}

Last user input:
{function_input}

Ground truth:
{ground_truth} 

Your answer (True or False, DON'T EXPLAIN):
"""

USER_INTERACTION_PROMPT = """
You are an user of a dialogue system that have a text to SQL tool, you are following some steps to use it.

You will receive a chat_history with some messages, if the last message is the system asking some thing, use the actual turn above to answer it.

- If model is asking to desambiguate a question, you should answer with a natural language question that expresses you query in a more clear way, based on chat history and your real intentions that will be given.
- If llm returns a result that don't looks relevante to last question user did, you may argue that it is not a good answer and ask for a better one.
- If the llm message is a error on SQL execution, try to understand the error and formulate you query in a way that it will not happen again.

Just follow like example above:

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