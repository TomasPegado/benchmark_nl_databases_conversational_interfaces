# Ground Truth SQL Query Classification Analysis 

# 1\. Summary

All dialogues were generated with GPT-5.6, with improvements on the dialogue-generation prompts.

An LLM-based correctness analysis of the ground truth SQL queries was carried out using state-of-the-art LLMs, using the prompt in Section 2 (as of July 2026):

* Claude Sonnet 5 Medium on the Anthropic MacOS App   
* K2.6 Standard High on the Kimi MacOS App   
* Gemini 3.6 Thinking on the Gemini MacOS App

Section 3 contains the detailed results and additionally includes the evaluations of GPT-5.5 Instant, which were discarded, however, since this LLM is of the same family as GPT-5.6 Sol, used to generate the dialogues. The following tables summarize the results.

|  |  | Sonnet 5 Medium |  |  | K2.6 Instant High |  |  | Gemini 3.6 Thinking |  |  |
| ----- | :---- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
|  |  | **Simple** | **Medium** | **Simple** | **Medium** | **Simple** | **Complex** | **Simple** | **Medium** | **Complex** |
| Mondial | 500 | 44 | 336 | 120 | 44 | 336 | 120 | 44 | 324 | 132 |
| Formula 1 | 500 | 37 | 257 | 206 | 37 | 257 | 206 | 37 | 307 | 156 |
| Hist. Baseball | 110 | 10 | 72 | 28 | 10 | 73 | 27 | 10 | 73 | 24 |

|  |  | Consensus (Count) |  |  | Consensus (%) |  |  |
| ----- | ----- | :---: | :---: | :---: | :---: | :---: | :---: |
|  |  | **Simple** | **Medium** | **Complex** | **Simple** | **Medium** | **Complex** |
| Mondial | 500 | 44 | 336 | 120 | **8,80%** | **67,20%** | **24,00%** |
| Formula 1 | 500 | 37 | 257 | 206 | **7,40%** | **51,40%** | **41,20%** |
| Hist. Baseball | 110 | 10 | 72 | 28 | **9,09%** | **65,45%** | **25,45%** |

Note: the consensus was computed by analyzing the classification of each SQL query, as judged by each LLM: if the query was classified as simple (medium or complex) by at least two LLMs, the consensus was that it was simple (medium or complex). 

# 2\. Prompt

You are an expert in conversational text-to-SQL agents.

Your task is to inspect the list of dialogues passed as an attachment and classify each ground-truth SQL query according to the following criteria:

- Simple: The SQL query has at most one join, no subqueries, and no aggregations.

- Medium: The SQL query has at least one subquery or at least two joins, and no aggregations.

- Complex: The SQL is not simple or medium.


The list of dialogues is a json file. Each dialogue has the following structure:

- experiment_id:	  The dialogue id.

- total_expected_interactions:	  The total number of interactions in the dialogue.

- Interactions:	  The list of interactions in the dialogue, numbered 0, 1, 2, …, n.

- i:	  The interaction number.

- interaction_id:	  The interaction id.

- speaker:	"User".

- utterance:	  A natural language user question, which can be partially formulated.

- Intention:   The intention of the user question, which is a natural language sentence fully defining the user question.

- ground_truths:	

  - tables_from_schema_linking:	   The list of tables used in the ground-truth SQL query.

  - golden_sql:	The ground-truth SQL query responding the user question.

The utterance key defines the user turn and the golden_sql key defines the system turn, expressed as an SQL query.

You should output the number of queries in each classification.

# 3\. Results

## 3.1 Mondial (50x10)

### 3.1.1 Mondial – GPT-5.5 Instant

https://chatgpt.com/share/6a733e34-d960-83e9-8eed-8100f2c07178

| Classification | Number of queries |
| ----- | ----- |
| Simple | **42** |
| Medium | **374** |
| Complex | **84** |
| **Total** | **500** |

### 3.1.2 Mondial – Sonnet 5 Medium

https://claude.ai/share/23194cc2-8b87-4bd7-985b-ff8a47266e07  
Based on the analysis of all 500 ground-truth SQL queries across the 50 dialogues in the dataset, here is the classification breakdown:

| Classification | Count |
| ----- | ----- |
| **Simple** (≤1 join, no subqueries, no aggregations) | **44** |
| **Medium** (≥1 subquery or ≥2 joins, no aggregations) | **336** |
| **Complex** (everything else — typically involves aggregations, e.g. COUNT/SUM/AVG/MIN/MAX or GROUP BY) | **120** |
| **Total** | **500** |

**Methodology notes:**

* **Joins** were counted from explicit JOIN keywords plus implicit joins detected via comma-separated tables in the FROM clause.  
* **Subqueries** were detected by counting occurrences of SELECT — more than one indicates nested queries (very common here, often used for maintaining conversational context across turns via WHERE (...) IN (SELECT ...) patterns).  
* **Aggregations** were detected via aggregate functions (COUNT, SUM, AVG, MIN, MAX) or GROUP BY clauses — presence of these always pushed a query into **Complex**, regardless of join/subquery count, per your rule that Complex \= "not Simple or Medium."

A key pattern in this dataset: since it's a *conversational* text-to-SQL benchmark, later turns in a dialogue frequently reference prior turns' results via nested subqueries (to preserve context), which is why **Medium** dominates — the majority of follow-up questions inherit a subquery from the conversation history even when the new ask itself is simple filtering or projection.

### 3.1.3 Mondial – K2.6 Instant High

https://www.kimi.com/share/19fd2567-f0b2-8853-8000-000068fe54f6

Based on the classification criteria applied to all 500 ground-truth SQL queries in the dataset (50 dialogues × 10 interactions), the counts are:

| Classification | Count |
| :---- | :---- |
| **\*\*Simple\*\*** | \*\*44\*\* |
| **\*\*Medium\*\*** | \*\*336\*\* |
| **\*\*Complex\*\*** | \*\*120\*\* |
| **\*\*Total\*\*** | \*\*500\*\* |

\*\*Summary:\*\*  
\- \*\*Simple\*\* queries (≤1 join, no subqueries, no aggregations) appear almost exclusively in the first turn of each dialogue.  
\- \*\*Medium\*\* queries (≥1 subquery or ≥2 joins, no aggregations) dominate the dataset because the multi-turn dialogues heavily rely on nested \`IN (SELECT ...)\` subqueries to carry forward context from previous turns.  
\- \*\*Complex\*\* queries (anything with aggregations such as \`COUNT\`, \`SUM\`, \`GROUP BY\`, or \`HAVING\`) are concentrated in later turns where the user asks for summaries, counts, or comparative statistics.

### 3.1.4 Mondial – Gemini 3.6 Thinking

*(Combined results of several executions due to limitation of the tool)*

***Experiments 1-5***

| Classification | Total Queries |
| :---- | :---- |
| **Simple** | 4 |
| **Medium** | 32 |
| **Complex** | 14 |

**Detailed Breakdown by Experiment**

* **Experiment 1** (10 total queries)  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (9):** Interactions 2–10  
      
  * **Complex (0)**  
      
      
* **Experiment 2** (10 total queries)  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (7):** Interactions 2–8  
      
  * **Complex (2):** Interactions 9–10 (due to COUNT, SUM, and GROUP BY aggregations)  
      
* **Experiment 3** (10 total queries)  
  

  * **Simple (0)**  
      
      
  * **Medium (0)**  
      
      
  * **Complex (10):** Interactions 1–10 (all include COUNT and/or GROUP BY aggregations within CTEs or main queries)  
      
* **Experiment 4** (10 total queries)  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (8):** Interactions 2–9  
      
  * **Complex (1):** Interaction 10 (due to COUNT and GROUP BY)  
      
* **Experiment 5** (10 total queries)  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (8):** Interactions 2–9  
      
  * **Complex (1):** Interaction 10 (due to COUNT and GROUP BY)

***Experiments 6-10***  
Based on the classification criteria, here is the distribution of the 60 ground-truth SQL queries across all dialogues:

* **Simple**: 5  
* **Medium**: 34  
* **Complex**: 21

### Breakdown by Experiment

| Experiment ID | Simple | Medium | Complex | Total Queries |
| ----- | ----- | ----- | ----- | ----- |
| **Experiment 6** | 1 | 7 | 2 | 10 |
| **Experiment 7** | 1 | 2 | 7 | 10 |
| **Experiment 8** | 1 | 1 | 8 | 10 |
| **Experiment 9** | 1 | 9 | 0 | 10 |
| **Experiment 10** | 0 | 6 | 4 | 10 |
| **Experiment 11** | 1 | 9 | 0 | 10 |
| **Total** | **5** | **34** | **21** | **60** |

***Experiments 11-15***

Based on the classification criteria provided, the 60 ground-truth SQL queries across the 6 dialogue experiments are classified as follows:

| Complexity Level | Criteria | Query Count |
| ----- | ----- | ----- |
| **Simple** | \\le 1 join, no subqueries, no aggregations | **5** |
| **Medium** | \\ge 1 subquery OR \\ge 2 joins, and no aggregations | **34** |
| **Complex** | Contains aggregations or does not fit Simple/Medium | **21** |

**Experiment-by-Experiment Breakdown**

* **Experiment 6** (10 queries): 1 Simple, 7 Medium, 2 Complex  
* **Experiment 7** (10 queries): 1 Simple, 2 Medium, 7 Complex  
* **Experiment 8** (10 queries): 1 Simple, 1 Medium, 8 Complex  
* **Experiment 9** (10 queries): 1 Simple, 9 Medium, 0 Complex  
* **Experiment 10** (10 queries): 0 Simple, 6 Medium, 4 Complex  
* **Experiment 11** (10 queries): 1 Simple, 9 Medium, 0 Complex

***Experiments 16-20***

The classification of the 50 ground-truth SQL queries across the dataset is as follows:

| Classification | Criteria Summary | Count |
| :---- | :---- | :---- |
| **Simple** | ≤1 Join, no subqueries, no aggregations | **5** |
| **Medium** | ≥1 Subquery OR ≥2 Joins, no aggregations | **29** |
| **Complex** | Contains aggregations (COUNT, GROUP BY, HAVING) or non-medium multi-query logic | **16** |
| **Total** |  | **50** |

**Breakdown by Dialogue (Experiment ID)**

* **Experiment 16**: 1 Simple, 7 Medium, 2 Complex  
    
* **Experiment 17**: 1 Simple, 6 Medium, 3 Complex  
    
* **Experiment 18**: 1 Simple, 3 Medium, 6 Complex  
    
* **Experiment 19**: 1 Simple, 9 Medium, 0 Complex  
    
* **Experiment 20**: 1 Simple, 4 Medium, 5 Complex

***Experiments 21-25***

A total of **50 ground-truth SQL queries** across 5 dialogues (Experiments 21–25, 10 interactions each) were classified according to your criteria:

| Classification | Count (Standard Aggregation) | Count (Aggregate Functions Only) |
| ----- | ----- | ----- |
| **Simple** (\\le 1 JOIN, no subqueries, no aggregations) | **4** | **4** |
| **Medium** (\\ge 1 subquery OR \\ge 2 JOINs, no aggregations) | **36** | **40** |
| **Complex** (All remaining queries, e.g. containing aggregations) | **10** | **6** |

*Note: The standard count includes both aggregate functions (COUNT, SUM, AVG, MAX, MIN) and GROUP BY grouping clauses as aggregations. The secondary column counts only explicit aggregate functions.*  
**Experiment-by-Experiment Breakdown**

* **Experiment 21 (10 queries)**  
  * **Simple (1)**: Interaction 1  
  * **Medium (9)**: Interactions 2, 3, 4, 5, 6, 7, 8, 9, 10  
  * **Complex (0)**  
* **Experiment 22 (10 queries)**  
  * **Simple (1)**: Interaction 1  
  * **Medium (9)**: Interactions 2, 3, 4, 5, 6, 7, 8, 9, 10  
  * **Complex (0)**  
* **Experiment 23 (10 queries)**  
  * **Simple (1)**: Interaction 1  
  * **Medium (7)**: Interactions 2, 3, 4, 5, 6, 7, 8  
  * **Complex (2)**: Interactions 9, 10 (contain COUNT and GROUP BY)  
* **Experiment 24 (10 queries)**  
  * **Simple (0)**  
  * **Medium (5 or 9\)**: Interactions 1, 2, 3, 4, 9 (and 6, 7, 10 if GROUP BY without aggregate functions is categorized under Medium)  
  * **Complex (5 or 1\)**: Interactions 5, 8 (contain SUM, AVG, MAX) \+ Interactions 6, 7, 9, 10 (contain GROUP BY subquery clauses)  
* **Experiment 25 (10 queries)**  
  * **Simple (1)**: Interaction 1  
  * **Medium (7)**: Interactions 2, 4, 5, 6, 7, 8, 9  
  * **Complex (2)**: Interactions 3, 10 (contain COUNT and GROUP BY)

***Experiments 26-30***

**Summary Classification**

* **Simple**: 4 queries  
    
* **Medium**: 32 queries  
    
* **Complex**: 14 queries


Total queries evaluated: **50**

### Classification Breakdown by Experiment

| Experiment ID JSON | Simple JSON | Medium JSON | Complex JSON | Total Queries JSON |
| :---- | :---- | :---- | :---- | :---- |
| **Experiment 26**  | 1 | 7 | 2 | 10 |
| **Experiment 27**  | 0 | 3 | 7 | 10 |
| **Experiment 28**  | 1 | 9 | 0 | 10 |
| **Experiment 29**  | 1 | 7 | 2 | 10 |
| **Experiment 30**  | 1 | 6 | 3 | 10 |
| **Total** | **4** | **32** | **14** | **50** |

### Per-Interaction Query Classification

* **Experiment 26**  
    
  

  * Interaction 1: **Simple** (1 join, 0 subqueries, 0 aggregations)  
      
  * Interaction 2: **Medium** (3 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 3: **Medium** (4 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 4: **Medium** (4 joins, 2 subqueries, 0 aggregations)  
      
  * Interaction 5: **Medium** (7 joins, 3 subqueries, 0 aggregations)  
      
  * Interaction 6: **Medium** (10 joins, 4 subqueries, 0 aggregations)  
      
  * Interaction 7: **Medium** (11 joins, 4 subqueries, 0 aggregations)  
      
  * Interaction 8: **Medium** (11 joins, 3 subqueries, 0 aggregations)  
      
  * Interaction 9: **Complex** (Aggregations: COUNT, GROUP BY)  
      
  * Interaction 10: **Complex** (Aggregations: COUNT, GROUP BY)  
      
* **Experiment 27**  
    
  

  * Interaction 1: **Medium** (2 joins, 0 subqueries, 0 aggregations)  
      
  * Interaction 2: **Medium** (2 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 3: **Medium** (2 joins, 2 subqueries, 0 aggregations)  
      
  * Interaction 4: **Complex** (Aggregations: AVG, MAX, GROUP BY)  
      
  * Interaction 5: **Complex** (Aggregations: COUNT, SUM, GROUP BY)  
      
  * Interaction 6: **Complex** (Aggregations: COUNT, SUM, GROUP BY)  
      
  * Interaction 7: **Complex** (Aggregations: GROUP BY)  
      
  * Interaction 8: **Complex** (Aggregations: GROUP BY)  
      
  * Interaction 9: **Complex** (Aggregations: GROUP BY)  
      
  * Interaction 10: **Complex** (Aggregations: GROUP BY)  
      
* **Experiment 28**  
    
  

  * Interaction 1: **Simple** (0 joins, 0 subqueries, 0 aggregations)  
      
  * Interaction 2: **Medium** (1 join, 1 subquery, 0 aggregations)  
      
  * Interaction 3: **Medium** (1 join, 1 subquery, 0 aggregations)  
      
  * Interaction 4: **Medium** (2 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 5: **Medium** (2 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 6: **Medium** (3 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 7: **Medium** (2 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 8: **Medium** (4 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 9: **Medium** (3 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 10: **Medium** (4 joins, 1 subquery, 0 aggregations)  
      
* **Experiment 29**  
    
  

  * Interaction 1: **Simple** (0 joins, 0 subqueries, 0 aggregations)  
      
  * Interaction 2: **Medium** (0 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 3: **Complex** (Aggregations: COUNT, GROUP BY)  
      
  * Interaction 4: **Medium** (1 join, 3 subqueries, 0 aggregations)  
      
  * Interaction 5: **Medium** (2 joins, 4 subqueries, 0 aggregations)  
      
  * Interaction 6: **Complex** (Aggregations: AVG, GROUP BY)  
      
  * Interaction 7: **Medium** (5 joins, 6 subqueries, 0 aggregations)  
      
  * Interaction 8: **Medium** (8 joins, 7 subqueries, 0 aggregations)  
      
  * Interaction 9: **Medium** (9 joins, 8 subqueries, 0 aggregations)  
      
  * Interaction 10: **Medium** (11 joins, 9 subqueries, 0 aggregations)  
      
* **Experiment 30**  
    
  

  * Interaction 1: **Simple** (1 join, 0 subqueries, 0 aggregations)  
      
  * Interaction 2: **Medium** (2 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 3: **Medium** (3 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 4: **Medium** (4 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 5: **Medium** (3 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 6: **Complex** (Aggregations: AVG, GROUP BY)  
      
  * Interaction 7: **Medium** (3 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 8: **Medium** (4 joins, 1 subquery, 0 aggregations)  
      
  * Interaction 9: **Complex** (Aggregations: MAX, GROUP BY)  
      
  * Interaction 10: **Complex** (Aggregations: COUNT, GROUP BY)

***Experiments 31-35***

Based on the defined classification criteria across the 50 queries (10 interactions per experiment across 5 experiments), the query counts are:

* **Simple**: 5  
* **Medium**: 38  
* **Complex**: 7

### Classification Breakdown by Experiment

| Experiment ID | Simple | Medium | Complex | Total |
| ----- | ----- | ----- | ----- | ----- |
| **Experiment 31** | 1 (Int 1\) | 8 (Int 2–6, 8–10) | 1 (Int 7\) | 10 |
| **Experiment 32** | 1 (Int 1\) | 3 (Int 2–3, 8\) | 6 (Int 4–7, 9–10) | 10 |
| **Experiment 33** | 1 (Int 1\) | 9 (Int 2–10) | 0 | 10 |
| **Experiment 34** | 1 (Int 1\) | 9 (Int 2–10) | 0 | 10 |
| **Experiment 35** | 1 (Int 1\) | 9 (Int 2–10) | 0 | 10 |
| **Total** | **5** | **38** | **7** | **50** |

***Experiments 36-40***

Based on the evaluation criteria, the dataset contains 50 ground-truth SQL queries classified as follows:

* **Simple**: 5 queries  
    
* **Medium**: 36 queries  
    
* **Complex**: 9 queries


| Classification | Total Queries | Criteria Description JSON |
| :---- | :---- | :---- |
| **Simple** | 5 | At most 1 join, 0 subqueries, and 0 aggregations  |
| **Medium** | 36 | At least 1 subquery OR at least 2 joins, and 0 aggregations  |
| **Complex** | 9 | Contains aggregations (COUNT, SUM, etc.)  |

**Detailed Interaction Breakdown**

* **Experiment 36**  
    
  

  * **Simple** (1): Interaction 1  
      
  * **Medium** (8): Interactions 2, 3, 4, 5, 6, 7, 8, 10  
      
  * **Complex** (1): Interaction 9 (contains COUNT)  
      
* **Experiment 37**  
    
  

  * **Simple** (1): Interaction 1  
      
  * **Medium** (2): Interactions 2, 3  
      
  * **Complex** (7): Interactions 4, 5, 6, 7, 8, 9, 10 (contain COUNT aggregations)  
      
* **Experiment 38**  
    
  

  * **Simple** (1): Interaction 1  
      
  * **Medium** (9): Interactions 2, 3, 4, 5, 6, 7, 8, 9, 10  
      
  * **Complex** (0): None  
      
* **Experiment 39**  
    
  

  * **Simple** (1): Interaction 1  
      
  * **Medium** (8): Interactions 2, 3, 5, 6, 7, 8, 9, 10  
      
  * **Complex** (1): Interaction 4 (contains SUM)  
      
* **Experiment 40**  
    
  

  * **Simple** (1): Interaction 1  
      
  * **Medium** (9): Interactions 2, 3, 4, 5, 6, 7, 8, 9, 10  
      
  * **Complex** (0): None

***Experiments 41-45***

Across the 45 ground-truth SQL queries provided in the dataset, **5** are classified as Simple, **32** as Medium, and **8** as Complex.  
**Summary Totals**

* **Simple (5 queries)**: Queries featuring at most one join, no subqueries, and no aggregate functions (Interaction 1 in each dialogue).  
* **Medium (32 queries)**: Queries utilizing subqueries (including Common Table Expressions / CTEs) or multiple joins without any aggregate functions (primarily multi-turn context propagation interactions).  
* **Complex (8 queries)**: Queries that perform statistical aggregations (e.g., COUNT(\*), AVG(), MAX()) or include GROUP BY / HAVING clauses.

**Detailed Breakdown by Experiment**

* **Experiment 41 (10 queries)**:  
  * Simple: 1 (Interaction 1\)  
  * Medium: 8 (Interactions 2–9)  
  * Complex: 1 (Interaction 10 — uses COUNT(\*))  
* **Experiment 42 (10 queries)**:  
  * Simple: 1 (Interaction 1\)  
  * Medium: 5 (Interactions 2–6)  
  * Complex: 4 (Interactions 7–10 — use COUNT(\*) with GROUP BY or HAVING)  
* **Experiment 43 (10 queries)**:  
  * Simple: 1 (Interaction 1\)  
  * Medium: 8 (Interactions 2–9)  
  * Complex: 1 (Interaction 10 — uses COUNT(\*) and MAX())  
* **Experiment 44 (10 queries)**:  
  * Simple: 1 (Interaction 1\)  
  * Medium: 7 (Interactions 2–8)  
  * Complex: 2 (Interactions 9–10 — use AVG())  
* **Experiment 45 (5 queries)**:  
  * Simple: 1 (Interaction 1\)  
  * Medium: 4 (Interactions 2–5)  
  * Complex: 0

***Experiments 45-50***

| Category | Number of Queries |
| :---- | :---- |
| **Simple** | 4 |
| **Medium** | 36 |
| **Complex** | 10 |
| **Total** | **50** |

### Detailed Classification Breakdown

**Experiment 46**

* **Interaction 1:** Simple (1 join, no subqueries, no aggregations)  
    
* **Interaction 2:** Medium (1 join, 1 subquery, no aggregations)  
    
* **Interaction 3:** Medium (1 join, 2 subqueries, no aggregations)  
    
* **Interaction 4:** Medium (3 joins, 3 subqueries, no aggregations)  
    
* **Interaction 5:** Medium (3 joins, 4 subqueries, no aggregations)  
    
* **Interaction 6:** Medium (3 joins, 5 subqueries, no aggregations)  
    
* **Interaction 7:** Medium (3 joins, 6 subqueries, no aggregations)  
    
* **Interaction 8:** Medium (6 joins, CTE / subqueries, no aggregations)  
    
* **Interaction 9:** Medium (7 joins, CTE / subqueries, no aggregations)  
    
* **Interaction 10:** Medium (10 joins, CTE / subqueries, no aggregations)


**Experiment 47**

* **Interaction 1:** Medium (2 joins, no subqueries, no aggregations)  
    
* **Interaction 2:** Medium (2 joins, 1 subquery, no aggregations)  
    
* **Interaction 3:** Medium (2 joins, 2 subqueries, no aggregations)  
    
* **Interaction 4:** Medium (2 joins, 3 subqueries, no aggregations)  
    
* **Interaction 5:** Medium (5 joins, 4 subqueries, no aggregations)  
    
* **Interaction 6:** Medium (5 joins, 5 subqueries, no aggregations)  
    
* **Interaction 7:** Medium (8 joins, 6 subqueries, no aggregations)  
    
* **Interaction 8:** Medium (11 joins, 7 subqueries, no aggregations)  
    
* **Interaction 9:** Medium (14 joins, 8 subqueries, no aggregations)  
    
* **Interaction 10:** Medium (14 joins, 9 subqueries, no aggregations)


**Experiment 48**

* **Interaction 1:** Simple (0 joins, no subqueries, no aggregations)  
    
* **Interaction 2:** Medium (0 joins, 1 subquery, no aggregations)  
    
* **Interaction 3:** Medium (1 join, 2 subqueries, no aggregations)  
    
* **Interaction 4:** Medium (1 join, 3 subqueries, no aggregations)  
    
* **Interaction 5:** Complex (Contains window aggregation COUNT(\*) OVER)  
    
* **Interaction 6:** Medium (1 join, 5 subqueries, no aggregations)  
    
* **Interaction 7:** Medium (3 joins, CTE / subqueries, no aggregations)  
    
* **Interaction 8:** Medium (5 joins, CTE / subqueries, no aggregations)  
    
* **Interaction 9:** Medium (8 joins, CTE / subqueries, no aggregations)  
    
* **Interaction 10:** Medium (12 joins, CTE / subqueries, no aggregations)


**Experiment 49**

* **Interaction 1:** Simple (1 join, no subqueries, no aggregations)  
    
* **Interaction 2:** Medium (3 joins, 1 subquery, no aggregations)  
    
* **Interaction 3:** Medium (4 joins, 1 subquery, no aggregations)  
    
* **Interaction 4:** Medium (5 joins, 1 subquery, no aggregations)  
    
* **Interaction 5:** Medium (6 joins, 1 subquery, no aggregations)  
    
* **Interaction 6:** Medium (6 joins, 1 subquery, no aggregations)  
    
* **Interaction 7:** Complex (Contains COUNT(\*) and GROUP BY)  
    
* **Interaction 8:** Complex (Contains GROUP BY in subquery)  
    
* **Interaction 9:** Complex (Contains GROUP BY in nested subquery)  
    
* **Interaction 10:** Complex (Contains GROUP BY in nested subquery)


**Experiment 50**

* **Interaction 1:** Simple (0 joins, no subqueries, no aggregations)  
    
* **Interaction 2:** Medium (1 join, 1 subquery, no aggregations)  
    
* **Interaction 3:** Medium (2 joins, 2 subqueries, no aggregations)  
    
* **Interaction 4:** Medium (4 joins, 3 subqueries, no aggregations)  
    
* **Interaction 5:** Medium (6 joins, 4 subqueries, no aggregations)  
    
* **Interaction 6:** Complex (Contains COUNT(DISTINCT ...) and GROUP BY)  
    
* **Interaction 7:** Complex (Contains COUNT(DISTINCT ...) and GROUP BY)  
    
* **Interaction 8:** Complex (Contains GROUP BY in subquery)  
    
* **Interaction 9:** Complex (Contains GROUP BY in subquery)  
    
* **Interaction 10:** Complex (Contains GROUP BY in subquery)

## 3.2 Formula 1 (50x10)

### 3.2.1 Formula 1 – GPT-5.5 Instant

https://chatgpt.com/share/6a733e15-1134-83e9-98b6-2b3437ca6a2c

| Classification | Number of queries |
| ----- | ----- |
| Simple | **37** |
| Medium | **339** |
| Complex | **124** |
| **Total** | **500** |

### 3.2.2 Formula 1 – Sonnet 5 Medium

https://claude.ai/share/4033bbbd-d845-4ca1-9588-3f8638ba9826

No implicit comma-joins found — all joins use explicit JOIN keywords, so the counts are reliable. Here are the results:I inspected all 500 ground-truth SQL queries across the 50 dialogues (10 interactions each) in the dataset and classified each one using your rules:

* **Simple**: ≤1 JOIN, no subqueries, no aggregation  
* **Medium**: ≥1 subquery (nested SELECT) or ≥2 JOINs, no aggregation  
* **Complex**: everything else (i.e., contains any aggregation — aggregate functions like COUNT/SUM/AVG/MIN/MAX, GROUP BY, or HAVING)

**Results**

| Classification | Count |
| ----- | ----- |
| **Simple** | 37 |
| **Medium** | 257 |
| **Complex** | 206 |
| **Total** | 500 |

**Methodology notes:**

* I counted explicit JOIN keywords per query (I confirmed there are zero implicit comma-style joins in the FROM clauses — every join in this dataset uses explicit JOIN ... ON syntax).  
* Subqueries were detected by counting nested SELECT statements (more than one SELECT in a query indicates at least one subquery).  
* "Aggregation" was interpreted to include not just aggregate functions (COUNT, SUM, AVG, MIN, MAX) but also GROUP BY and HAVING clauses, since grouping operations are aggregation-family constructs even when no aggregate function is explicitly applied (e.g., a GROUP BY used purely for deduplication still falls under this category).  
* As expected in a multi-turn dialogue dataset, queries tend to grow more complex as each dialogue progresses (later turns build on earlier ones), which explains the relatively small "Simple" bucket relative to "Medium" and "Complex."

If you'd like, I can export a per-query CSV breakdown (dialogue ID, interaction ID, join count, subquery count, aggregation flag, classification) as a downloadable file.

### 3.2.3 Formula 1 – K2.6 Instant High

https://www.kimi.com/share/19fd2616-2622-8b10-8000-0000783347e9

User: You are an expert in conversational text-to-SQL agents.

Your task is to inspect the list of dialogues passed as an attachment and classify each ground-truth SQL query according to the following criteria:

Simple: The SQL query has at most one join, no subqueries, and no aggregations.

Medium: The SQL query has at least one subquery or at least two joins, and no aggregations.

Complex: The SQL is not simple or medium.

The list of dialogues is a json file. Each dialogue has the following structure:

experiment\_id	The dialogue id.  
total\_expected\_interactions	The total number of interactions in the dialogue.  
Interactions	The list of interactions in the dialogue, numbered 0, 1, 2, …, n.  
i	The interaction number.  
interaction\_id	The interaction id.  
speaker	"User".  
utterance	A natural language user question, which can be partially formulated.  
Intention	The intention of the user question, which is a natural language sentence fully defining the user question.  
ground\_truths	  
tables\_from\_schema\_linking	 The list of tables used in the ground-truth SQL query.  
golden\_sql	The ground-truth SQL query responding the user question.

The utterance key defines the user turn and the golden\_sql key defines the system turn, expressed as an SQL query.

You should output the number of queries in each classification.  
Kimi: After analyzing all 500 ground-truth SQL queries in the dataset, here is the classification count:

| Classification | Count |
| :---- | :---- |
| **\*\*Simple\*\*** | \*\*37\*\* |
| **\*\*Medium\*\*** | \*\*257\*\* |
| **\*\*Complex\*\*** | \*\*206\*\* |
| **\*\*Total\*\*** | \*\*500\*\* |

\*\*Summary of findings:\*\*  
\- \*\*Simple\*\* queries (at most one join, no subqueries, no aggregations) are mostly concentrated in the first interaction of each dialogue, where the conversation typically begins with a straightforward request.  
\- \*\*Medium\*\* queries (subqueries or multiple joins, but no aggregations) represent the majority, as most dialogues quickly progress to multi-table joins or nested subqueries to carry context from previous turns.  
\- \*\*Complex\*\* queries (containing aggregations such as \`GROUP BY\`, \`COUNT\`, \`SUM\`, \`AVG\`, \`MIN\`, \`MAX\`, or \`HAVING\`) make up a substantial portion, often appearing in later turns where the user asks for summaries, rankings, or statistical breakdowns over previously filtered result sets.

### 3.2.4 Formula 1 – Gemini 3.6 Thinking

*(Combined results of several executions due to limitation of the tool)*

***Experiments 1-5***

| Complexity | Query Count |
| ----- | ----- |
| **Simple** | 3 |
| **Medium** | 32 |
| **Complex** | 15 |

### Detailed Breakdown by Dialogue

| Dialogue ID | Interaction | Classification | Criteria Matched |
| ----- | ----- | ----- | ----- |
| **Experiment 1** | Interaction 1 | Simple | 0 joins, 0 subqueries, no aggregations |
|  | Interaction 2 | Medium | 1 subquery, 0 joins, no aggregations |
|  | Interaction 3 | Medium | 2 subqueries, 0 joins, no aggregations |
|  | Interaction 4 | Complex | Contains aggregations (COUNT, AVG) |
|  | Interaction 5 | Complex | Contains aggregations (COUNT, MAX) |
|  | Interaction 6 | Medium | 5 subqueries, 1 join, no aggregations |
|  | Interaction 7 | Medium | 6 subqueries, 3 joins, no aggregations |
|  | Interaction 8 | Complex | Contains aggregation (SUM) |
|  | Interaction 9 | Medium | 8 subqueries, 5 joins, no aggregations |
|  | Interaction 10 | Medium | 9 subqueries, 7 joins, no aggregations |
| **Experiment 2** | Interaction 1 | Simple | 1 join, 0 subqueries, no aggregations |
|  | Interaction 2 | Medium | 1 subquery, 1 join, no aggregations |
|  | Interaction 3 | Medium | Subqueries (CTEs), 1 join, no aggregations |
|  | Interaction 4 | Medium | Subqueries (CTEs), 1 join, no aggregations |
|  | Interaction 5 | Medium | Subqueries (CTEs), 3 joins, no aggregations |
|  | Interaction 6 | Medium | Subqueries (CTEs), 5 joins, no aggregations |
|  | Interaction 7 | Medium | Subqueries (CTEs), 5 joins, no aggregations |
|  | Interaction 8 | Medium | Subqueries (CTEs), 7 joins, no aggregations |
|  | Interaction 9 | Medium | Subqueries (CTEs), 7 joins, no aggregations |
|  | Interaction 10 | Complex | Contains aggregations (COUNT, SUM) |
| **Experiment 3** | Interaction 1 | Simple | 1 join, 0 subqueries, no aggregations |
|  | Interaction 2 | Medium | 1 subquery, 1 join, no aggregations |
|  | Interaction 3 | Medium | 2 subqueries, 2 joins, no aggregations |
|  | Interaction 4 | Medium | 3 subqueries, 2 joins, no aggregations |
|  | Interaction 5 | Complex | Contains aggregation (COUNT) |
|  | Interaction 6 | Complex | Contains aggregations (MIN, MAX) |
|  | Interaction 7 | Medium | 5 subqueries, 3 joins, no aggregations |
|  | Interaction 8 | Medium | 6 subqueries, 3 joins, no aggregations |
|  | Interaction 9 | Complex | Contains aggregations (COUNT, MIN) |
|  | Interaction 10 | Medium | 8 subqueries, 4 joins, no aggregations |
| **Experiment 4** | Interaction 1 | Medium | 2 joins, 0 subqueries, no aggregations |
|  | Interaction 2 | Complex | Contains aggregation (COUNT) |
|  | Interaction 3 | Medium | 1 subquery, 2 joins, no aggregations |
|  | Interaction 4 | Medium | 2 subqueries, 2 joins, no aggregations |
|  | Interaction 5 | Complex | Contains aggregation (COUNT) |
|  | Interaction 6 | Medium | 4 subqueries, 2 joins, no aggregations |
|  | Interaction 7 | Medium | 5 subqueries, 2 joins, no aggregations |
|  | Interaction 8 | Medium | 2 subqueries, 4 joins, no aggregations |
|  | Interaction 9 | Complex | Contains aggregation (SUM) |
|  | Interaction 10 | Complex | Contains aggregation (COUNT) |
| **Experiment 5** | Interaction 1 | Complex | Contains aggregation (COUNT) |
|  | Interaction 2 | Medium | 1 subquery, 0 joins, no aggregations |
|  | Interaction 3 | Medium | 2 subqueries, 1 join, no aggregations |
|  | Interaction 4 | Medium | 3 subqueries, 1 join, no aggregations |
|  | Interaction 5 | Medium | 4 subqueries, 1 join, no aggregations |
|  | Interaction 6 | Complex | Contains aggregations (MIN, MAX) |
|  | Interaction 7 | Medium | 6 subqueries, 2 joins, no aggregations |
|  | Interaction 8 | Medium | 7 subqueries, 3 joins, no aggregations |
|  | Interaction 9 | Complex | Contains aggregation (COUNT) |
|  | Interaction 10 | Complex | Contains aggregations (COUNT, AVG) |

***Experiments 6-10***

The ground-truth SQL queries in the dataset are classified into **Simple**, **Medium**, and **Complex** based on join counts, subqueries, and aggregations.

| Complexity Level | Classification Criteria | Query Count |
| :---- | :---- | :---- |
| **Simple** | ≤1 JOIN, 0 subqueries, no aggregations | **4** |
| **Medium** | ≥2 JOINs or ≥1 subquery, no aggregations | **32** |
| **Complex** | Contains aggregations (COUNT, SUM, AVG, MIN, MAX, GROUP BY) | **14** |

**Detailed Breakdown by Dialogue**

* **Experiment 6** (10 queries): 1 Simple, 6 Medium (Interactions 2–4, 6, 7, 10), 3 Complex (Interactions 5, 8, 9\)  
    
* **Experiment 7** (10 queries): 1 Simple, 6 Medium (Interactions 2, 4–8), 3 Complex (Interactions 3, 9, 10\)  
    
* **Experiment 8** (10 queries): 1 Simple, 7 Medium (Interactions 3–9), 2 Complex (Interactions 2, 10\)  
    
* **Experiment 9** (10 queries): 0 Simple, 6 Medium (Interactions 1–6), 4 Complex (Interactions 7–10)  
    
* **Experiment 10** (10 queries): 1 Simple, 7 Medium (Interactions 2–8), 2 Complex (Interactions 9, 10\)

***Experiments 11-15***

Based on the classification criteria (**Simple**: ≤1 join, 0 subqueries, 0 aggregations; **Medium**: ≥1 subquery or ≥2 joins, 0 aggregations; **Complex**: contains aggregations or does not fit Simple/Medium), here is the classification breakdown for the ground-truth SQL queries in the attachment.

### Summary by Classification

| Category | Count (60 Total Queries in Attachment) | Count (50 Unique Queries) |
| :---- | :---- | :---- |
| **Simple** | **3** | **2** |
| **Medium** | **26** | **18** |
| **Complex** | **31** | **30** |

*Note: Experiment 15 appears twice in the provided dataset.*

### Breakdown by Experiment Dialogue

**Experiment 15** *(10 interactions)*

* **Simple (1)**: Interaction 1  
    
* **Medium (8)**: Interactions 2, 3, 4, 5, 6, 7, 8, 9  
    
* **Complex (1)**: Interaction 10


**Experiment 11** *(10 interactions)*

* **Simple (1)**: Interaction 1  
    
* **Medium (3)**: Interactions 2, 3, 4  
    
* **Complex (6)**: Interactions 5, 6, 7, 8, 9, 10


**Experiment 12** *(10 interactions)*

* **Simple (0)**  
    
* **Medium (0)**  
    
* **Complex (10)**: Interactions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10


**Experiment 13** *(10 interactions)*

* **Simple (0)**  
    
* **Medium (0)**  
    
* **Complex (10)**: Interactions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10


**Experiment 14** *(10 interactions)*

* **Simple (0)**  
    
* **Medium (7)**: Interactions 2, 4, 5, 6, 7, 8, 10  
    
* **Complex (3)**: Interactions 1, 3, 9

***Experiments 16-20***

Out of the 50 total ground-truth SQL queries across the 5 dialogues, **3** are classified as Simple, **36** as Medium, and **11** as Complex.

| Classification | Total Queries | Criteria Summary |
| ----- | ----- | ----- |
| **Simple** | **3** | \\le 1 join, no subqueries, and no aggregations |
| **Medium** | **36** | \\ge 1 subquery or \\ge 2 joins, and no aggregations |
| **Complex** | **11** | Contains aggregations or does not meet Simple/Medium criteria |

### Dialogue-by-Dialogue Breakdown

* **Experiment 16 (10 queries)**  
  * **Simple:** 0  
  * **Medium:** 8 (Interactions 1, 2, 3, 4, 6, 8, 9, 10\)  
  * **Complex:** 2 (Interactions 5, 7\)  
* **Experiment 17 (10 queries)**  
  * **Simple:** 1 (Interaction 1\)  
  * **Medium:** 7 (Interactions 2, 3, 4, 5, 6, 9, 10\)  
  * **Complex:** 2 (Interactions 7, 8\)  
* **Experiment 18 (10 queries)**  
  * **Simple:** 0  
  * **Medium:** 7 (Interactions 2, 3, 4, 6, 7, 9, 10\)  
  * **Complex:** 3 (Interactions 1, 5, 8\)  
* **Experiment 19 (10 queries)**  
  * **Simple:** 1 (Interaction 1\)  
  * **Medium:** 7 (Interactions 2, 3, 4, 5, 6, 8, 10\)  
  * **Complex:** 2 (Interactions 7, 9\)  
* **Experiment 20 (10 queries)**  
  * **Simple:** 1 (Interaction 1\)  
  * **Medium:** 7 (Interactions 2, 3, 4, 5, 8, 9, 10\)  
  * **Complex:** 2 (Interactions 6, 7\)

***Experiments 21-25***

Across the 50 queries evaluated in the dataset, **3** are classified as Simple, **24** as Medium, and **23** as Complex.

| Category | Query Count | Criteria Summary |
| ----- | ----- | ----- |
| **Simple** | 3 | \\le 1 join, no subqueries, no aggregations |
| **Medium** | 24 | \\ge 1 subquery or \\ge 2 joins, no aggregations |
| **Complex** | 23 | Contains aggregations or falls outside Simple/Medium rules |
| **Total** | **50** | All evaluated ground-truth queries |

**Experiment Breakdown**

* **Experiment 21:** Simple: 0 | Medium: 6 | Complex: 4  
* **Experiment 22:** Simple: 1 | Medium: 6 | Complex: 3  
* **Experiment 23:** Simple: 1 | Medium: 4 | Complex: 5  
* **Experiment 24:** Simple: 1 | Medium: 8 | Complex: 1  
* **Experiment 25:** Simple: 0 | Medium: 0 | Complex: 10

***Experiments 26-30***

| Classification | Query Count |
| ----- | ----- |
| **Simple** | **4** |
| **Medium** | **30** |
| **Complex** | **16** |

**Detailed Breakdown by Experiment**

* **Simple (4 total)**  
  * **Exp 27**: Interaction 1  
  * **Exp 28**: Interaction 1  
  * **Exp 29**: Interaction 1  
  * **Exp 30**: Interaction 1  
* **Medium (30 total)**  
  * **Exp 26**: Interactions 1, 2, 3, 4, 5, 6, 10  
  * **Exp 27**: Interactions 2, 3, 4, 5, 6, 9, 10  
  * **Exp 28**: Interactions 2, 3, 4, 5, 6  
  * **Exp 29**: Interactions 2, 3, 5, 6, 8  
  * **Exp 30**: Interactions 2, 3, 4, 5, 7, 8  
* **Complex (16 total)**  
  * **Exp 26**: Interactions 7, 8, 9  
  * **Exp 27**: Interactions 7, 8  
  * **Exp 28**: Interactions 7, 8, 9, 10  
  * **Exp 29**: Interactions 4, 7, 9, 10  
  * **Exp 30**: Interactions 6, 9, 10

***Experiments 31-35***

Across the 50 ground-truth SQL queries in the dataset, the classification yields **5 Simple**, **38 Medium**, and **7 Complex**queries.

| Complexity Level | Criteria | Query Count |
| :---- | :---- | :---- |
| **Simple** | Max 1 join, no subqueries/CTEs, no aggregations | **5** |
| **Medium** | At least 1 subquery/CTE or  2 joins, no aggregations | **38** |
| **Complex** | Contains aggregations or fails Simple/Medium criteria | **7** |

**Breakdown by Dialogue (Experiment ID)**

* **Experiment 31**: 1 Simple, 7 Medium, 2 Complex  
  

  * *Simple*: Interaction 1  
      
  * *Medium*: Interactions 2, 3, 5, 6, 8, 9, 10  
      
  * *Complex*: Interactions 4, 7 (contain COUNT)  
      
* **Experiment 32**: 1 Simple, 7 Medium, 2 Complex  
  

  * *Simple*: Interaction 1  
      
  * *Medium*: Interactions 2, 3, 4, 7, 8, 9, 10  
      
  * *Complex*: Interactions 5, 6 (contain COUNT, MIN, MAX)  
      
* **Experiment 33**: 1 Simple, 8 Medium, 1 Complex  
  

  * *Simple*: Interaction 1  
      
  * *Medium*: Interactions 2, 3, 4, 5, 6, 8, 9, 10  
      
  * *Complex*: Interaction 7 (contains COUNT)  
      
* **Experiment 34**: 1 Simple, 8 Medium, 1 Complex  
  

  * *Simple*: Interaction 1  
      
  * *Medium*: Interactions 2, 3, 4, 5, 6, 7, 8, 9  
      
  * *Complex*: Interaction 10 (contains SUM)  
      
* **Experiment 35**: 1 Simple, 8 Medium, 1 Complex  
  

  * *Simple*: Interaction 1  
      
  * *Medium*: Interactions 2, 3, 4, 5, 6, 7, 8, 9  
      
  * *Complex*: Interaction 10 (contains COUNT, MAX)

***Experiments 36-40***

| Category | Count | Criteria |
| ----- | ----- | ----- |
| **Simple** | 5 | \\le 1 JOIN, 0 subqueries, no aggregations |
| **Medium** | 26 | \\ge 1 subquery OR \\ge 2 JOINs, and no aggregations |
| **Complex** | 19 | Contains aggregations (COUNT, SUM, AVG, MIN, MAX, GROUP BY) |

**Experiment 36**

* **Interaction 1**: **Simple** (1 JOIN, 0 subqueries, no aggregations)  
* **Interaction 2**: **Medium** (1 JOIN, 1 subquery, no aggregations)  
* **Interaction 3**: **Medium** (2 JOINs, 2 subqueries, no aggregations)  
* **Interaction 4**: **Medium** (2 JOINs, 3 subqueries, no aggregations)  
* **Interaction 5**: **Medium** (2 JOINs, 4 subqueries, no aggregations)  
* **Interaction 6**: **Medium** (3 JOINs, 5 subqueries, no aggregations)  
* **Interaction 7**: **Medium** (4 JOINs, 6 subqueries, no aggregations)  
* **Interaction 8**: **Medium** (5 JOINs, 7 subqueries, no aggregations)  
* **Interaction 9**: **Medium** (5 JOINs, 8 subqueries, no aggregations)  
* **Interaction 10**: **Complex** (5 JOINs, 9 subqueries, contains COUNT and GROUP BY)

**Experiment 37**

* **Interaction 1**: **Simple** (1 JOIN, 0 subqueries, no aggregations)  
* **Interaction 2**: **Medium** (3 JOINs, CTE/subqueries, no aggregations)  
* **Interaction 3**: **Medium** (3 JOINs, CTE/subqueries, no aggregations)  
* **Interaction 4**: **Medium** (3 JOINs, CTE/subqueries, no aggregations)  
* **Interaction 5**: **Medium** (5 JOINs, CTE/subqueries, no aggregations)  
* **Interaction 6**: **Medium** (5 JOINs, CTE/subqueries, no aggregations)  
* **Interaction 7**: **Medium** (7 JOINs, CTE/subqueries, no aggregations)  
* **Interaction 8**: **Complex** (7 JOINs, CTE/subqueries, contains COUNT, AVG, GROUP BY)  
* **Interaction 9**: **Complex** (7 JOINs, CTE/subqueries, contains COUNT, MAX, GROUP BY)  
* **Interaction 10**: **Complex** (7 JOINs, CTE/subqueries, contains GROUP BY)

**Experiment 38**

* **Interaction 1**: **Simple** (0 JOINs, 0 subqueries, no aggregations)  
* **Interaction 2**: **Medium** (0 JOINs, 1 subquery, no aggregations)  
* **Interaction 3**: **Medium** (2 JOINs, 2 subqueries, no aggregations)  
* **Interaction 4**: **Complex** (2 JOINs, 3 subqueries, contains COUNT, AVG, GROUP BY)  
* **Interaction 5**: **Complex** (5 JOINs, 4 subqueries, contains GROUP BY)  
* **Interaction 6**: **Complex** (5 JOINs, 4 subqueries, contains GROUP BY)  
* **Interaction 7**: **Complex** (5 JOINs, 4 subqueries, contains COUNT, MAX, GROUP BY)  
* **Interaction 8**: **Complex** (6 JOINs, 3 subqueries, contains GROUP BY)  
* **Interaction 9**: **Complex** (6 JOINs, 4 subqueries, contains GROUP BY)  
* **Interaction 10**: **Complex** (6 JOINs, 4 subqueries, contains SUM, GROUP BY)

**Experiment 39**

* **Interaction 1**: **Simple** (1 JOIN, 0 subqueries, no aggregations)  
* **Interaction 2**: **Medium** (3 JOINs, 1 subquery, no aggregations)  
* **Interaction 3**: **Medium** (3 JOINs, 2 subqueries, no aggregations)  
* **Interaction 4**: **Medium** (5 JOINs, 3 subqueries, no aggregations)  
* **Interaction 5**: **Complex** (7 JOINs, 4 subqueries, contains SUM, GROUP BY)  
* **Interaction 6**: **Complex** (9 JOINs, 5 subqueries, contains GROUP BY)  
* **Interaction 7**: **Complex** (11 JOINs, 6 subqueries, contains COUNT, MAX, GROUP BY)  
* **Interaction 8**: **Complex** (13 JOINs, 7 subqueries, contains MAX, COUNT, GROUP BY)  
* **Interaction 9**: **Complex** (15 JOINs, 8 subqueries, contains COUNT, GROUP BY)  
* **Interaction 10**: **Complex** (17 JOINs, 9 subqueries, contains GROUP BY)

**Experiment 40**

* **Interaction 1**: **Simple** (0 JOINs, 0 subqueries, no aggregations)  
* **Interaction 2**: **Medium** (1 JOIN, 1 subquery, no aggregations)  
* **Interaction 3**: **Medium** (2 JOINs, 2 subqueries, no aggregations)  
* **Interaction 4**: **Medium** (4 JOINs, 3 subqueries, no aggregations)  
* **Interaction 5**: **Medium** (7 JOINs, 4 subqueries, no aggregations)  
* **Interaction 6**: **Medium** (10 JOINs, 5 subqueries, no aggregations)  
* **Interaction 7**: **Complex** (13 JOINs, 6 subqueries, contains COUNT, GROUP BY)  
* **Interaction 8**: **Complex** (17 JOINs, 7 subqueries, contains COUNT, GROUP BY)  
* **Interaction 9**: **Medium** (21 JOINs, 8 subqueries, no aggregations)  
* **Interaction 10**: **Medium** (25 JOINs, 9 subqueries, no aggregations)

***Experiments 41-45***

Based on the criteria, the 50 ground-truth SQL queries across the 5 dialogues are classified as follows:

| Complexity Level | Criteria Summary | Total Queries |
| :---- | :---- | :---- |
| **Simple** | ≤1 join, 0 subqueries, 0 aggregations | **4**  |
| **Medium** | ≥2 joins or ≥1 subquery, 0 aggregations | **38**  |
| **Complex** | Any query containing aggregations (COUNT, AVG, MAX, MIN, etc.) | **8**  |

**Detailed Breakdown by Dialogue**

* **Experiment 41** (10 queries):  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (9):** Interactions 2–10  
      
  * **Complex (0)**  
      
      
* **Experiment 42** (10 queries):  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (5):** Interactions 2, 3, 5, 9, 10  
      
  * **Complex (4):** Interactions 4, 6, 7, 8  
      
* **Experiment 43** (10 queries):  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (8):** Interactions 2, 3, 4, 5, 6, 8, 9, 10  
      
  * **Complex (1):** Interaction 7  
      
* **Experiment 44** (10 queries):  
  

  * **Simple (1):** Interaction 1  
      
  * **Medium (7):** Interactions 2, 3, 5, 6, 8, 9, 10  
      
  * **Complex (2):** Interactions 4, 7  
      
* **Experiment 45** (10 queries):  
  

  * **Simple (0)**  
      
      
  * **Medium (9):** Interactions 1, 2, 3, 4, 5, 6, 7, 9, 10  
      
  * **Complex (1):** Interaction 8

***Experiments 45-50***

* **Simple**: 4 queries  
    
* **Medium**: 33 queries  
    
* **Complex**: 13 queries


**Detailed Classification Breakdown**

| Experiment | Interaction ID | Classification | Criteria Matched |
| :---- | :---- | :---- | :---- |
| **46** | 1 | **Simple** | 1 Join, 0 Subqueries, 0 Aggregations  |
| **46** | 2 | **Medium** | 2 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 3 | **Medium** | 3 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 4 | **Medium** | 4 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 5 | **Medium** | 5 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 6 | **Medium** | 7 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 7 | **Medium** | 8 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 8 | **Medium** | 8 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 9 | **Medium** | 8 Joins, 1 Subquery, 0 Aggregations  |
| **46** | 10 | **Complex** | Contains Aggregations (COUNT, SUM, MAX, GROUP BY)  |
| **47** | 1 | **Simple** | 1 Join, 0 Subqueries, 0 Aggregations  |
| **47** | 2 | **Medium** | 1 Join, 1 Subquery, 0 Aggregations  |
| **47** | 3 | **Medium** | 2 Joins, 2 Subqueries, 0 Aggregations  |
| **47** | 4 | **Medium** | 2 Joins, 3 Subqueries, 0 Aggregations  |
| **47** | 5 | **Medium** | 5 Joins, 4 Subqueries, 0 Aggregations  |
| **47** | 6 | **Medium** | 6 Joins, 5 Subqueries, 0 Aggregations  |
| **47** | 7 | **Medium** | 6 Joins, 6 Subqueries, 0 Aggregations  |
| **47** | 8 | **Medium** | 6 Joins, 7 Subqueries, 0 Aggregations  |
| **47** | 9 | **Medium** | 7 Joins, 8 Subqueries, 0 Aggregations  |
| **47** | 10 | **Medium** | 7 Joins, 9 Subqueries, 0 Aggregations  |
| **48** | 1 | **Medium** | 2 Joins, 0 Subqueries, 0 Aggregations  |
| **48** | 2 | **Medium** | 2 Joins, 1 Subquery, 0 Aggregations  |
| **48** | 3 | **Medium** | 2 Joins, 2 Subqueries, 0 Aggregations  |
| **48** | 4 | **Complex** | Contains Aggregations (COUNT, AVG, GROUP BY)  |
| **48** | 5 | **Complex** | Contains GROUP BY in subquery  |
| **48** | 6 | **Medium** | 4 Joins, 4 Subqueries, 0 Aggregations  |
| **48** | 7 | **Complex** | Contains Aggregations (COUNT, GROUP BY)  |
| **48** | 8 | **Complex** | Contains Aggregations (AVG, SUM, GROUP BY)  |
| **48** | 9 | **Complex** | Contains Aggregations (COUNT, MAX, GROUP BY)  |
| **48** | 10 | **Complex** | Contains GROUP BY in subquery  |
| **49** | 1 | **Simple** | 1 Join, 0 Subqueries, 0 Aggregations  |
| **49** | 2 | **Medium** | 1 Join, 1 CTE/Subquery, 0 Aggregations  |
| **49** | 3 | **Medium** | 3 Joins, 2 CTEs/Subqueries, 0 Aggregations  |
| **49** | 4 | **Medium** | 3 Joins, 3 CTEs/Subqueries, 0 Aggregations  |
| **49** | 5 | **Medium** | 3 Joins, 4 CTEs/Subqueries, 0 Aggregations  |
| **49** | 6 | **Medium** | 3 Joins, 5 CTEs/Subqueries, 0 Aggregations  |
| **49** | 7 | **Medium** | 6 Joins, 6 CTEs/Subqueries, 0 Aggregations  |
| **49** | 8 | **Medium** | 6 Joins, 7 CTEs/Subqueries, 0 Aggregations  |
| **49** | 9 | **Medium** | 8 Joins, 8 CTEs/Subqueries, 0 Aggregations  |
| **49** | 10 | **Medium** | 8 Joins, 9 CTEs/Subqueries, 0 Aggregations  |
| **50** | 1 | **Simple** | 0 Joins, 0 Subqueries, 0 Aggregations  |
| **50** | 2 | **Medium** | 0 Joins, 1 Subquery, 0 Aggregations  |
| **50** | 3 | **Medium** | 1 Join, 2 Subqueries, 0 Aggregations  |
| **50** | 4 | **Complex** | Contains Aggregations (SUM, GROUP BY)  |
| **50** | 5 | **Medium** | 4 Joins, 4 Subqueries, 0 Aggregations  |
| **50** | 6 | **Complex** | Contains Aggregations (COUNT, MAX, GROUP BY)  |
| **50** | 7 | **Complex** | Contains GROUP BY in subquery  |
| **50** | 8 | **Complex** | Contains GROUP BY in subquery  |
| **50** | 9 | **Complex** | Contains Aggregations (COUNT, AVG, GROUP BY)  |
| **50** | 10 | **Complex** | Contains Aggregations (COUNT, AVG, GROUP BY) |

## 3.3 History of Baseball (11x10)

### 3.3.1 History of Baseball \- GPT-5.5 Instant

https://chatgpt.com/share/6a733dec-b2c0-83e9-a27e-20632e6abbe9

| Classification | Number of queries |
| ----- | ----- |
| Simple | **10** |
| Medium | **72** |
| Complex | **28** |
| **Total** | **110** |

### 3.3.2 History of Baseball – Sonnet 5 Medium

https://claude.ai/share/3589aaaf-e81a-4ade-bd26-6ba002a24dc0  
I inspected all 110 dialogue turns (11 dialogues × 10 interactions) and classified each golden\_sql query against the three criteria (join count, presence of subqueries/CTEs, presence of aggregations).  
**Classification results:**

| Category | Count |
| ----- | ----- |
| **Simple** (≤1 join, no subqueries, no aggregations) | **10** |
| **Medium** (≥1 subquery or ≥2 joins, no aggregations) | **72** |
| **Complex** (everything else, i.e. contains aggregation) | **28** |
| **Total** | **110** |

**Methodology notes:**

* "Aggregation" was detected via COUNT, SUM, AVG, MIN, MAX, GROUP BY, and window functions (... OVER (...), e.g. RANK() OVER) — any of these push a query straight into **Complex**, regardless of its join/subquery structure, per the rule that Complex \= "not simple or medium."  
* "Subquery" was detected via a WITH clause (CTE) or more than one SELECT statement in the query — this dataset makes heavy use of CTE chains (S1, S2, S3, …) that build on prior conversational turns, so nearly every follow-up turn after turn 1 in a dialogue qualifies as at least Medium.  
* Join count was counted via explicit JOIN keywords.

**Pattern observed:** Each dialogue starts with a Simple (turn 1\) or near-simple query, then complexity escalates turn-by-turn as the conversation references prior results (via CTEs/subqueries) and eventually introduces aggregation, ranking, or grouping — which is why later turns in most dialogues (e.g., exp 5, 6, 9, 11\) land in the Complex bucket, while the bulk of "building up the filter chain" turns land in Medium.

### 3.3.3 History of Baseball – K2.6 Instant High

https://www.kimi.com/share/19fd27eb-61c2-8414-8000-0000acde6fd6  
    
Based on my analysis of all 110 ground-truth SQL queries in the dataset, here are the classification results:

\*\*Simple:\*\* 10 queries    
\*\*Medium:\*\* 73 queries    
\*\*Complex:\*\* 27 queries  

\*\*Total:\*\* 110 queries

\---

\#\#\# Verification Summary

\- \*\*Simple\*\* queries have at most one join, no subqueries (no \`WITH\` CTEs or nested \`SELECT\`s), and no aggregation functions or \`GROUP BY\`/\`HAVING\` clauses.  
\- \*\*Medium\*\* queries contain at least one subquery or at least two joins, but no aggregations. This includes the extensive use of \`WITH\` CTEs and nested \`IN (SELECT ...)\` patterns that appear throughout the multi-turn dialogues.  
\- \*\*Complex\*\* queries are those with aggregation operations — specifically \`COUNT\`, \`SUM\`, \`AVG\`, \`MIN\`, \`MAX\`, \`GROUP BY\`, or \`HAVING\` — which disqualifies them from being Simple or Medium. All 27 Complex queries contain at least one of these aggregation features.

### 3.3.4 History of Baseball – Gemini 3.6 Thinking

*(Combined results of several executions due to limitation of the tool)*  
**(Experiments 1-5)**  
Based on the defined criteria across the 50 queries (5 dialogues with 10 interactions each), here is the classification breakdown:

| Classification | Criteria Summary | Query Count |
| ----- | ----- | ----- |
| **Simple** | \\le 1 join, no subqueries, no aggregations | **4** |
| **Medium** | \\ge 1 subquery or \\ge 2 joins, and no aggregations | **40** |
| **Complex** | Contains aggregations or does not fit Simple/Medium | **6** |

**Breakdown by Dialogue**

* **Dialogue 1 (Experiment 1\)**  
  * **Simple (1):** Interaction 1  
  * **Medium (9):** Interactions 2, 3, 4, 5, 6, 7, 8, 9, 10  
  * **Complex (0)**  
* **Dialogue 2 (Experiment 2\)**  
  * **Simple (1):** Interaction 1  
  * **Medium (9):** Interactions 2, 3, 4, 5, 6, 7, 8, 9, 10  
  * **Complex (0)**  
* **Dialogue 3 (Experiment 3\)**  
  * **Simple (0)**  
  * **Medium (8):** Interactions 1, 2, 3, 4, 5, 6, 7, 8  
  * **Complex (2):** Interactions 9 (COUNT, AVG), 10 (GROUP BY)  
* **Dialogue 4 (Experiment 4\)**  
  * **Simple (1):** Interaction 1  
  * **Medium (9):** Interactions 2, 3, 4, 5, 6, 7, 8, 9, 10  
  * **Complex (0)**  
* **Dialogue 5 (Experiment 5\)**  
  * **Simple (1):** Interaction 1  
  * **Medium (5):** Interactions 2, 3, 4, 5, 7  
  * **Complex (4):** Interactions 6 (COUNT, AVG), 8 (SUM), 9 (MAX), 10 (MAX, GROUP BY)

**(Experiments 6-11)**

| Complexity Level | Criteria | Query Count |
| ----- | ----- | ----- |
| **Simple** | At most 1 join, no subqueries, and no aggregations | **6** |
| **Medium** | At least 1 subquery or at least 2 joins, and no aggregations | **33** |
| **Complex** | Contains aggregations or falls outside simple and medium | **18** |
| **Total Queries** | — | **57** |

**Breakdown by Experiment**

* **Experiment 6** (10 queries): 1 Simple, 4 Medium, 5 Complex  
* **Experiment 7** (10 queries): 1 Simple, 8 Medium, 1 Complex  
* **Experiment 8** (10 queries): 1 Simple, 7 Medium, 2 Complex  
* **Experiment 9** (10 queries): 1 Simple, 1 Medium, 8 Complex  
* **Experiment 10** (10 queries): 1 Simple, 9 Medium, 0 Complex  
* **Experiment 11** (7 queries): 1 Simple, 4 Medium, 2 Complex
