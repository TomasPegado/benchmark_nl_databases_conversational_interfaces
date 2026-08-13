# Ground Truth SQL Query Correctness Analysis 

# 1\. Summary

All dialogues were generated with GPT-5.6, with improvements on the dialogue-generation prompts.

An LLM-based correctness analysis of the ground truth SQL queries was carried out using state-of-the-art LLMs, using the prompt in Section 2 (as of July 2026):

* Claude Sonnet 5 Medium on the Anthropic MacOS App   
* K2.6 Standard High on the Kimi MacOS App   
* Gemini 3.6 Thinking on the Gemini MacOS App

Section 3 contains the detailed results and additionally includes the evaluations of GPT-5.5 Instant, which were discarded, however, since this LLM is of the same family as GPT-5.6 Sol, used to generate the dialogues. The following tables summarize the results.

|  |  | Sonnet 5 Medium |  | K2.6 Instant High |  | Gemini 3.6 Thinking |  |
| ----- | ----- | :---: | :---: | :---: | :---: | :---: | :---: |
|  |  | **Correct** | **Incorrect** | **Correct** | **Incorrect** | **Correct** | **Incorrect** |
| Mondial | 500 | 467 | 33 | 500 | 0 | 472 | 28 |
| Formula 1 | 500 | 363 | 137 | 500 | 0 | 495 | 5 |
| Hist. Baseball | 110 | 100 | 10 | 106 | 4 | 108 | 2 |

|  |  | Consensus (Count) |  | Consensus (%) |  |
| ----- | ----- | :---: | :---: | :---: | :---: |
|  |  | **Correct** | **Incorrect** | **Correct** | **Incorrect** |
| Mondial | 500 | 472 | 28 | **94%** | **6%** |
| Formula 1 | 500 | 495 | 5 | **99%** | **1%** |
| Hist. Baseball | 110 | 108 | 2 | **98%** | **2%** |

Note: the consensus was computed by analyzing the correctness of each SQL query, as judged by each LLM: if the query was considered correct by at least two LLMs, the consensus was that it was correct. 

# 2\. Prompt

You are an expert in text-to-SQL agents.

Your task is to inspect the list of dialogues and the database schema passed as attachments and classify each ground-truth SQL query according to the following criteria:

- Correct: The ground-truth SQL query correctly responds to the natural language question specified.

- Incorrect: The ground-truth SQL query does not correctly represent the natural language question specified.

The list of dialogues is a json file. Each dialogue has the following structure:

- experiment_id:	The dialogue id.
- total_expected_interactions:	The total number of interactions in the dialogue.
- Interactions:	The list of interactions in the dialogue, numbered 0, 1, 2, …, n.
- i:	The interaction number.
- interaction_id:	The interaction id.
- Speaker:	"User".
- Utterance:	A natural language user question, which can be partially formulated.
- Intention:	The intention of the user question, which is a natural language sentence fully defining the user question.
- ground_truths:	
    - tables_from_schema_linking	 The list of tables used in the ground-truth SQL query.
    - golden_sql	The ground-truth SQL query responding the user question.

The intention key specifies the natural language question and the golden_sql key specifies the ground-truth SQL query responding the question.

You should output the number of queries in each classification.

You should also output a table indicating, for each incorrect SQL query, the dialogue id, the iteraction id, the natural language question, and the ground-truth SQL query.

## 3\. Results

## 3.1 Mondial

### 3.1.1 Mondial – GPT-5.5 Instant

https://chatgpt.com/share/6a735c03-7e30-83e9-8e95-f7511cdf7a21

I inspected the attached dataset structure and schema. The dataset contains **50 dialogues × 10 interactions \= 500 ground-truth SQL queries**. 20260724-gpt5\_6-mondial\_dialogue\_dataset 50x10.jsonJSON

Based on a consistency review of the natural-language intentions against the corresponding golden\_sql queries and the provided schema, I did **not identify any SQL query that contradicts its associated intention**.

**Summary**

| Classification | Number of queries |
| ----- | ----- |
| Correct | **500** |
| Incorrect | **0** |

**Incorrect SQL queries**

No incorrect ground-truth SQL queries were found.

| Dialogue ID | Interaction ID | Natural language question | Ground-truth SQL |
| ----- | ----- | ----- | ----- |
| *None* | *None* | *None* | *None* |

The evaluation was performed over the entire dataset of **500 interactions** contained in the uploaded JSON file. 20260724-gpt5\_6-mondial\_dialogue\_dataset 50x10.jsonJSON

### 3.1.2 Mondial – Sonnet 5 Medium

https://claude.ai/share/96c97773-61c5-4c16-89c2-73d13bdab442

All 33 confirmed. I've now cross-checked the results against the schema, then layered heuristic checks (ordering direction, comparison operators, COUNT/GROUP BY logic, negation handling, and declared-table-vs-used-table consistency) across all 500 interactions. Aside from the 33 confirmed cases, no other logic errors surfaced.

**Summary**

| Classification | Count |
| ----- | ----- |
| **Correct** | 467 |
| **Incorrect** | 33 |
| **Total** | 500 |

**Why the 33 are incorrect:** every one of them references a column called META\_REPCOL on one of the query's tables (e.g. D.META\_REPCOL, GR.META\_REPCOL). This column does not exist anywhere in the Mondial schema — it's a leftover template placeholder (evidently meant to stand in for whatever "representative/stored/reporting label" column the user was asking about) that was never substituted with a real column name. Any query containing it will fail to execute against the actual database, so it cannot correctly answer the corresponding natural-language question.

**Incorrect queries**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL |
| ----- | ----- | ----- | ----- |
| 5 | 9 | Of those, retain the ones in Adrar and show their stored desert labels. | ... SELECT D.DESERT, D.COUNTRY, D.PROVINCE, D.META\_REPCOL FROM MONDIAL\_GEO\_DESERT D WHERE ... AND D.PROVINCE \= 'Adrar' ORDER BY D.DESERT ASC |
| 6 | 3 | What representative labels are stored for those Aargau records? | SELECT RIVER, COUNTRY, PROVINCE, META\_REPCOL FROM MONDIAL\_GEO\_RIVER WHERE (RIVER, COUNTRY, PROVINCE) IN (... COUNTRY \= 'CH' AND PROVINCE \= 'Aargau') ORDER BY RIVER ASC |
| 6 | 4 | Can you present those same labeled records in reverse alphabetical order by river? | SELECT RIVER, COUNTRY, PROVINCE, META\_REPCOL FROM MONDIAL\_GEO\_RIVER WHERE (RIVER, COUNTRY, PROVINCE) IN (... COUNTRY \= 'CH' AND PROVINCE \= 'Aargau') ORDER BY RIVER DESC |
| 9 | 2 | For those same source entries, show the stored source label too, and sort them by province. | WITH P1 AS (...) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE ... ORDER BY G.PROVINCE ASC, G.RIVER ASC |
| 9 | 9 | For those exact results, show the source country, province, and stored source label, ordered by province and then river. | WITH P1..P8 AS (...) SELECT G.RIVER, RT.LAKE, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G ... ORDER BY G.PROVINCE ASC, G.RIVER ASC, RT.LAKE ASC |
| 12 | 9 | Keep that link only if its merge record has no metadata marker. | WITH P1..P8 AS (...) SELECT M.SEA1, M.SEA2, M.META\_REPCOL FROM MONDIAL\_MERGESWITH M ... AND M.META\_REPCOL IS NULL ORDER BY M.SEA1 ASC, M.SEA2 ASC |
| 12 | 10 | Finally, display the two sea identifiers for that filtered link in reverse alphabetical order by the connected sea. | WITH P1..P9 AS (... AND M.META\_REPCOL IS NULL) SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M ... ORDER BY M.SEA2 DESC, M.SEA1 DESC |
| 15 | 6 | What representative label is stored for each of those estuary records? | WITH S1..S5 AS (...) SELECT E.RIVER, E.META\_REPCOL FROM MONDIAL\_GEO\_ESTUARY E WHERE ... ORDER BY E.META\_REPCOL ASC, E.RIVER ASC |
| 21 | 4 | For that shorter list, display the label text alongside the airport name and code, ordered from west to east. | SELECT A.NAME, A.IATACODE, A.META\_REPCOL, A.LONGITUDE FROM MONDIAL\_AIRPORT A WHERE ... ORDER BY A.LONGITUDE ASC, A.IATACODE ASC |
| 22 | 8 | Of these mountain-bearing records, keep only those whose metadata label exactly matches the island name. | SELECT G.ISLAND, G.COUNTRY, G.PROVINCE, G.META\_REPCOL, M.MOUNTAIN FROM MONDIAL\_GEO\_ISLAND G ... AND G.META\_REPCOL \= G.ISLAND ORDER BY M.MOUNTAIN ASC, G.PROVINCE ASC |
| 22 | 9 | For these filtered island records, show every city and mountain pairing found on the same island. | SELECT G.ISLAND, G.COUNTRY, G.PROVINCE, L.CITY, M.MOUNTAIN FROM MONDIAL\_GEO\_ISLAND G ... WHERE ... AND G2.META\_REPCOL \= G2.ISLAND) ORDER BY L.CITY ASC, M.MOUNTAIN ASC, G.PROVINCE ASC |
| 22 | 10 | What island-group name and island type go with each of those city and mountain pairings? | SELECT G.ISLAND, G.COUNTRY, G.PROVINCE, I.ISLANDS, I.TYPE, L.CITY, M.MOUNTAIN FROM MONDIAL\_GEO\_ISLAND G ... AND G2.META\_REPCOL \= G2.ISLAND) ORDER BY L.CITY ASC, M.MOUNTAIN ASC, G.PROVINCE ASC |
| 25 | 5 | What stored representative label does each of those mountain-location records have? | SELECT GM.MOUNTAIN, GM.COUNTRY, GM.PROVINCE, GM.META\_REPCOL FROM MONDIAL\_GEO\_MOUNTAIN GM WHERE ... ORDER BY GM.MOUNTAIN ASC, GM.COUNTRY ASC, GM.PROVINCE ASC |
| 29 | 1 | Which estuary records are in country D? | SELECT RIVER, COUNTRY, PROVINCE, META\_REPCOL FROM MONDIAL\_GEO\_ESTUARY WHERE COUNTRY \= 'D' ORDER BY RIVER ASC, PROVINCE ASC |
| 29 | 2 | Of those, which ones are in Sachsen-Anhalt? | SELECT RIVER, COUNTRY, PROVINCE, META\_REPCOL FROM MONDIAL\_GEO\_ESTUARY WHERE (RIVER, COUNTRY, PROVINCE) IN (...) AND PROVINCE \= 'Sachsen-Anhalt' ORDER BY RIVER ASC |
| 34 | 3 | For the source records that had an alternate-name match, show the river, country, province, and representative label, ordered by province. | WITH S1, S2 AS (...) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G ... ORDER BY G.PROVINCE ASC, G.COUNTRY ASC, G.RIVER ASC |
| 34 | 4 | From that set, keep only records whose representative label is identical to the river name. | WITH S1..S3 AS (...) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE ... AND G.META\_REPCOL \= G.RIVER ORDER BY G.RIVER ASC, G.COUNTRY ASC, G.PROVINCE ASC |
| 34 | 5 | Which historical population observations are available for the provinces in that filtered set? | WITH S1..S4 AS (... G4.META\_REPCOL \= G4.RIVER) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, PP.YEAR, PP.POPULATION FROM MONDIAL\_GEO\_SOURCE G ... ORDER BY PP.YEAR ASC, G.COUNTRY ASC, G.PROVINCE ASC |
| 34 | 6 | Of the source records with population history, retain those whose province name contains "Sumatera" and sort them by river. | WITH S1..S5 AS (... G4.META\_REPCOL \= G4.RIVER ...) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE ... AND G.PROVINCE LIKE '%Sumatera%' ORDER BY G.RIVER ASC, G.COUNTRY ASC, G.PROVINCE ASC |
| 34 | 7 | Now return just the distinct country and province pairs for that subset, with countries first. | WITH S1..S6 AS (... G4.META\_REPCOL \= G4.RIVER ...) SELECT DISTINCT G.COUNTRY, G.PROVINCE FROM MONDIAL\_GEO\_SOURCE G WHERE ... ORDER BY G.COUNTRY ASC, G.PROVINCE ASC |
| 34 | 8 | For the source records behind those pairs, add each province's current population, area, capital, and capital province. | WITH S1..S7 AS (... G4.META\_REPCOL \= G4.RIVER ...) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, P.POPULATION, P.AREA, P.CAPITAL, P.CAPPROV FROM MONDIAL\_GEO\_SOURCE G ... ORDER BY G.COUNTRY ASC, G.PROVINCE ASC, G.RIVER ASC |
| 34 | 9 | Among those records, keep only river names beginning with "B" and order the results by province, then river. | WITH S1..S8 AS (... G4.META\_REPCOL \= G4.RIVER ...) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE ... AND G.RIVER LIKE 'B%' ORDER BY G.PROVINCE ASC, G.RIVER ASC, G.COUNTRY ASC |
| 34 | 10 | Finally, pair those remaining river sources with their province aliases and all dated population observations. | WITH S1..S9 AS (... G4.META\_REPCOL \= G4.RIVER ...) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, O.OTHERNAME, PP.YEAR, PP.POPULATION FROM MONDIAL\_GEO\_SOURCE G ... ORDER BY G.COUNTRY ASC, G.PROVINCE ASC, O.OTHERNAME ASC, PP.YEAR ASC |
| 39 | 5 | Now list those same continents alphabetically with their areas and reference labels. | SELECT MC.NAME, MC.AREA, MC.META\_REPCOL FROM MONDIAL\_CONTINENT MC WHERE ... ORDER BY MC.NAME ASC |
| 42 | 2 | For those rivers, show the stored label alongside the river, country, and province, ordered alphabetically by river. | SELECT GR.RIVER, GR.COUNTRY, GR.PROVINCE, GR.META\_REPCOL FROM MONDIAL\_GEO\_RIVER GR WHERE ... ORDER BY GR.RIVER ASC, GR.COUNTRY ASC, GR.PROVINCE ASC |
| 42 | 5 | Now show just the river identifiers and stored labels for that same set, sorted by country, province, and river. | WITH NAMED\_RIVERS, PREVIOUS\_RIVERS AS (...) SELECT GR.RIVER, GR.COUNTRY, GR.PROVINCE, GR.META\_REPCOL FROM MONDIAL\_GEO\_RIVER GR WHERE ... ORDER BY GR.COUNTRY ASC, GR.PROVINCE ASC, GR.RIVER ASC |
| 42 | 9 | For the selected rivers that had those same-province source matches, show their stored labels, excluding missing labels. | WITH NAMED\_RIVERS..PREVIOUS\_RIVERS AS (...) SELECT GR.RIVER, GR.COUNTRY, GR.PROVINCE, GR.META\_REPCOL FROM MONDIAL\_GEO\_RIVER GR WHERE ... AND GR.META\_REPCOL IS NOT NULL ORDER BY GR.RIVER ASC |
| 42 | 10 | Finally, how many of those labeled river records are there in each country? | WITH NAMED\_RIVERS..PREVIOUS\_RIVERS AS (... GR6.META\_REPCOL IS NOT NULL) SELECT GR.COUNTRY, COUNT(\*) AS RIVER\_RECORD\_COUNT FROM MONDIAL\_GEO\_RIVER GR ... GROUP BY GR.COUNTRY ORDER BY RIVER\_RECORD\_COUNT DESC, GR.COUNTRY ASC |
| 46 | 6 | For exactly those continents, include their descriptive label as well as their name and area. | SELECT MC.NAME, MC.AREA, MC.META\_REPCOL FROM MONDIAL\_CONTINENT MC WHERE ... ORDER BY MC.NAME ASC |
| 46 | 7 | From that exact set, retain only continents with an area of at least 9,500,000. | SELECT MC.NAME, MC.AREA, MC.META\_REPCOL FROM MONDIAL\_CONTINENT MC WHERE ... AND MC.AREA \>= 9500000 ORDER BY MC.NAME ASC |
| 47 | 4 | For that narrowed set, show the stored label too and list the largest continent first. | SELECT C.NAME, C.AREA, C.META\_REPCOL FROM MONDIAL\_CONTINENT C WHERE ... ORDER BY C.AREA DESC, C.NAME ASC |
| 47 | 10 | Finally, show the name, area, and stored label for exactly those continents, ordered from smallest to largest. | SELECT C.NAME, C.AREA, C.META\_REPCOL FROM MONDIAL\_CONTINENT C WHERE ... ORDER BY C.AREA ASC, C.NAME ASC |
| 48 | 4 | For those matched records, show their reporting labels, excluding any that lack a province. | SELECT G.SEA, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SEA G WHERE ... AND G.PROVINCE IS NOT NULL ORDER BY G.PROVINCE ASC |

**Note on method:** I built a schema-only SQLite database from the DDL (tables prefixed MONDIAL\_ to match the golden SQL's naming convention) and executed every one of the 500 golden queries against it to catch syntax/column errors, then ran targeted heuristic checks across the full set (ORDER BY direction vs. wording like "ascending/descending/reverse alphabetical," comparison-operator direction for "at least/at most/more than/fewer than," COUNT/GROUP BY expectations for "how many...each," and negation handling for "excluding"). Two queries (dialogue 13/interaction 10 and dialogue 28/interaction 10\) triggered a SQLite parse error on DATE '1960-01-01' syntax, but this is valid ANSI/Oracle date-literal syntax (just unsupported by SQLite's parser) — not a real defect, so those remain classified as Correct. All other flags raised by the heuristics turned out to be false positives on closer inspection (e.g., existential "at least one" phrased via JOIN/EXISTS rather than a numeric \>=, or window-function COUNT(\*) OVER (PARTITION BY ...) satisfying "for each ... add the count").

### 3.1.3 Mondial – K2.6 Instant High

https://www.kimi.com/share/19fd3001-4d52-80c9-8000-000047fe86ca  
    
Based on my thorough examination of the dialogue dataset and database schema, I analyzed the natural language intentions against the ground-truth SQL queries. I inspected the semantic correctness, table joins, filter conditions, column selections, context chaining across multi-turn dialogues, and ordering clauses.

\#\# Classification Summary

| Classification | Count |
| :---- | :---- |
| **\*\*Correct\*\*** | 500 |
| **\*\*Incorrect\*\*** | 0 |

\#\# Incorrect Queries Table

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| **\*(none)\*** | \*(none)\* | \*(none)\* | \*(none)\* |

\*\*Explanation:\*\*

All 500 ground-truth SQL queries correctly represent their corresponding natural language questions. The dataset demonstrates consistent and accurate:

1\. \*\*Schema linking\*\* — All referenced tables and columns exist in the provided Mondial schema.  
2\. \*\*Context maintenance\*\* — Multi-turn dialogues properly chain previous results using nested \`IN\` clauses or CTEs (\`WITH\` clauses), ensuring each subsequent query operates on the exact set of records identified in prior interactions.  
3\. \*\*Filter conditions\*\* — \`WHERE\` clauses correctly implement the numeric ranges, string patterns (\`LIKE\`), null checks (\`IS NOT NULL\`), and geographic constraints specified in the intentions.  
4\. \*\*Join logic\*\* — Inner joins, left joins, and multi-table joins use correct key relationships (e.g., \`A.ISLAND \= I.NAME\`, \`G.PROVINCE \= P.NAME AND G.COUNTRY \= P.COUNTRY\`).  
5\. \*\*Aggregation and grouping\*\* — \`COUNT\`, \`SUM\`, \`MIN\`, \`MAX\`, \`GROUP BY\`, and \`HAVING\` clauses match the analytical requests (e.g., counting distinct cities, summing areas, finding earliest years).  
6\. \*\*Sorting\*\* — \`ORDER BY\` clauses correctly implement ascending, descending, and multi-column tie-breaking requirements specified in the utterances.

No queries were found to have semantic mismatches, missing constraints, incorrect column projections, or broken context chains relative to their stated intentions.

### 3.1.4 Mondial – Gemini 3.6 Thinking

*(Combined results of several executions due to limitation of the tool)*

***Experiments 1-5***  
After inspecting the provided dataset and database schema, each ground-truth SQL query was verified for schema validity, join correctness, and semantic alignment with the natural language intention.  
**Classification Summary**

* **Correct:** 49 queries  
* **Incorrect:** 1 query

**Incorrect SQL Queries**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query | Reason for Incorrectness |
| ----- | ----- | ----- | ----- | ----- |
| 5 | 9 | Of those, retain the ones in Adrar and show their stored desert labels. | WITH S1 AS (SELECT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D JOIN MONDIAL\_PROVINCE P ON D.PROVINCE \= P.NAME AND D.COUNTRY \= P.COUNTRY WHERE D.COUNTRY \= 'RIM'), S2 AS (SELECT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D JOIN MONDIAL\_PROVINCE P ON D.PROVINCE \= P.NAME AND D.COUNTRY \= P.COUNTRY WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S1.DESERT, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT DISTINCT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D JOIN MONDIAL\_PROVINCE P ON D.PROVINCE \= P.NAME AND D.COUNTRY \= P.COUNTRY LEFT JOIN MONDIAL\_GEO\_ESTUARY E ON E.PROVINCE \= P.NAME AND E.COUNTRY \= P.COUNTRY WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S2.DESERT, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S3.DESERT, S3.COUNTRY, S3.PROVINCE FROM S3) AND D.DESERT LIKE 'Erg%'), S5 AS (SELECT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D JOIN MONDIAL\_PROVINCE P ON D.PROVINCE \= P.NAME AND D.COUNTRY \= P.COUNTRY WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S4.DESERT, S4.COUNTRY, S4.PROVINCE FROM S4)), S6 AS (SELECT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D JOIN MONDIAL\_PROVINCE P ON D.PROVINCE \= P.NAME AND D.COUNTRY \= P.COUNTRY WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S5.DESERT, S5.COUNTRY, S5.PROVINCE FROM S5)), S7 AS (SELECT DISTINCT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D JOIN MONDIAL\_PROVINCE P ON D.PROVINCE \= P.NAME AND D.COUNTRY \= P.COUNTRY LEFT JOIN MONDIAL\_GEO\_ESTUARY E ON E.PROVINCE \= P.NAME AND E.COUNTRY \= P.COUNTRY WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S6.DESERT, S6.COUNTRY, S6.PROVINCE FROM S6)), S8 AS (SELECT D.DESERT, D.COUNTRY, D.PROVINCE FROM MONDIAL\_GEO\_DESERT D WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S7.DESERT, S7.COUNTRY, S7.PROVINCE FROM S7) AND D.COUNTRY \= 'RIM') SELECT D.DESERT, D.COUNTRY, D.PROVINCE, D.META\_REPCOL FROM MONDIAL\_GEO\_DESERT D WHERE (D.DESERT, D.COUNTRY, D.PROVINCE) IN (SELECT S8.DESERT, S8.COUNTRY, S8.PROVINCE FROM S8) AND D.PROVINCE \= 'Adrar' ORDER BY D.DESERT ASC | The column META\_REPCOL referenced on table MONDIAL\_GEO\_DESERT (D.META\_REPCOL) does not exist in the database schema. |

***Experiments 6-10***

* **Correct Queries:** 49  
* **Incorrect Queries:** 1

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| **6** | **10** | **Utterance:**"Which joined river names contribute to each of those country pairs?"  **Intention:**"List the river names belonging to each occurrence-country and source-country pair produced by the preceding count."  | SELECT G.COUNTRY AS OCCURRENCE\_COUNTRY, S.COUNTRY AS SOURCE\_COUNTRY, R.NAME FROM MONDIAL\_GEO\_RIVER G JOIN MONDIAL\_RIVER R ON G.RIVER \= R.NAME JOIN MONDIAL\_GEO\_SOURCE S ON S.RIVER \= R.NAME WHERE (G.COUNTRY, S.COUNTRY) IN (SELECT G9.COUNTRY, S9.COUNTRY FROM MONDIAL\_GEO\_RIVER G9 JOIN MONDIAL\_RIVER R9 ON G9.RIVER \= R9.NAME JOIN MONDIAL\_GEO\_SOURCE S9 ON S9.RIVER \= R9.NAME WHERE (G9.RIVER, G9.COUNTRY, G9.PROVINCE, R9.NAME, S9.RIVER, S9.COUNTRY, S9.PROVINCE) IN (SELECT G8.RIVER, G8.COUNTRY, G8.PROVINCE, R8.NAME, S8.RIVER, S8.COUNTRY, S8.PROVINCE FROM MONDIAL\_GEO\_RIVER G8 JOIN MONDIAL\_RIVER R8 ON G8.RIVER \= R8.NAME JOIN MONDIAL\_GEO\_SOURCE S8 ON S8.RIVER \= R8.NAME WHERE G8.COUNTRY \= 'CH' AND G8.PROVINCE \= 'Aargau' AND R8.LENGTH \>= 100\) GROUP BY G9.COUNTRY, S9.COUNTRY) ORDER BY G.COUNTRY ASC, S.COUNTRY ASC, R.NAME ASC |

The outer query in Interaction 10 fails to constrain the rivers to those previously selected (Swiss rivers in Aargau with length ≥100 km). By filtering only on (G.COUNTRY, S.COUNTRY), it selects every river in the database matching those country pairs rather than returning only the specific contributing rivers.

***Experiments 11-15***

Out of the 50 total ground-truth SQL queries across the 5 dialogues, **47** are classified as **Correct** and **3** are classified as **Incorrect**.

* **Correct Queries:** 47  
* **Incorrect Queries:** 3

The incorrect queries fail because they reference a non-existent column (META\_REPCOL) that is not defined in the corresponding database schema tables (MONDIAL\_MERGESWITH and MONDIAL\_GEO\_ESTUARY).

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| ----- | ----- | ----- | ----- |
| **12** | **9** | Keep that link only if its merge record has no metadata marker. | WITH P1 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE M.SEA1 \= 'Andaman Sea' AND B.DEPTH IS NOT NULL), P2 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P1.SEA1, P1.SEA2 FROM P1)), P3 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P2.SEA1, P2.SEA2 FROM P2) AND M.SEA2 \> 'Gulf of Bengal'), P4 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P3.SEA1, P3.SEA2 FROM P3)), P5 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P4.SEA1, P4.SEA2 FROM P4)), P6 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P5.SEA1, P5.SEA2 FROM P5)), P7 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P6.SEA1, P6.SEA2 FROM P6) AND M.SEA2 LIKE '%Ocean%'), P8 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P7.SEA1, P7.SEA2 FROM P7)) SELECT M.SEA1, M.SEA2, M.META\_REPCOL FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P8.SEA1, P8.SEA2 FROM P8) AND M.META\_REPCOL IS NULL ORDER BY M.SEA1 ASC, M.SEA2 ASC |
| **12** | **10** | Finally, display the two sea identifiers for that filtered link in reverse alphabetical order by the connected sea. | WITH P1 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE M.SEA1 \= 'Andaman Sea' AND B.DEPTH IS NOT NULL), P2 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P1.SEA1, P1.SEA2 FROM P1)), P3 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P2.SEA1, P2.SEA2 FROM P2) AND M.SEA2 \> 'Gulf of Bengal'), P4 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P3.SEA1, P3.SEA2 FROM P3)), P5 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P4.SEA1, P4.SEA2 FROM P4)), P6 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P5.SEA1, P5.SEA2 FROM P5)), P7 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P6.SEA1, P6.SEA2 FROM P6) AND M.SEA2 LIKE '%Ocean%'), P8 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P7.SEA1, P7.SEA2 FROM P7)), P9 AS (SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P8.SEA1, P8.SEA2 FROM P8) AND M.META\_REPCOL IS NULL) SELECT M.SEA1, M.SEA2 FROM MONDIAL\_MERGESWITH M JOIN MONDIAL\_SEA A ON M.SEA1 \= A.NAME JOIN MONDIAL\_SEA B ON M.SEA2 \= B.NAME WHERE (M.SEA1, M.SEA2) IN (SELECT P9.SEA1, P9.SEA2 FROM P9) ORDER BY M.SEA2 DESC, M.SEA1 DESC |
| **15** | **6** | What representative label is stored for each of those estuary records? | WITH S1 AS (SELECT E1.RIVER, E1.COUNTRY, E1.PROVINCE FROM MONDIAL\_GEO\_ESTUARY E1 JOIN MONDIAL\_RIVER R1 ON E1.RIVER \= R1.NAME WHERE E1.COUNTRY \= 'D' AND R1.LENGTH IS NOT NULL AND R1.LENGTH \<= 500), S2 AS (SELECT E2.RIVER, E2.COUNTRY, E2.PROVINCE FROM MONDIAL\_GEO\_ESTUARY E2 JOIN MONDIAL\_RIVER R2 ON E2.RIVER \= R2.NAME WHERE (E2.RIVER, E2.COUNTRY, E2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT E3.RIVER, E3.COUNTRY, E3.PROVINCE FROM MONDIAL\_GEO\_ESTUARY E3 JOIN MONDIAL\_RIVER R3 ON E3.RIVER \= R3.NAME WHERE (E3.RIVER, E3.COUNTRY, E3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT E4.RIVER, E4.COUNTRY, E4.PROVINCE FROM MONDIAL\_GEO\_ESTUARY E4 JOIN MONDIAL\_RIVER R4 ON E4.RIVER \= R4.NAME WHERE (E4.RIVER, E4.COUNTRY, E4.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3)), S5 AS (SELECT E5.RIVER, E5.COUNTRY, E5.PROVINCE FROM MONDIAL\_GEO\_ESTUARY E5 WHERE (E5.RIVER, E5.COUNTRY, E5.PROVINCE) IN (SELECT S4.RIVER, S4.COUNTRY, S4.PROVINCE FROM S4)) SELECT E.RIVER, E.META\_REPCOL FROM MONDIAL\_GEO\_ESTUARY E WHERE (E.RIVER, E.COUNTRY, E.PROVINCE) IN (SELECT S5.RIVER, S5.COUNTRY, S5.PROVINCE FROM S5) ORDER BY E.META\_REPCOL ASC, E.RIVER ASC |

***Experiments 16-20***

All 50 ground-truth SQL queries across the 5 dialogues were inspected against their corresponding schema and natural language intentions, and all queries accurately reflect the specified user questions.

### Query Classification Summary

* **Correct SQL Queries:** 50  
* **Incorrect SQL Queries:** 0

### Incorrect SQL Queries

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| *None* | *None* | *None* | *None* |

***Experiments 21-25***

Out of the 50 ground-truth SQL queries evaluated across 5 dialogues:

* **Correct:** 45 queries correctly align with the database schema and answer the corresponding natural language question.  
* **Incorrect:** 5 queries reference a non-existent column (META\_REPCOL) in the provided database schema.

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| ----- | ----- | ----- | ----- |
| **21** | 4 | For the previously selected airports above 300 meters, show each airport's name, IATA code, descriptive label, and longitude, ordered from lowest to highest longitude. | SELECT A.NAME, A.IATACODE, A.META\_REPCOL, A.LONGITUDE FROM MONDIAL\_AIRPORT A WHERE (A.IATACODE) IN (SELECT A1.IATACODE FROM MONDIAL\_AIRPORT A1 WHERE (A1.IATACODE) IN (SELECT A2.IATACODE FROM MONDIAL\_AIRPORT A2 JOIN MONDIAL\_CITY C2 ON A2.CITY \= C2.NAME AND A2.COUNTRY \= C2.COUNTRY AND A2.PROVINCE \= C2.PROVINCE WHERE (A2.IATACODE) IN (SELECT A3.IATACODE FROM MONDIAL\_AIRPORT A3 WHERE A3.COUNTRY \= 'CZ' AND A3.GMTOFFSET \= 1 AND A3.ELEVATION \>= 200)) AND A1.ELEVATION \> 300\) ORDER BY A.LONGITUDE ASC, A.IATACODE ASC |
| **22** | 8 | From the previously selected city-bearing Madagaskar island records with mountains, retain geographic records whose metadata label is identical to the island name. | SELECT G.ISLAND, G.COUNTRY, G.PROVINCE, G.META\_REPCOL, M.MOUNTAIN FROM MONDIAL\_GEO\_ISLAND G JOIN MONDIAL\_ISLAND I ON G.ISLAND \= I.NAME JOIN MONDIAL\_MOUNTAINONISLAND M ON I.NAME \= M.ISLAND WHERE (G.ISLAND, G.COUNTRY, G.PROVINCE) IN (SELECT DISTINCT G2.ISLAND, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_ISLAND G2 JOIN MONDIAL\_ISLAND I2 ON G2.ISLAND \= I2.NAME JOIN MONDIAL\_LOCATEDON L2 ON I2.NAME \= L2.ISLAND JOIN MONDIAL\_MOUNTAINONISLAND M2 ON I2.NAME \= M2.ISLAND WHERE G2.ISLAND \= 'Madagaskar' AND G2.COUNTRY \= 'RM' AND G2.PROVINCE IS NOT NULL) AND G.META\_REPCOL \= G.ISLAND ORDER BY M.MOUNTAIN ASC, G.PROVINCE ASC |
| **22** | 9 | For the previously filtered Madagaskar geographic records, list each pairing of a located city and a mountain on the corresponding island. | SELECT G.ISLAND, G.COUNTRY, G.PROVINCE, L.CITY, M.MOUNTAIN FROM MONDIAL\_GEO\_ISLAND G JOIN MONDIAL\_ISLAND I ON G.ISLAND \= I.NAME JOIN MONDIAL\_LOCATEDON L ON I.NAME \= L.ISLAND JOIN MONDIAL\_MOUNTAINONISLAND M ON I.NAME \= M.ISLAND WHERE (G.ISLAND, G.COUNTRY, G.PROVINCE) IN (SELECT DISTINCT G2.ISLAND, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_ISLAND G2 JOIN MONDIAL\_ISLAND I2 ON G2.ISLAND \= I2.NAME JOIN MONDIAL\_LOCATEDON L2 ON I2.NAME \= L2.ISLAND JOIN MONDIAL\_MOUNTAINONISLAND M2 ON I2.NAME \= M2.ISLAND WHERE G2.ISLAND \= 'Madagaskar' AND G2.COUNTRY \= 'RM' AND G2.PROVINCE IS NOT NULL AND G2.META\_REPCOL \= G2.ISLAND) ORDER BY L.CITY ASC, M.MOUNTAIN ASC, G.PROVINCE ASC |
| **22** | 10 | For the previously selected Madagaskar city and mountain pairings, add the corresponding island-group name and island type. | SELECT G.ISLAND, G.COUNTRY, G.PROVINCE, I.ISLANDS, I.TYPE, L.CITY, M.MOUNTAIN FROM MONDIAL\_GEO\_ISLAND G JOIN MONDIAL\_ISLAND I ON G.ISLAND \= I.NAME JOIN MONDIAL\_LOCATEDON L ON I.NAME \= L.ISLAND JOIN MONDIAL\_MOUNTAINONISLAND M ON I.NAME \= M.ISLAND WHERE (G.ISLAND, G.COUNTRY, G.PROVINCE) IN (SELECT DISTINCT G2.ISLAND, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_ISLAND G2 JOIN MONDIAL\_ISLAND I2 ON G2.ISLAND \= I2.NAME JOIN MONDIAL\_LOCATEDON L2 ON I2.NAME \= L2.ISLAND JOIN MONDIAL\_MOUNTAINONISLAND M2 ON I2.NAME \= M2.ISLAND WHERE G2.ISLAND \= 'Madagaskar' AND G2.COUNTRY \= 'RM' AND G2.PROVINCE IS NOT NULL AND G2.META\_REPCOL \= G2.ISLAND) ORDER BY L.CITY ASC, M.MOUNTAIN ASC, G.PROVINCE ASC |
| **25** | 5 | Report the stored representative label for every mountain-location record in the previously listed set. | SELECT GM.MOUNTAIN, GM.COUNTRY, GM.PROVINCE, GM.META\_REPCOL FROM MONDIAL\_GEO\_MOUNTAIN GM WHERE (GM.MOUNTAIN, GM.COUNTRY, GM.PROVINCE) IN (SELECT GM2.MOUNTAIN, GM2.COUNTRY, GM2.PROVINCE FROM MONDIAL\_GEO\_MOUNTAIN GM2 WHERE (GM2.MOUNTAIN, GM2.COUNTRY, GM2.PROVINCE) IN (SELECT GM1.MOUNTAIN, GM1.COUNTRY, GM1.PROVINCE FROM MONDIAL\_GEO\_MOUNTAIN GM1 JOIN MONDIAL\_MOUNTAIN M1 ON GM1.MOUNTAIN \= M1.NAME WHERE GM1.MOUNTAIN LIKE 'A%') AND GM2.COUNTRY IN ('IND', 'IR')) ORDER BY GM.MOUNTAIN ASC, GM.COUNTRY ASC, GM.PROVINCE ASC |

All five incorrect queries fail because they attempt to select or filter on the column META\_REPCOL, which does not exist in AIRPORT, GEO\_ISLAND, or GEO\_MOUNTAIN tables in the schema.

***Experiments 26-30***

* **Correct Queries:** 47  
* **Incorrect Queries:** 3  
* **Total Queries Evaluated:** 50

| Dialogue ID (experiment\_id) | Interaction ID (interaction\_id) | Natural Language Question (intention) | Ground-Truth SQL Query (golden\_sql) |
| :---- | :---- | :---- | :---- |
| **27** | **6** | For exactly the second-country codes returned by the preceding grouped result, provide each country's name along with its border count and total border length. | SELECT B.COUNTRY2, C2.NAME AS COUNTRY\_NAME, COUNT(\*) AS BORDER\_COUNT, SUM(B.LENGTH) AS TOTAL\_LENGTH FROM MONDIAL\_BORDERS B JOIN MONDIAL\_COUNTRY C2 ON B.COUNTRY2 \= C2.CODE WHERE B.COUNTRY2 IN (SELECT P5.COUNTRY2 FROM MONDIAL\_BORDERS P5 WHERE (P5.COUNTRY1, P5.COUNTRY2) IN (SELECT P4.COUNTRY1, P4.COUNTRY2 FROM MONDIAL\_BORDERS P4 WHERE (P4.COUNTRY1, P4.COUNTRY2) IN (SELECT P3.COUNTRY1, P3.COUNTRY2 FROM MONDIAL\_BORDERS P3 WHERE (P3.COUNTRY1, P3.COUNTRY2) IN (SELECT P2.COUNTRY1, P2.COUNTRY2 FROM MONDIAL\_BORDERS P2 WHERE (P2.COUNTRY1, P2.COUNTRY2) IN (SELECT P1.COUNTRY1, P1.COUNTRY2 FROM MONDIAL\_BORDERS P1 JOIN MONDIAL\_COUNTRY C1 ON P1.COUNTRY1 \= C1.CODE JOIN MONDIAL\_COUNTRY C2P ON P1.COUNTRY2 \= C2P.CODE WHERE C1.NAME \= 'Albania') AND P2.LENGTH \>= 150\) AND P3.COUNTRY1 \= 'AL') AND P4.LENGTH BETWEEN 150 AND 300\) AND P5.COUNTRY2 IN ('GR', 'MK', 'MNE') GROUP BY P5.COUNTRY2) GROUP BY B.COUNTRY2, C2.NAME ORDER BY B.COUNTRY2 |
| **29** | **1** | Which river estuary records are located in country D? | SELECT RIVER, COUNTRY, PROVINCE, META\_REPCOL FROM MONDIAL\_GEO\_ESTUARY WHERE COUNTRY \= 'D' ORDER BY RIVER ASC, PROVINCE ASC |
| **29** | **2** | Which of the river estuary records in country D are located in the province of Sachsen-Anhalt? | SELECT RIVER, COUNTRY, PROVINCE, META\_REPCOL FROM MONDIAL\_GEO\_ESTUARY WHERE (RIVER, COUNTRY, PROVINCE) IN (SELECT RIVER, COUNTRY, PROVINCE FROM MONDIAL\_GEO\_ESTUARY WHERE COUNTRY \= 'D') AND PROVINCE \= 'Sachsen-Anhalt' ORDER BY RIVER ASC |

**Reasons for Incorrect Classifications**

* **Dialogue 27, Interaction 6:** The outer query aggregates over MONDIAL\_BORDERS B without constraining the context filters established in previous turns (i.e., B.COUNTRY1 \= 'AL'). As a result, it sums up and counts all global borders for Greece, Macedonia, and Montenegro rather than retaining the border counts and lengths from the filtered set of Albania's borders.  
* **Dialogue 29, Interactions 1 & 2:** Both queries select a non-existent column (META\_REPCOL) that does not exist in MONDIAL\_GEO\_ESTUARY or anywhere in the database schema, rendering the generated SQL invalid.

***Experiments 31-35***  
**Classification Summary**

* **Correct Queries:** 42  
* **Incorrect Queries:** 8  
* **Total Evaluated Queries:** 50

**Incorrect Ground-Truth SQL Queries**  
The following table details the 8 SQL queries classified as **Incorrect**. All 8 failures occur in Experiment 34 due to references to a non-existent column (META\_REPCOL) on the MONDIAL\_GEO\_SOURCE table.

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| ----- | ----- | ----- | ----- |
| **34** | **3** | Show the river, country, province, and representative label for exactly the Batang Hari source records whose provinces had recorded alternate names, ordered by province. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2) ORDER BY G.PROVINCE ASC, G.COUNTRY ASC, G.RIVER ASC |
| **34** | **4** | Keep only the previously listed Batang Hari source records with alternate-name matches whose representative label exactly equals their river name. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT G3.RIVER, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SOURCE G3 WHERE (G3.RIVER, G3.COUNTRY, G3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3) AND G.META\_REPCOL \= G.RIVER ORDER BY G.RIVER ASC, G.COUNTRY ASC, G.PROVINCE ASC |
| **34** | **5** | List every available historical population year and value for the provinces belonging to the previously filtered Batang Hari source records. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT G3.RIVER, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SOURCE G3 WHERE (G3.RIVER, G3.COUNTRY, G3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT G4.RIVER, G4.COUNTRY, G4.PROVINCE FROM MONDIAL\_GEO\_SOURCE G4 WHERE (G4.RIVER, G4.COUNTRY, G4.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3) AND G4.META\_REPCOL \= G4.RIVER) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, PP.YEAR, PP.POPULATION FROM MONDIAL\_GEO\_SOURCE G JOIN MONDIAL\_PROVINCE P ON G.COUNTRY \= P.COUNTRY AND G.PROVINCE \= P.NAME JOIN MONDIAL\_PROVPOPS PP ON P.COUNTRY \= PP.COUNTRY AND P.NAME \= PP.PROVINCE WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S4.RIVER, S4.COUNTRY, S4.PROVINCE FROM S4) ORDER BY PP.YEAR ASC, G.COUNTRY ASC, G.PROVINCE ASC |
| **34** | **6** | From exactly the previously matched source records that have historical population observations, retain those with Sumatera in the province name and order them by river. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT G3.RIVER, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SOURCE G3 WHERE (G3.RIVER, G3.COUNTRY, G3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT G4.RIVER, G4.COUNTRY, G4.PROVINCE FROM MONDIAL\_GEO\_SOURCE G4 WHERE (G4.RIVER, G4.COUNTRY, G4.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3) AND G4.META\_REPCOL \= G4.RIVER), S5 AS (SELECT G5.RIVER, G5.COUNTRY, G5.PROVINCE FROM MONDIAL\_GEO\_SOURCE G5 JOIN MONDIAL\_PROVINCE P5 ON G5.COUNTRY \= P5.COUNTRY AND G5.PROVINCE \= P5.NAME JOIN MONDIAL\_PROVPOPS PP5 ON P5.COUNTRY \= PP5.COUNTRY AND P5.NAME \= PP5.PROVINCE WHERE (G5.RIVER, G5.COUNTRY, G5.PROVINCE) IN (SELECT S4.RIVER, S4.COUNTRY, S4.PROVINCE FROM S4)) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S5.RIVER, S5.COUNTRY, S5.PROVINCE FROM S5) AND G.PROVINCE LIKE '%Sumatera%' ORDER BY G.RIVER ASC, G.COUNTRY ASC, G.PROVINCE ASC |
| **34** | **7** | Return the distinct country and province pairs for the previously retained source records whose province names contain Sumatera, ordered first by country and then by province. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT G3.RIVER, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SOURCE G3 WHERE (G3.RIVER, G3.COUNTRY, G3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT G4.RIVER, G4.COUNTRY, G4.PROVINCE FROM MONDIAL\_GEO\_SOURCE G4 WHERE (G4.RIVER, G4.COUNTRY, G4.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3) AND G4.META\_REPCOL \= G4.RIVER), S5 AS (SELECT G5.RIVER, G5.COUNTRY, G5.PROVINCE FROM MONDIAL\_GEO\_SOURCE G5 JOIN MONDIAL\_PROVINCE P5 ON G5.COUNTRY \= P5.COUNTRY AND G5.PROVINCE \= P5.NAME JOIN MONDIAL\_PROVPOPS PP5 ON P5.COUNTRY \= PP5.COUNTRY AND P5.NAME \= PP5.PROVINCE WHERE (G5.RIVER, G5.COUNTRY, G5.PROVINCE) IN (SELECT S4.RIVER, S4.COUNTRY, S4.PROVINCE FROM S4)), S6 AS (SELECT G6.RIVER, G6.COUNTRY, G6.PROVINCE FROM MONDIAL\_GEO\_SOURCE G6 WHERE (G6.RIVER, G6.COUNTRY, G6.PROVINCE) IN (SELECT S5.RIVER, S5.COUNTRY, S5.PROVINCE FROM S5) AND G6.PROVINCE LIKE '%Sumatera%') SELECT DISTINCT G.COUNTRY, G.PROVINCE FROM MONDIAL\_GEO\_SOURCE G WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S6.RIVER, S6.COUNTRY, S6.PROVINCE FROM S6) ORDER BY G.COUNTRY ASC, G.PROVINCE ASC |
| **34** | **8** | For exactly the source records represented by the previously listed country and province pairs, provide the province's current population, area, capital, and capital province. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT G3.RIVER, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SOURCE G3 WHERE (G3.RIVER, G3.COUNTRY, G3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT G4.RIVER, G4.COUNTRY, G4.PROVINCE FROM MONDIAL\_GEO\_SOURCE G4 WHERE (G4.RIVER, G4.COUNTRY, G4.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3) AND G4.META\_REPCOL \= G4.RIVER), S5 AS (SELECT G5.RIVER, G5.COUNTRY, G5.PROVINCE FROM MONDIAL\_GEO\_SOURCE G5 JOIN MONDIAL\_PROVINCE P5 ON G5.COUNTRY \= P5.COUNTRY AND G5.PROVINCE \= P5.NAME JOIN MONDIAL\_PROVPOPS PP5 ON P5.COUNTRY \= PP5.COUNTRY AND P5.NAME \= PP5.PROVINCE WHERE (G5.RIVER, G5.COUNTRY, G5.PROVINCE) IN (SELECT S4.RIVER, S4.COUNTRY, S4.PROVINCE FROM S4)), S6 AS (SELECT G6.RIVER, G6.COUNTRY, G6.PROVINCE FROM MONDIAL\_GEO\_SOURCE G6 WHERE (G6.RIVER, G6.COUNTRY, G6.PROVINCE) IN (SELECT S5.RIVER, S5.COUNTRY, S5.PROVINCE FROM S5) AND G6.PROVINCE LIKE '%Sumatera%'), S7 AS (SELECT G7.RIVER, G7.COUNTRY, G7.PROVINCE FROM MONDIAL\_GEO\_SOURCE G7 WHERE (G7.RIVER, G7.COUNTRY, G7.PROVINCE) IN (SELECT S6.RIVER, S6.COUNTRY, S6.PROVINCE FROM S6)) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, P.POPULATION, P.AREA, P.CAPITAL, P.CAPPROV FROM MONDIAL\_GEO\_SOURCE G JOIN MONDIAL\_PROVINCE P ON G.COUNTRY \= P.COUNTRY AND G.PROVINCE \= P.NAME WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S7.RIVER, S7.COUNTRY, S7.PROVINCE FROM S7) ORDER BY G.COUNTRY ASC, G.PROVINCE ASC, G.RIVER ASC |
| **34** | **9** | From exactly the source records whose province details were just returned, keep those with river names beginning with B and order them by province and river. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT G3.RIVER, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SOURCE G3 WHERE (G3.RIVER, G3.COUNTRY, G3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT G4.RIVER, G4.COUNTRY, G4.PROVINCE FROM MONDIAL\_GEO\_SOURCE G4 WHERE (G4.RIVER, G4.COUNTRY, G4.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3) AND G4.META\_REPCOL \= G4.RIVER), S5 AS (SELECT G5.RIVER, G5.COUNTRY, G5.PROVINCE FROM MONDIAL\_GEO\_SOURCE G5 JOIN MONDIAL\_PROVINCE P5 ON G5.COUNTRY \= P5.COUNTRY AND G5.PROVINCE \= P5.NAME JOIN MONDIAL\_PROVPOPS PP5 ON P5.COUNTRY \= PP5.COUNTRY AND P5.NAME \= PP5.PROVINCE WHERE (G5.RIVER, G5.COUNTRY, G5.PROVINCE) IN (SELECT S4.RIVER, S4.COUNTRY, S4.PROVINCE FROM S4)), S6 AS (SELECT G6.RIVER, G6.COUNTRY, G6.PROVINCE FROM MONDIAL\_GEO\_SOURCE G6 WHERE (G6.RIVER, G6.COUNTRY, G6.PROVINCE) IN (SELECT S5.RIVER, S5.COUNTRY, S5.PROVINCE FROM S5) AND G6.PROVINCE LIKE '%Sumatera%'), S7 AS (SELECT G7.RIVER, G7.COUNTRY, G7.PROVINCE FROM MONDIAL\_GEO\_SOURCE G7 WHERE (G7.RIVER, G7.COUNTRY, G7.PROVINCE) IN (SELECT S6.RIVER, S6.COUNTRY, S6.PROVINCE FROM S6)), S8 AS (SELECT G8.RIVER, G8.COUNTRY, G8.PROVINCE FROM MONDIAL\_GEO\_SOURCE G8 JOIN MONDIAL\_PROVINCE P8 ON G8.COUNTRY \= P8.COUNTRY AND G8.PROVINCE \= P8.NAME WHERE (G8.RIVER, G8.COUNTRY, G8.PROVINCE) IN (SELECT S7.RIVER, S7.COUNTRY, S7.PROVINCE FROM S7)) SELECT G.RIVER, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SOURCE G WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S8.RIVER, S8.COUNTRY, S8.PROVINCE FROM S8) AND G.RIVER LIKE 'B%' ORDER BY G.PROVINCE ASC, G.RIVER ASC, G.COUNTRY ASC |
| **34** | **10** | For exactly the remaining Batang Hari source records whose river names begin with B, list each province alias together with every available historical population year and value. | WITH S1 AS (SELECT G1.RIVER, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SOURCE G1 JOIN MONDIAL\_PROVINCE P1 ON G1.COUNTRY \= P1.COUNTRY AND G1.PROVINCE \= P1.NAME WHERE G1.RIVER \= 'Batang Hari'), S2 AS (SELECT G2.RIVER, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SOURCE G2 JOIN MONDIAL\_PROVINCE P2 ON G2.COUNTRY \= P2.COUNTRY AND G2.PROVINCE \= P2.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O2 ON P2.COUNTRY \= O2.COUNTRY AND P2.NAME \= O2.PROVINCE WHERE (G2.RIVER, G2.COUNTRY, G2.PROVINCE) IN (SELECT S1.RIVER, S1.COUNTRY, S1.PROVINCE FROM S1)), S3 AS (SELECT G3.RIVER, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SOURCE G3 WHERE (G3.RIVER, G3.COUNTRY, G3.PROVINCE) IN (SELECT S2.RIVER, S2.COUNTRY, S2.PROVINCE FROM S2)), S4 AS (SELECT G4.RIVER, G4.COUNTRY, G4.PROVINCE FROM MONDIAL\_GEO\_SOURCE G4 WHERE (G4.RIVER, G4.COUNTRY, G4.PROVINCE) IN (SELECT S3.RIVER, S3.COUNTRY, S3.PROVINCE FROM S3) AND G4.META\_REPCOL \= G4.RIVER), S5 AS (SELECT G5.RIVER, G5.COUNTRY, G5.PROVINCE FROM MONDIAL\_GEO\_SOURCE G5 JOIN MONDIAL\_PROVINCE P5 ON G5.COUNTRY \= P5.COUNTRY AND G5.PROVINCE \= P5.NAME JOIN MONDIAL\_PROVPOPS PP5 ON P5.COUNTRY \= PP5.COUNTRY AND P5.NAME \= PP5.PROVINCE WHERE (G5.RIVER, G5.COUNTRY, G5.PROVINCE) IN (SELECT S4.RIVER, S4.COUNTRY, S4.PROVINCE FROM S4)), S6 AS (SELECT G6.RIVER, G6.COUNTRY, G6.PROVINCE FROM MONDIAL\_GEO\_SOURCE G6 WHERE (G6.RIVER, G6.COUNTRY, G6.PROVINCE) IN (SELECT S5.RIVER, S5.COUNTRY, S5.PROVINCE FROM S5) AND G6.PROVINCE LIKE '%Sumatera%'), S7 AS (SELECT G7.RIVER, G7.COUNTRY, G7.PROVINCE FROM MONDIAL\_GEO\_SOURCE G7 WHERE (G7.RIVER, G7.COUNTRY, G7.PROVINCE) IN (SELECT S6.RIVER, S6.COUNTRY, S6.PROVINCE FROM S6)), S8 AS (SELECT G8.RIVER, G8.COUNTRY, G8.PROVINCE FROM MONDIAL\_GEO\_SOURCE G8 JOIN MONDIAL\_PROVINCE P8 ON G8.COUNTRY \= P8.COUNTRY AND G8.PROVINCE \= P8.NAME WHERE (G8.RIVER, G8.COUNTRY, G8.PROVINCE) IN (SELECT S7.RIVER, S7.COUNTRY, S7.PROVINCE FROM S7)), S9 AS (SELECT G9.RIVER, G9.COUNTRY, G9.PROVINCE FROM MONDIAL\_GEO\_SOURCE G9 WHERE (G9.RIVER, G9.COUNTRY, G9.PROVINCE) IN (SELECT S8.RIVER, S8.COUNTRY, S8.PROVINCE FROM S8) AND G9.RIVER LIKE 'B%') SELECT G.RIVER, G.COUNTRY, G.PROVINCE, O.OTHERNAME, PP.YEAR, PP.POPULATION FROM MONDIAL\_GEO\_SOURCE G JOIN MONDIAL\_PROVINCE P ON G.COUNTRY \= P.COUNTRY AND G.PROVINCE \= P.NAME JOIN MONDIAL\_PROVINCEOTHERNAME O ON P.COUNTRY \= O.COUNTRY AND P.NAME \= O.PROVINCE JOIN MONDIAL\_PROVPOPS PP ON P.COUNTRY \= PP.COUNTRY AND P.NAME \= PP.PROVINCE WHERE (G.RIVER, G.COUNTRY, G.PROVINCE) IN (SELECT S9.RIVER, S9.COUNTRY, S9.PROVINCE FROM S9) ORDER BY G.COUNTRY ASC, G.PROVINCE ASC, O.OTHERNAME ASC, PP.YEAR ASC |

***Experiments 36-40***  
Based on the evaluation of the 50 ground-truth SQL queries against their corresponding natural language questions and database schema, here is the classification breakdown:

* **Correct Queries:** 49  
* **Incorrect Queries:** 1  
* **Total Queries Evaluated:** 50

### Incorrect SQL Query Details

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| ----- | ----- | ----- | ----- |
| **39** | **5** | Now list those same continents alphabetically with their areas and reference labels. | SELECT MC.NAME, MC.AREA, MC.META\_REPCOL FROM MONDIAL\_CONTINENT MC WHERE (MC.NAME) IN (SELECT MC4.NAME FROM MONDIAL\_CONTINENT MC4 WHERE (MC4.NAME) IN (SELECT MC3.NAME FROM MONDIAL\_CONTINENT MC3 WHERE (MC3.NAME) IN (SELECT MC2.NAME FROM MONDIAL\_CONTINENT MC2 WHERE (MC2.NAME) IN (SELECT MC1.NAME FROM MONDIAL\_CONTINENT MC1 WHERE MC1.AREA \>= 9000000)) AND MC3.AREA \< 45000000)) ORDER BY MC.NAME ASC |

*Reason for classification:* The query selects MC.META\_REPCOL, but the column META\_REPCOL does not exist in the CONTINENT table schema, causing the query to be invalid.

***Experiments 41-45***

A total of 45 ground-truth SQL queries across 5 dialogues were inspected, resulting in **44 Correct** queries and **1 Incorrect** query.

**Classification Summary**

* **Correct:** 44  
* **Incorrect:** 1

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| 45 | 5 | Among those island-mountain results, which mountains rise above their island's recorded elevation? | SELECT DISTINCT GI.ISLAND, GI.COUNTRY, GI.PROVINCE, M.NAME AS MOUNTAIN, I.ELEVATION AS ISLAND\_ELEVATION, M.ELEVATION AS MOUNTAIN\_ELEVATION FROM MONDIAL\_GEO\_ISLAND GI JOIN MONDIAL\_ISLAND I ON GI.ISLAND \= I.NAME JOIN MONDIAL\_MOUNTAINONISLAND MI ON I.NAME \= MI.ISLAND JOIN MON |

*Note on the incorrect query:* The ground-truth SQL query in experiment 45, interaction 5 is truncated mid-statement (JOIN MON), resulting in an incomplete query and a SQL syntax error.

***Experiments 45-50***

Out of 40 evaluated ground-truth SQL queries across the dataset, 35 are **Correct** and 5 are **Incorrect**. The incorrect queries fail schema validation because they select a non-existent column (META\_REPCOL) that is not present in the database schema tables (CONTINENT or GEO\_SEA).

* **Correct Queries:** 35  
* **Incorrect Queries:** 5  
* **Total Inspected Queries:** 40

**Incorrect Ground-Truth SQL Queries**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| ----- | ----- | ----- | ----- |
| **46** | **6** | Show the name, area, and descriptive label for the continents satisfying all prior conditions, without changing which continents are included. | SELECT MC.NAME, MC.AREA, MC.META\_REPCOL FROM MONDIAL\_CONTINENT MC WHERE MC.NAME IN (SELECT MC5.NAME FROM MONDIAL\_CONTINENT MC5 WHERE MC5.NAME IN (SELECT DISTINCT MC4.NAME FROM MONDIAL\_CONTINENT MC4 JOIN MONDIAL\_ENCOMPASSES E4 ON E4.CONTINENT \= MC4.NAME JOIN MONDIAL\_COUNTRY C4 ON C4.CODE \= E4.COUNTRY WHERE MC4.NAME IN (SELECT MC3.NAME FROM MONDIAL\_CONTINENT MC3 WHERE MC3.NAME IN (SELECT MC2.NAME FROM MONDIAL\_CONTINENT MC2 WHERE MC2.NAME IN (SELECT DISTINCT MC1.NAME FROM MONDIAL\_CONTINENT MC1 JOIN MONDIAL\_ENCOMPASSES E1 ON E1.CONTINENT \= MC1.NAME WHERE E1.COUNTRY \= 'AL') AND MC2.AREA \> 9000000)) AND C4.POPULATION \> 10000000\) AND MC5.AREA \< 10000000\) ORDER BY MC.NAME ASC |
| **46** | **7** | Among the continents satisfying all previous conditions, retain only those whose area is at least 9,500,000. | SELECT MC.NAME, MC.AREA, MC.META\_REPCOL FROM MONDIAL\_CONTINENT MC WHERE MC.NAME IN (SELECT MC6.NAME FROM MONDIAL\_CONTINENT MC6 WHERE MC6.NAME IN (SELECT MC5.NAME FROM MONDIAL\_CONTINENT MC5 WHERE MC5.NAME IN (SELECT DISTINCT MC4.NAME FROM MONDIAL\_CONTINENT MC4 JOIN MONDIAL\_ENCOMPASSES E4 ON E4.CONTINENT \= MC4.NAME JOIN MONDIAL\_COUNTRY C4 ON C4.CODE \= E4.COUNTRY WHERE MC4.NAME IN (SELECT MC3.NAME FROM MONDIAL\_CONTINENT MC3 WHERE MC3.NAME IN (SELECT MC2.NAME FROM MONDIAL\_CONTINENT MC2 WHERE MC2.NAME IN (SELECT DISTINCT MC1.NAME FROM MONDIAL\_CONTINENT MC1 JOIN MONDIAL\_ENCOMPASSES E1 ON E1.CONTINENT \= MC1.NAME WHERE E1.COUNTRY \= 'AL') AND MC2.AREA \> 9000000)) AND C4.POPULATION \> 10000000\) AND MC5.AREA \< 10000000)) AND MC.AREA \>= 9500000 ORDER BY MC.NAME ASC |
| **47** | **4** | For the previously selected continents between 9 million and 20 million square kilometers, show each name, area, and stored label, ordered from largest to smallest area. | SELECT C.NAME, C.AREA, C.META\_REPCOL FROM MONDIAL\_CONTINENT C WHERE C.NAME IN (SELECT C1.NAME FROM MONDIAL\_CONTINENT C1 WHERE C1.AREA \< 20000000 AND C1.NAME IN (SELECT C2.NAME FROM MONDIAL\_CONTINENT C2 WHERE C2.AREA \> 9000000 AND C2.NAME IN (SELECT DISTINCT C3.NAME FROM MONDIAL\_CONTINENT C3 JOIN MONDIAL\_ENCOMPASSES E3 ON E3.CONTINENT \= C3.NAME JOIN MONDIAL\_COUNTRY CO3 ON CO3.CODE \= E3.COUNTRY WHERE CO3.POPULATION \> 10000000))) ORDER BY C.AREA DESC, C.NAME ASC |
| **47** | **10** | For exactly the continents that include a country with a European ethnic group after all prior restrictions, show each name, area, and stored label, ordered by increasing area. | SELECT C.NAME, C.AREA, C.META\_REPCOL FROM MONDIAL\_CONTINENT C WHERE C.NAME IN (SELECT DISTINCT C1.NAME FROM MONDIAL\_CONTINENT C1 JOIN MONDIAL\_ENCOMPASSES E1 ON E1.CONTINENT \= C1.NAME JOIN MONDIAL\_COUNTRY CO1 ON CO1.CODE \= E1.COUNTRY JOIN MONDIAL\_ETHNICGROUP EG1 ON EG1.COUNTRY \= CO1.CODE WHERE EG1.NAME \= 'European' AND C1.NAME IN (SELECT DISTINCT C2.NAME FROM MONDIAL\_CONTINENT C2 JOIN MONDIAL\_ENCOMPASSES E2 ON E2.CONTINENT \= C2.NAME JOIN MONDIAL\_COUNTRY CO2 ON CO2.CODE \= E2.COUNTRY JOIN MONDIAL\_ECONOMY EC2 ON EC2.COUNTRY \= CO2.CODE WHERE EC2.UNEMPLOYMENT \> 20 AND C2.NAME IN (SELECT DISTINCT C3.NAME FROM MONDIAL\_CONTINENT C3 JOIN MONDIAL\_ENCOMPASSES E3 ON E3.CONTINENT \= C3.NAME JOIN MONDIAL\_COUNTRY CO3 ON CO3.CODE \= E3.COUNTRY JOIN MONDIAL\_ETHNICGROUP EG3 ON EG3.COUNTRY \= CO3.CODE WHERE EG3.PERCENTAGE \> 30 AND C3.NAME IN (SELECT C4.NAME FROM MONDIAL\_CONTINENT C4 WHERE C4.AREA \<= 10000000 AND C4.NAME IN (SELECT DISTINCT C5.NAME FROM MONDIAL\_CONTINENT C5 JOIN MONDIAL\_ENCOMPASSES E5 ON E5.CONTINENT \= C5.NAME JOIN MONDIAL\_COUNTRY CO5 ON CO5.CODE \= E5.COUNTRY JOIN MONDIAL\_ECONOMY EC5 ON EC5.COUNTRY \= CO5.CODE WHERE EC5.GDP \> 200000 AND C5.NAME IN (SELECT C6.NAME FROM MONDIAL\_CONTINENT C6 WHERE C6.NAME IN (SELECT C7.NAME FROM MONDIAL\_CONTINENT C7 WHERE C7.AREA \< 20000000 AND C7.NAME IN (SELECT C8.NAME FROM MONDIAL\_CONTINENT C8 WHERE C8.AREA \> 9000000 AND C8.NAME IN (SELECT DISTINCT C9.NAME FROM MONDIAL\_CONTINENT C9 JOIN MONDIAL\_ENCOMPASSES E9 ON E9.CONTINENT \= C9.NAME JOIN MONDIAL\_COUNTRY CO9 ON CO9.CODE \= E9.COUNTRY WHERE CO9.POPULATION \> 10000000))))))))) ORDER BY C.AREA ASC, C.NAME ASC |
| **48** | **4** | For exactly the geographic records that had matching sea details, return each record's reporting label and retain only records with a known province. | SELECT G.SEA, G.COUNTRY, G.PROVINCE, G.META\_REPCOL FROM MONDIAL\_GEO\_SEA G WHERE (G.SEA, G.COUNTRY, G.PROVINCE) IN (SELECT G1.SEA, G1.COUNTRY, G1.PROVINCE FROM MONDIAL\_GEO\_SEA G1 JOIN MONDIAL\_SEA S1 ON G1.SEA \= S1.NAME WHERE (G1.SEA, G1.COUNTRY, G1.PROVINCE) IN (SELECT G2.SEA, G2.COUNTRY, G2.PROVINCE FROM MONDIAL\_GEO\_SEA G2 WHERE (G2.SEA, G2.COUNTRY, G2.PROVINCE) IN (SELECT G3.SEA, G3.COUNTRY, G3.PROVINCE FROM MONDIAL\_GEO\_SEA G3 WHERE G3.SEA \= 'Sea of Japan') AND G2.COUNTRY \= 'J')) AND G.PROVINCE IS NOT NULL ORDER BY G.PROVINCE ASC |

## 3.2 Formula 1

### 3.2.1 Formula 1 – GPT-5.5 Instant

https://chatgpt.com/share/6a737e44-9798-83e9-9304-09fa3263ea94  
I inspected the uploaded dialogue dataset and schema. The dataset contains **50 dialogues × 10 interactions \= 500 ground-truth SQL queries**. 20260731-gpt5\_6\_Formula1 (bird)\_dialogue\_dataset\_50x10.jsonJSON  
After reviewing the SQL queries against their corresponding natural-language intentions, I found:

| Classification | Number of queries |
| ----- | ----- |
| Correct | **500** |
| Incorrect | **0** |

### Incorrect SQL queries

No incorrect ground-truth SQL queries were identified.

| Dialogue ID | Interaction ID | Natural language question | Ground-truth SQL |
| ----- | ----- | ----- | ----- |
| — | — | — | — |

Overall, the ground-truth SQL queries consistently preserve the conversational context and correctly implement the intentions expressed at each interaction.

### 3.2.2 Formula 1 – Sonnet 5 Medium

https://claude.ai/share/a66467a1-178b-4768-acdb-aa055599cb9d  
Now let's run every golden SQL query against this schema to catch syntax/reference errors, and collect results for semantic review.Now let's build the final report as a markdown file with the full table.\#\# Results  
**Total queries evaluated: 500** (50 dialogues × 10 interactions)

| Classification | Count |
| ----- | ----- |
| **Correct** | 363 |
| **Incorrect** | 137 |

**Method:** I rebuilt the standard Formula 1 schema (the formula1.sql file you attached is actually missing the races, results, seasons, and status tables that most golden queries reference — I reconstructed those using the well-known Formula 1 schema that matches the FORMULA\_1\_\* table names in the queries) and executed all 500 golden\_sql statements against it in SQLite. I then heuristically screened the 363 that ran successfully for semantic mismatches (wrong aggregate function, wrong comparison operator, wrong sort direction) — every flag turned out to be a false positive on manual review, so those 363 stand as Correct.  
**Why 137 failed to execute (Incorrect):**

1. **Invalid DATE 'yyyy-mm-dd' literal syntax — 133 queries.** SQLite doesn't support the ANSI date-literal form DATE '1980-01-01' used throughout (e.g. D.DOB BETWEEN DATE '1980-01-01' AND DATE '1990-12-31'). SQLite reads DATE as a bare column name and throws a syntax error. This affects any interaction whose golden SQL filters on driver birth dates.  
2. **Parser stack overflow — 4 queries.** In the last turn(s) of a few very long dialogues, the golden SQL nests 9+ correlated subqueries (one per prior conversational turn) plus the DATE literal bug above, exceeding SQLite's parser stack depth and failing outright.

The full 137-row table (dialogue ID, interaction ID, question, golden SQL, failure reason) is in the file above — it's too long to paste inline here, but here's a sample of the pattern:

| Dialogue ID | Interaction ID | Question | Failure reason |
| ----- | ----- | ----- | ----- |
| 3 | 4 | born between January 1, 1980 and December 31, 1990 | Invalid DATE '...' literal |
| 7 | 10 | earliest/latest birth dates by nationality | Parser stack overflow |
| 9 | 3 | born between 1970 and... | Invalid DATE '...' literal |
| 17 | 10 | (deep nested chain, turn 10\) | Parser stack overflow |
| 33 | 1 | born 1980–... | Invalid DATE '...' literal |

Affected dialogues (any interaction with a DOB BETWEEN DATE ... filter, or turn 10 of dialogues 7/17/35/45): **3, 5, 7, 9, 12, 13, 14, 17, 18, 20, 21, 23, 25, 27, 32, 33, 34, 35, 36, 45**.

### 3.2.3 Formula 1 – K2.6 Instant High

https://www.kimi.com/share/19fd3be1-f482-822c-8000-0000c1aca9e3

Based on my thorough inspection of the dataset, I performed the following validation steps on all 500 queries:

1\. \*\*Syntactic validation\*\*: Checked for unbalanced parentheses, unbalanced quotes, missing SELECT clauses, and malformed SQL structures across all 500 queries. \*\*No syntax errors were found.\*\*  
2\. \*\*Schema alignment\*\*: Verified that all referenced tables and columns correspond to the provided Formula 1 schema (accounting for the \`FORMULA\_1\_\` prefix convention used throughout the dataset). All table and column references are valid.  
3\. \*\*Ordering compliance\*\*: Verified that every query requesting a specific ordering (alphabetical, chronological, highest-first, etc.) includes a corresponding \`ORDER BY\` clause. \*\*No missing ORDER BY clauses were found.\*\*  
4\. \*\*Semantic sampling\*\*: Conducted detailed line-by-line semantic review of dialogues across all experiment types (Experiments 1, 2, 10, 11, 15, 16, 17, 19, 20, 21, 22, 23, 24, and others). All sampled queries correctly:  
   \- Propagate multi-turn dialogue context through deeply nested subqueries or CTEs  
   \- Apply the correct filters (\`WHERE\`, \`HAVING\`) matching the natural language intent  
   \- Select the exact columns requested in the utterance/intention  
   \- Join tables on correct foreign keys  
   \- Use appropriate aggregation and grouping where required

\#\# Classification Summary

| Classification | Count |
| :---- | :---- |
| **\*\*Correct\*\*** | 500 |
| **\*\*Incorrect\*\*** | 0 |

\#\# Incorrect Queries Table

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| **\*(none)\*** | \*(none)\* | \*(none)\* | \*(none)\* |

\*\*Note:\*\* The dataset contains 50 dialogues × 10 interactions \= 500 total ground-truth SQL queries. Based on comprehensive syntactic and semantic analysis, all 500 queries correctly represent their corresponding natural language questions and properly maintain context across multi-turn dialogue history. No queries were found to be incorrect.

### 3.2.4 Formula 1 – Gemini 3.6 Thinking

*(Combined results of several executions due to limitation of the tool)*

***Experiments 1-5***  
**Classification Summary**

* **Correct:** 50  
* **Incorrect:** 0

**Incorrect Queries Detail**  
No incorrect ground-truth SQL queries were found in the provided dialogues. All 50 queries across the 5 dialogues accurately express the specified natural language intentions and align with the database schema.  
***Experiments 6-10***

All 50 ground-truth SQL queries across the 5 dialogues (Experiment IDs 6, 7, 8, 9, and 10\) were evaluated against their respective natural language intentions and database schemas.

* **Correct Queries:** 50  
* **Incorrect Queries:** 0

### Incorrect SQL Queries

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| *None* | *None* | *None* | *None* |

***Experiments 11-15***

Based on a systematic evaluation of all ground-truth SQL queries against their corresponding natural language user intentions and database schema, all evaluated queries accurately reflect the conversational context and context-filtering requirements of each dialogue turn.  
**Classification Summary**

* **Correct:** 60  
* **Incorrect:** 0

**Incorrect SQL Queries**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| ----- | ----- | ----- | ----- |
| *None* | *None* | *No incorrect SQL queries were found.* | *N/A* |

***Experiments 16-20***

**Classification Breakdown**

* **Correct:** 50  
* **Incorrect:** 0

**Incorrect SQL Queries**

| Dialogue ID (experiment\_id) | Interaction ID | Natural Language Question (Intention) | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| *None* | *None* | *None* | *None* |

All 50 ground-truth SQL queries across dialogues 16, 17, 18, 19, and 20 correctly represent and satisfy their corresponding natural language intentions.

***Experiments 21-25***  
After evaluating all 50 ground-truth SQL queries across the 5 dialogues (experiments 21–25) against their natural language intentions and database schema, every query accurately reflects the intent and logical context of its corresponding question.

* **Correct**: 50  
* **Incorrect**: 0

**Incorrect SQL Queries**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-truth SQL Query |
| ----- | ----- | ----- | ----- |
| *None* | *None* | *None* | *None* |

***Experiments 26-30***  
All 40 ground-truth SQL queries across the 5 dialogues (experiments 26 through 30\) were evaluated against their corresponding natural language utterances, intentions, and the database schema.

### Classification Summary

* **Correct:** 40  
* **Incorrect:** 0

### Incorrect Queries Table

| Dialogue ID (Experiment) | Interaction ID | Natural Language Question (Intention) | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| *None* | *None* | *No incorrect SQL queries were found.* | *N/A* |

***Experiments 31-35***

**Classification Summary**

* **Correct:** 50  
* **Incorrect:** 0

**Incorrect Ground-Truth SQL Queries**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-truth SQL Query |
| :---- | :---- | :---- | :---- |
| N/A | N/A | None | None |

All 50 ground-truth SQL queries across the 5 dialogues accurately reflect the corresponding natural language questions and intentions according to the database schema.

***Experiments 36-40***

**Classification Overview**

* **Correct Queries:** 38  
* **Incorrect Queries:** 2  
* **Total Queries Evaluated:** 40

**Incorrect Ground-Truth SQL Queries**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query | Reason for Incorrect Classification |
| ----- | ----- | ----- | ----- | ----- |
| **37** | **9** | For the countries in the preceding summary, count circuits with known altitude and report the maximum altitude in each country, ordered alphabetically. | WITH S1 AS (SELECT DISTINCT C1.CIRCUITID FROM FORMULA\_1\_CIRCUITS C1 JOIN FORMULA\_1\_RACES R1 ON R1.CIRCUITID \= C1.CIRCUITID WHERE R1.YEAR \= 2009 AND R1.ROUND BETWEEN 1 AND 10), S2 AS (SELECT DISTINCT C2.CIRCUITID FROM FORMULA\_1\_CIRCUITS C2 JOIN FORMULA\_1\_RACES R2 ON R2.CIRCUITID \= C2.CIRCUITID JOIN FORMULA\_1\_SEASONS S2 ON S2.YEAR \= R2.YEAR WHERE C2.CIRCUITID IN (SELECT CIRCUITID FROM S1) AND S2.YEAR BETWEEN 2010 AND 2015), S3 AS (SELECT C3.CIRCUITID FROM FORMULA\_1\_CIRCUITS C3 WHERE C3.CIRCUITID IN (SELECT CIRCUITID FROM S2) AND C3.ALT \>= 500), S4 AS (SELECT C4.CIRCUITID FROM FORMULA\_1\_CIRCUITS C4 WHERE C4.CIRCUITID IN (SELECT CIRCUITID FROM S3) AND C4.COUNTRY IN ('Mexico', 'Austria', 'Brazil')), S5 AS (SELECT DISTINCT C5.CIRCUITID FROM FORMULA\_1\_CIRCUITS C5 JOIN FORMULA\_1\_RACES R5 ON R5.CIRCUITID \= C5.CIRCUITID JOIN FORMULA\_1\_QUALIFYING Q5 ON Q5.RACEID \= R5.RACEID WHERE C5.CIRCUITID IN (SELECT CIRCUITID FROM S4) AND Q5.POSITION \= 1 AND Q5.Q3 IS NOT NULL), S6 AS (SELECT C6.CIRCUITID FROM FORMULA\_1\_CIRCUITS C6 WHERE C6.CIRCUITID IN (SELECT CIRCUITID FROM S5) AND C6.NAME LIKE '%Circuit%'), S7 AS (SELECT DISTINCT C7.CIRCUITID FROM FORMULA\_1\_CIRCUITS C7 JOIN FORMULA\_1\_RACES R7 ON R7.CIRCUITID \= C7.CIRCUITID JOIN FORMULA\_1\_PITSTOPS P7 ON P7.RACEID \= R7.RACEID WHERE C7.CIRCUITID IN (SELECT CIRCUITID FROM S6) AND P7.MILLISECONDS \< 25000), PREVIOUS\_SELECTION AS (SELECT C8.COUNTRY FROM FORMULA\_1\_CIRCUITS C8 WHERE C8.CIRCUITID IN (SELECT CIRCUITID FROM S7) GROUP BY C8.COUNTRY) SELECT C.COUNTRY, COUNT(C.CIRCUITID) AS CIRCUIT\_COUNT, MAX(C.ALT) AS MAXIMUM\_ALTITUDE FROM FORMULA\_1\_CIRCUITS C WHERE C.COUNTRY IN (SELECT COUNTRY FROM PREVIOUS\_SELECTION) AND C.CIRCUITID IN (SELECT CIRCUITID FROM S7) AND C.ALT IS NOT NULL GROUP BY C.COUNTRY ORDER BY C.COUNTRY ASC | The intention asks to summarize all circuits within the identified countries. However, the query includes AND C.CIRCUITID IN (SELECT CIRCUITID FROM S7), restricting the country-level count and maximum altitude calculation exclusively to the previously filtered subset of circuits (S7). |
| **40** | **8** | For each circuit included in the preceding win summary, count the distinct seasons in which its selected winning results occurred. | SELECT C.CIRCUITID, C.NAME AS CIRCUIT\_NAME, COUNT(DISTINCT S.YEAR) AS SEASON\_COUNT FROM FORMULA\_1\_RESULTS RES JOIN FORMULA\_1\_RACES R ON RES.RACEID \= R.RACEID JOIN FORMULA\_1\_CIRCUITS C ON R.CIRCUITID \= C.CIRCUITID JOIN FORMULA\_1\_SEASONS S ON R.YEAR \= S.YEAR JOIN FORMULA\_1\_STATUS ST ON RES.STATUSID \= ST.STATUSID WHERE (C.CIRCUITID, ST.STATUS) IN (SELECT C1.CIRCUITID, ST1.STATUS FROM FORMULA\_1\_RESULTS RES1 JOIN FORMULA\_1\_RACES R1 ON RES1.RACEID \= R1.RACEID JOIN FORMULA\_1\_CIRCUITS C1 ON R1.CIRCUITID \= C1.CIRCUITID JOIN FORMULA\_1\_STATUS ST1 ON RES1.STATUSID \= ST1.STATUSID WHERE (RES1.RESULTID) IN (SELECT RES2.RESULTID FROM FORMULA\_1\_RESULTS RES2 JOIN FORMULA\_1\_RACES R2 ON RES2.RACEID \= R2.RACEID JOIN FORMULA\_1\_CIRCUITS C2 ON R2.CIRCUITID \= C2.CIRCUITID JOIN FORMULA\_1\_STATUS ST2 ON RES2.STATUSID \= ST2.STATUSID WHERE (RES2.RESULTID) IN (SELECT RES3.RESULTID FROM FORMULA\_1\_RESULTS RES3 JOIN FORMULA\_1\_RACES R3 ON RES3.RACEID \= R3.RACEID JOIN FORMULA\_1\_CIRCUITS C3 ON R3.CIRCUITID \= C3.CIRCUITID JOIN FORMULA\_1\_SEASONS S3 ON R3.YEAR \= S3.YEAR WHERE (RES3.RACEID) IN (SELECT R4.RACEID FROM FORMULA\_1\_RACES R4 JOIN FORMULA\_1\_CIRCUITS C4 ON R4.CIRCUITID \= C4.CIRCUITID JOIN FORMULA\_1\_SEASONS S4 ON R4.YEAR \= S4.YEAR WHERE (R4.CIRCUITID) IN (SELECT C5.CIRCUITID FROM FORMULA\_1\_CIRCUITS C5 JOIN FORMULA\_1\_RACES R5 ON R5.CIRCUITID \= C5.CIRCUITID WHERE (R5.RACEID) IN (SELECT R6.RACEID FROM FORMULA\_1\_RACES R6 JOIN FORMULA\_1\_CIRCUITS C6 ON R6.CIRCUITID \= C6.CIRCUITID WHERE (R6.CIRCUITID) IN (SELECT C7.CIRCUITID FROM FORMULA\_1\_CIRCUITS C7 WHERE C7.ALT \>= 500\) AND R6.YEAR BETWEEN 2010 AND 2020\) AND C5.COUNTRY IN ('Austria', 'Belgium', 'Spain')) AND R4.YEAR BETWEEN 2010 AND 2020\) AND RES3.POSITION \= 1)))) GROUP BY C.CIRCUITID, C.NAME ORDER BY C.NAME ASC | The outer query filters by (C.CIRCUITID, ST.STATUS) pairs but fails to restrict RES entries to winning results (RES.POSITION \= 1 or filtering on specific RESULTID). As a result, non-winning race entries sharing that status and circuit are wrongly included when calculating distinct seasons. |

***Experiments 41-45***

An inspection of all 50 ground-truth SQL queries across the 5 dialogues (experiments 41 to 45\) against the natural language questions and database schema reveals the following classification:

* **Correct:** 48  
* **Incorrect:** 2

### Incorrect Ground-Truth SQL Queries

| Dialogue ID (experiment\_id) | Interaction ID (interaction\_id) | Natural Language Question (utterance) | Ground-Truth SQL (golden\_sql) | Reason for Incorrect Classification |
| :---- | :---- | :---- | :---- | :---- |
| **45** | **9** | For those nationality groups, list the drivers who had standings in race 18, along with their positions and points. | SELECT D.DRIVERID, D.FORENAME, D.SURNAME, D.NATIONALITY, DS.DRIVERSTANDINGSID, DS.POSITION, DS.POINTS, R.NAME FROM FORMULA\_1\_DRIVERS D JOIN FORMULA\_1\_DRIVERSTANDINGS DS ON DS.DRIVERID \= D.DRIVERID JOIN FORMULA\_1\_RACES R ON R.RACEID \= DS.RACEID WHERE DS.RACEID \= 18 AND D.NATIONALITY IN (SELECT D8.NATIONALITY FROM FORMULA\_1\_DRIVERS D8 WHERE D8.NATIONALITY IS NOT NULL AND D8.DRIVERID IN (SELECT D7.DRIVERID FROM FORMULA\_1\_DRIVERS D7 JOIN FORMULA\_1\_PITSTOPS P7 ON P7.DRIVERID \= D7.DRIVERID JOIN FORMULA\_1\_RACES R7 ON R7.RACEID \= P7.RACEID WHERE (P7.RACEID, P7.DRIVERID, P7.STOP) IN (SELECT P6.RACEID, P6.DRIVERID, P6.STOP FROM FORMULA\_1\_DRIVERS D6 JOIN FORMULA\_1\_PITSTOPS P6 ON P6.DRIVERID \= D6.DRIVERID JOIN FORMULA\_1\_RACES R6 ON R6.RACEID \= P6.RACEID WHERE P6.RACEID \= 841 AND D6.DRIVERID IN (SELECT D5.DRIVERID FROM FORMULA\_1\_DRIVERSTANDINGS DS5 JOIN FORMULA\_1\_RACES R5 ON R5.RACEID \= DS5.RACEID WHERE DS5.RACEID \= 18 AND D5.DRIVERID IN (SELECT D4.DRIVERID FROM FORMULA\_1\_DRIVERS D4 WHERE D4.NATIONALITY \= 'British' AND D4.DRIVERID IN (SELECT D3.DRIVERID FROM FORMULA\_1\_DRIVERS D3 JOIN FORMULA\_1\_PITSTOPS P3 ON P3.DRIVERID \= D3.DRIVERID JOIN FORMULA\_1\_RACES R3 ON R3.RACEID \= P3.RACEID WHERE (P3.RACEID, P3.DRIVERID, P3.STOP) IN (SELECT P2.RACEID, P2.DRIVERID, P2.STOP FROM FORMULA\_1\_DRIVERS D2 JOIN FORMULA\_1\_PITSTOPS P2 ON P2.DRIVERID \= D2.DRIVERID JOIN FORMULA\_1\_RACES R2 ON R2.RACEID \= P2.RACEID WHERE P2.RACEID \= 841 AND D2.DRIVERID IN (SELECT D1.DRIVERID FROM FORMULA\_1\_DRIVERS D1 JOIN FORMULA\_1\_DRIVERSTANDINGS DS1 ON DS1.DRIVERID \= D1.DRIVERID JOIN FORMULA\_1\_RACES R1 ON R1.RACEID \= DS1.RACEID WHERE DS1.RACEID \= 18 AND DS1.POSITION \<= 3))))))) GROUP BY D8.NATIONALITY) ORDER BY DS.POSITION ASC, D.DRIVERID ASC | The subquery SELECT D5.DRIVERID FROM FORMULA\_1\_DRIVERSTANDINGS DS5 JOIN FORMULA\_1\_RACES R5references alias D5 (D5.DRIVERID), but FORMULA\_1\_DRIVERS D5 was omitted from the FROM/JOIN clause, causing an invalid column/table alias reference error. |
| **45** | **10** | Finally, which race-841 pit stops belong to exactly those drivers, and what were their lap and duration? | SELECT D.DRIVERID, D.FORENAME, D.SURNAME, P.RACEID, P.STOP, P.LAP, P.DURATION, R.NAME FROM FORMULA\_1\_DRIVERS D JOIN FORMULA\_1\_PITSTOPS P ON P.DRIVERID \= D.DRIVERID JOIN FORMULA\_1\_RACES R ON R.RACEID \= P.RACEID WHERE P.RACEID \= 841 AND D.DRIVERID IN (SELECT D9.DRIVERID FROM FORMULA\_1\_DRIVERS D9 JOIN FORMULA\_1\_DRIVERSTANDINGS DS9 ON DS9.DRIVERID \= D9.DRIVERID JOIN FORMULA\_1\_RACES R9 ON R9.RACEID \= DS9.RACEID WHERE DS9.RACEID \= 18 AND D9.NATIONALITY IN (SELECT D8.NATIONALITY FROM FORMULA\_1\_DRIVERS D8 WHERE D8.NATIONALITY IS NOT NULL AND D8.DRIVERID IN (SELECT D7.DRIVERID FROM FORMULA\_1\_DRIVERS D7 JOIN FORMULA\_1\_PITSTOPS P7 ON P7.DRIVERID \= D7.DRIVERID JOIN FORMULA\_1\_RACES R7 ON R7.RACEID \= P7.RACEID WHERE (P7.RACEID, P7.DRIVERID, P7.STOP) IN (SELECT P6.RACEID, P6.DRIVERID, P6.STOP FROM FORMULA\_1\_DRIVERS D6 JOIN FORMULA\_1\_PITSTOPS P6 ON P6.DRIVERID \= D6.DRIVERID JOIN FORMULA\_1\_RACES R6 ON R6.RACEID \= P6.RACEID WHERE P6.RACEID \= 841 AND D6.DRIVERID IN (SELECT D5.DRIVERID FROM FORMULA\_1\_DRIVERSTANDINGS DS5 JOIN FORMULA\_1\_RACES R5 ON R5.RACEID \= DS5.RACEID WHERE DS5.RACEID \= 18 AND D5.DRIVERID IN (SELECT D4.DRIVERID FROM FORMULA\_1\_DRIVERS D4 WHERE D4.NATIONALITY \= 'British' AND D4.DRIVERID IN (SELECT D3.DRIVERID FROM FORMULA\_1\_DRIVERS D3 JOIN FORMULA\_1\_PITSTOPS P3 ON P3.DRIVERID \= D3.DRIVERID JOIN FORMULA\_1\_RACES R3 ON R3.RACEID \= P3.RACEID WHERE (P3.RACEID, P3.DRIVERID, P3.STOP) IN (SELECT P2.RACEID, P2.DRIVERID, P2.STOP FROM FORMULA\_1\_DRIVERS D2 JOIN FORMULA\_1\_PITSTOPS P2 ON P2.DRIVERID \= D2.DRIVERID JOIN FORMULA\_1\_RACES R2 ON R2.RACEID \= P2.RACEID WHERE P2.RACEID \= 841 AND D2.DRIVERID IN (SELECT D1.DRIVERID FROM FORMULA\_1\_DRIVERS D1 JOIN FORMULA\_1\_DRIVERSTANDINGS DS1 ON DS1.DRIVERID \= D1.DRIVERID JOIN FORMULA\_1\_RACES R1 ON R1.RACEID \= DS1.RACEID WHERE DS1.RACEID \= 18 AND DS1.POSITION \<= 3))))))) GROUP BY D8.NATIONALITY)) ORDER BY D.DRIVERID ASC, P.STOP ASC | Inherits the same syntax/alias error as Interaction 9: D5 is selected in SELECT D5.DRIVERID FROM FORMULA\_1\_DRIVERSTANDINGS DS5... without including table FORMULA\_1\_DRIVERS D5 in the FROM/JOIN clause. |

***Experiments 45-50***

**Classification Summary:**

* **Correct:** 49  
* **Incorrect:** 1

**Incorrect Ground-Truth SQL Query Details:**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-truth SQL Query |
| ----- | ----- | ----- | ----- |
| **48** | **10** | Within the exact country groups from the preceding summary, list the reference, full name, and country of the previously selected circuits whose names contain the word Circuit. | SELECT FORMULA\_1\_CIRCUITS.CIRCUITREF, FORMULA\_1\_CIRCUITS.NAME, FORMULA\_1\_CIRCUITS.COUNTRY FROM FORMULA\_1\_CIRCUITS WHERE (FORMULA\_1\_CIRCUITS.COUNTRY) IN (SELECT FORMULA\_1\_CIRCUITS.COUNTRY FROM FORMULA\_1\_CIRCUITS WHERE (FORMULA\_1\_CIRCUITS.CIRCUITID) IN (SELECT FORMULA\_1\_CIRCUITS.CIRCUITID FROM FORMULA\_1\_CIRCUITS JOIN FORMULA\_1\_RACES ON FORMULA\_1\_RACES.CIRCUITID \= FORMULA\_1\_CIRCUITS.CIRCUITID JOIN FORMULA\_1\_DRIVERSTANDINGS ON FORMULA\_1\_DRIVERSTANDINGS.RACEID \= FORMULA\_1\_RACES.RACEID WHERE (FORMULA\_1\_CIRCUITS.CIRCUITID) IN (SELECT FORMULA\_1\_CIRCUITS.CIRCUITID FROM FORMULA\_1\_CIRCUITS JOIN FORMULA\_1\_RACES ON FORMULA\_1\_RACES.CIRCUITID \= FORMULA\_1\_CIRCUITS.CIRCUITID JOIN FORMULA\_1\_LAPTIMES ON FORMULA\_1\_LAPTIMES.RACEID \= FORMULA\_1\_RACES.RACEID WHERE FORMULA\_1\_RACES.YEAR \= 2009 GROUP BY FORMULA\_1\_CIRCUITS.CIRCUITID) AND FORMULA\_1\_RACES.YEAR \= 2009 GROUP BY FORMULA\_1\_CIRCUITS.CIRCUITID) AND FORMULA\_1\_CIRCUITS.ALT IS NOT NULL GROUP BY FORMULA\_1\_CIRCUITS.COUNTRY) AND (FORMULA\_1\_CIRCUITS.CIRCUITID) IN (SELECT FORMULA\_1\_CIRCUITS.CIRCUITID FROM FORMULA\_1\_CIRCUITS JOIN FORMULA\_1\_RACES ON FORMULA\_1\_RACES.CIRCUITID \= FORMULA\_1\_CIRCUITS.CIRCUITID JOIN FORMULA\_1\_DRIVERSTANDINGS ON FORMULA\_1\_DRIVERSTANDINGS.RACEID \= FORMULA\_1\_RACES.RACEID WHERE (FORMULA\_1\_CIRCUITS.CIRCUITID) IN (SELECT FORMULA\_1\_CIRCUITS.CIRCUITID FROM FORMULA\_1\_CIRCUITS JOIN FORMULA\_1\_RACES ON FORMULA\_1\_RACES.CIRCUITID \= FORMULA\_1\_CIRCUITS.CIRCUITID JOIN FORMULA\_1\_LAPTIMES ON FORMULA\_1\_LAPTIMES.RACEID \= FORMULA\_1\_RACES.RACEID WHERE FORMULA\_1\_RACES.YEAR \= 2009 GROUP BY FORMULA\_1\_CIRCUITS.CIRCUITID) AND FORMULA\_1\_RACES.YEAR \= 2009 GROUP BY FORMULA\_1\_CIRCUITS.CIRCUITID) AND FORMULA\_1\_CIRCUITS.ALT IS NOT NULL AND FORMULA\_1\_CIRCUITS.NAME LIKE '%Circuit%' ORDER BY FORMULA\_1\_CIRCUITS.NAME ASC |

*(Note on the incorrect query: Interaction 10 in Dialogue 48 lost the historical context subqueries established in previous turns—specifically filtering for altitude \\ge 100, countries 'Spain' or 'Germany', and years 2007–2009—causing it to select all 2009 circuits and countries rather than the specific subset accumulated in the conversation history).*

## 3.3 History of Baseball

### 3.3.1 History of Baseball \- GPT-5.5 Instant

https://chatgpt.com/share/6a737ede-2118-83e9-9772-0a0cd84a176c

I inspected the dialogue dataset and its associated baseball schema. The dataset contains **11 dialogues × 10 interactions \= 110 ground-truth SQL queries**. The schema definitions are consistent with the tables and attributes referenced by the SQL queries. 20260727-gpt5\_6\_Baseball (kaggle)\_dialogue\_dataset\_11x10.jsonJSON baseball.txtTXT

**Classification Summary**

| Classification | Number of queries |
| ----- | ----- |
| Correct | **110** |
| Incorrect | **0** |

**Incorrect SQL Queries**

No incorrect ground-truth SQL queries were found.

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL |
| ----- | ----- | ----- | ----- |
| — | — | — | — |

Based on the review, every ground-truth SQL query correctly represents the corresponding natural-language intention, including the conversational context carried across interactions.

### 3.3.2 History of Baseball – Sonnet 5 Medium

https://claude.ai/share/56787bbd-08c4-43d1-94df-41a9c51a5ad6  
Files are there now. Let me inspect both.Now let's look at the dialogue JSON file.11x10 \= 110 interactions. Let me extract them all into a structured file for careful review.Now let me fetch the actual raw CSV file to check the exact award\_id values.\#\# Summary  
I reviewed all 110 dialogue interactions (11 dialogues × 10 turns) against the Lahman/"History of Baseball" schema (thehistoryofbaseball\_hall\_of\_fame, \_player, \_player\_award, \_player\_award\_vote, \_salary).  
**Classification counts:**

| Classification | Count |
| ----- | ----- |
| Correct | 100 |
| Incorrect | 10 |

**Finding:** All 10 interactions in **Dialogue 10** are incorrect. The root cause is in Interaction 1: it filters THEHISTORYOFBASEBALL\_PLAYER\_AWARD.AWARD\_ID \= 'Cy Young'. In the standard Lahman database (which this Kaggle dataset is derived from), the **award-winner** table (AwardsPlayers → player\_award) uses the literal 'Cy Young Award', not 'Cy Young' — the shorter string 'Cy Young' is only the correct literal in the **award-voting** table (AwardsSharePlayers → player\_award\_vote), which Dialogues 2 and 3 correctly use. Because Dialogue 10 queries the non-voting player\_award table with the wrong literal, the base CTE returns no matching Cy Young winners, and every subsequent turn (2–10) inherits and compounds this same flawed filter — so the whole dialogue answers a different (empty/incorrect) question than the one asked.  
All other dialogues (1, 2, 3, 4, 5, 6, 7, 8, 9, 11\) were checked turn-by-turn for correct joins, correct cumulative filtering logic across turns, correct aggregate/window function usage, and correct literal values (e.g., 'BBWAA', 'Player', 'Y', 'Most Valuable Player', 'NL', state codes) — all were found to correctly implement their stated intent.

## Incorrect Queries (Dialogue 10\)

| Dialogue | Interaction | Natural Language Question | Ground-Truth SQL |
| ----- | ----- | ----- | ----- |
| 10 | 1 | Which players won a Cy Young award from 2000 onward? | SELECT DISTINCT P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST FROM THEHISTORYOFBASEBALL\_PLAYER P JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID WHERE A.AWARD\_ID \= 'Cy Young' AND A.YEAR \>= 2000 ORDER BY P.NAME\_LAST ASC, P.NAME\_FIRST ASC, P.PLAYER\_ID ASC |
| 10 | 2 | Of those players, which ones also won an MVP award? | WITH PREVIOUS\_SELECTION AS (SELECT DISTINCT P.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_PLAYER P JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID WHERE A.AWARD\_ID \= 'Cy Young' AND A.YEAR \>= 2000\) SELECT DISTINCT P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST FROM THEHISTORYOFBASEBALL\_PLAYER P JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID WHERE P.PLAYER\_ID IN (SELECT PLAYER\_ID FROM PREVIOUS\_SELECTION) AND A.AWARD\_ID \= 'Most Valuable Player' ORDER BY P.NAME\_LAST ASC, P.NAME\_FIRST ASC, P.PLAYER\_ID ASC |
| 10 | 3 | For that smaller group, who appears in an award vote with at least one first-place vote? | Same S1/PREVIOUS\_SELECTION chain (built on AWARD\_ID \= 'Cy Young') → joins player\_award\_vote filtered on V.VOTES\_FIRST \>= 1 |
| 10 | 4 | Which of those players had a recorded salary above $1 million? | Same cascading CTE chain → joins salary filtered on S.SALARY \> 1000000 |
| 10 | 5 | Among them, who received any listed award in the same year as one of their salary records? | Same cascading CTE chain → joins player\_award and salary on matching YEAR |
| 10 | 6 | Of those players, who also has an award-vote record from a year when they won more than half of the available points? | Same cascading CTE chain → filters V.POINTS\_WON \> V.POINTS\_MAX / 2 |
| 10 | 7 | Which members of that group also have a salary record from the same year as one of those strong vote results? | Same cascading CTE chain → joins salary on S.YEAR \= V.YEAR |
| 10 | 8 | From those players, keep only those born in the USA who weighed at least 200 pounds. | Same cascading CTE chain → filters P.BIRTH\_COUNTRY \= 'USA' AND TO\_NUMBER(P.WEIGHT) \>= 200 |
| 10 | 9 | Now show those same players from heaviest to lightest, including their birth states. | Same cascading CTE chain → ORDER BY TO\_NUMBER(P.WEIGHT) DESC |
| 10 | 10 | What awards did each of those players win, and in which years and leagues? | Same cascading CTE chain → final SELECT ... FROM player JOIN player\_award |

Each row after Interaction 1 preserves the same broken AWARD\_ID \= 'Cy Young' filter inside its nested CTEs, so the entire dialogue's result set is built on a false premise (matching zero or wrong award records instead of actual Cy Young Award winners).

### 3.3.3 History of Baseball – K2.6 Instant High

//www.kimi.com/share/19fd7f8a-1782-8672-8000-00009b65a763

After carefully inspecting all 110 ground-truth SQL queries (11 experiments × 10 interactions each) against the database schema and the stated natural-language intentions, I found that \*\*106 queries are correct\*\* and \*\*4 queries are incorrect\*\*.

The incorrect queries all appear in \*\*Experiment 11\*\*, where unnecessary one-to-many joins are combined with aggregation (or a lack of deduplication) in ways that produce duplicated or inflated results.

\#\#\# Classification Counts

| Classification | Count |
| :---- | :---- |
| **\*\*Correct\*\*** | 106 |
| **\*\*Incorrect\*\*** | 4 |

\#\#\# Incorrect Queries

| Dialogue ID | Interaction ID | Natural Language Question (Intention) | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| **\*\*11\*\*** | \*\*5\*\* | For precisely those inducted award winners, identify the players with award-ballot records and total their points and first-place votes. | \`SELECT P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST, SUM(V.POINTS\_WON) AS TOTAL\_POINTS\_WON, SUM(V.VOTES\_FIRST) AS TOTAL\_FIRST\_PLACE\_VOTES FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H JOIN THEHISTORYOFBASEBALL\_PLAYER P ON H.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V ON V.PLAYER\_ID \= P.PLAYER\_ID WHERE (P.PLAYER\_ID) IN (SELECT DISTINCT P1.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H1 JOIN THEHISTORYOFBASEBALL\_PLAYER P1 ON H1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A1 ON A1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V1 ON V1.PLAYER\_ID \= P1.PLAYER\_ID WHERE (P1.PLAYER\_ID) IN (SELECT P2.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H2 JOIN THEHISTORYOFBASEBALL\_PLAYER P2 ON H2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A2 ON A2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V2 ON V2.PLAYER\_ID \= P2.PLAYER\_ID WHERE (P2.PLAYER\_ID) IN (SELECT P3.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H3 JOIN THEHISTORYOFBASEBALL\_PLAYER P3 ON H3.PLAYER\_ID \= P3.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A3 ON A3.PLAYER\_ID \= P3.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V3 ON V3.PLAYER\_ID \= P3.PLAYER\_ID WHERE (P3.PLAYER\_ID) IN (SELECT H4.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H4 WHERE H4.YEARID \= 1936 AND H4.VOTEDBY \= 'BBWAA' AND H4.CATEGORY \= 'Player' AND H4.VOTES \>= 170)) AND H2.YEARID \= 1936 AND H2.VOTEDBY \= 'BBWAA' AND H2.CATEGORY \= 'Player' AND H2.INDUCTED \= 'Y') GROUP BY P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST ORDER BY TOTAL\_POINTS\_WON DESC, P.PLAYER\_ID ASC\` |
| **\*\*11\*\*** | \*\*8\*\* | Among precisely the players in the vote-margin ranking, identify those with salary records and calculate each player's total recorded salary. | \`SELECT P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST, SUM(S.SALARY) AS TOTAL\_RECORDED\_SALARY FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H JOIN THEHISTORYOFBASEBALL\_PLAYER P ON H.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V ON V.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S ON S.PLAYER\_ID \= P.PLAYER\_ID WHERE (P.PLAYER\_ID) IN (SELECT DISTINCT P1.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H1 JOIN THEHISTORYOFBASEBALL\_PLAYER P1 ON H1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A1 ON A1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V1 ON V1.PLAYER\_ID \= P1.PLAYER\_ID WHERE (P1.PLAYER\_ID) IN (SELECT DISTINCT P2.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H2 JOIN THEHISTORYOFBASEBALL\_PLAYER P2 ON H2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A2 ON A2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V2 ON V2.PLAYER\_ID \= P2.PLAYER\_ID WHERE (P2.PLAYER\_ID) IN (SELECT P3.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H3 JOIN THEHISTORYOFBASEBALL\_PLAYER P3 ON H3.PLAYER\_ID \= P3.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A3 ON A3.PLAYER\_ID \= P3.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V3 ON V3.PLAYER\_ID \= P3.PLAYER\_ID WHERE (P3.PLAYER\_ID) IN (SELECT H4.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H4 WHERE H4.YEARID \= 1936 AND H4.VOTEDBY \= 'BBWAA' AND H4.CATEGORY \= 'Player' AND H4.VOTES \>= 170\) AND H3.YEARID \= 1936 AND H3.VOTEDBY \= 'BBWAA' AND H3.CATEGORY \= 'Player' AND H3.INDUCTED \= 'Y') AND H2.YEARID \= 1936 AND H2.VOTEDBY \= 'BBWAA' AND H2.CATEGORY \= 'Player' AND H2.BALLOTS \>= 200\) AND H1.YEARID \= 1936 AND H1.VOTEDBY \= 'BBWAA' AND H1.CATEGORY \= 'Player') GROUP BY P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST ORDER BY TOTAL\_RECORDED\_SALARY DESC, P.PLAYER\_ID ASC\` |
| **\*\*11\*\*** | \*\*9\*\* | Among precisely the previously selected players with salary records, find those who received National League awards and count those awards for each player. | \`SELECT P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST, COUNT(\*) AS NL\_AWARD\_COUNT FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H JOIN THEHISTORYOFBASEBALL\_PLAYER P ON H.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S ON S.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V ON V.PLAYER\_ID \= P.PLAYER\_ID WHERE (P.PLAYER\_ID) IN (SELECT P1.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H1 JOIN THEHISTORYOFBASEBALL\_PLAYER P1 ON H1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A1 ON A1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V1 ON V1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S1 ON S1.PLAYER\_ID \= P1.PLAYER\_ID WHERE (P1.PLAYER\_ID) IN (SELECT P2.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H2 JOIN THEHISTORYOFBASEBALL\_PLAYER P2 ON H2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A2 ON A2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V2 ON V2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S2 ON S2.PLAYER\_ID \= P2.PLAYER\_ID WHERE (P2.PLAYER\_ID) IN (SELECT H3.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H3 WHERE H3.YEARID \= 1936 AND H3.VOTEDBY \= 'BBWAA' AND H3.CATEGORY \= 'Player' AND H3.VOTES \>= 170\) AND H2.YEARID \= 1936 AND H2.VOTEDBY \= 'BBWAA' AND H2.CATEGORY \= 'Player' AND H2.INDUCTED \= 'Y' AND H2.BALLOTS \>= 200 GROUP BY P2.PLAYER\_ID) AND A1.LEAGUE\_ID \= 'NL' GROUP BY P1.PLAYER\_ID) AND A.LEAGUE\_ID \= 'NL' GROUP BY P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST ORDER BY NL\_AWARD\_COUNT DESC, P.PLAYER\_ID ASC\` |
| **\*\*11\*\*** | \*\*10\*\* | For precisely the National League award winners retained in the preceding step, report each player's total recorded salary, total award-ballot points, and 1936 Hall of Fame vote total. | \`SELECT P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST, SA.TOTAL\_RECORDED\_SALARY, VA.TOTAL\_POINTS\_WON, H.VOTES AS HALL\_OF\_FAME\_VOTES FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H JOIN THEHISTORYOFBASEBALL\_PLAYER P ON H.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID JOIN (SELECT S.PLAYER\_ID, SUM(S.SALARY) AS TOTAL\_RECORDED\_SALARY FROM THEHISTORYOFBASEBALL\_SALARY S GROUP BY S.PLAYER\_ID) SA ON SA.PLAYER\_ID \= P.PLAYER\_ID JOIN (SELECT V.PLAYER\_ID, SUM(V.POINTS\_WON) AS TOTAL\_POINTS\_WON FROM THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V GROUP BY V.PLAYER\_ID) VA ON VA.PLAYER\_ID \= P.PLAYER\_ID WHERE (P.PLAYER\_ID) IN (SELECT P1.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H1 JOIN THEHISTORYOFBASEBALL\_PLAYER P1 ON H1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S1 ON S1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A1 ON A1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V1 ON V1.PLAYER\_ID \= P1.PLAYER\_ID WHERE (P1.PLAYER\_ID) IN (SELECT P2.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H2 JOIN THEHISTORYOFBASEBALL\_PLAYER P2 ON H2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A2 ON A2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V2 ON V2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S2 ON S2.PLAYER\_ID \= P2.PLAYER\_ID WHERE (P2.PLAYER\_ID) IN (SELECT H3.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H3 WHERE H3.YEARID \= 1936 AND H3.VOTEDBY \= 'BBWAA' AND H3.CATEGORY \= 'Player' AND H3.VOTES \>= 170\) AND H2.YEARID \= 1936 AND H2.VOTEDBY \= 'BBWAA' AND H2.CATEGORY \= 'Player' AND H2.INDUCTED \= 'Y' AND H2.BALLOTS \>= 200 GROUP BY P2.PLAYER\_ID) AND A1.LEAGUE\_ID \= 'NL' GROUP BY P1.PLAYER\_ID) AND H.YEARID \= 1936 AND H.VOTEDBY \= 'BBWAA' AND H.CATEGORY \= 'Player' AND A.LEAGUE\_ID \= 'NL' ORDER BY SA.TOTAL\_RECORDED\_SALARY DESC, P.PLAYER\_ID ASC\` |

   
\#\#\# Why these four are incorrect

- \*\*Experiment 11, Interaction 5\*\*: The query aggregates \`SUM(V.POINTS\_WON)\` and \`SUM(V.VOTES\_FIRST)\` while also joining \`THEHISTORYOFBASEBALL\_PLAYER\_AWARD\` (aliased as \`A\`). Because a player can have many awards, the join creates a Cartesian product between awards and award-votes, causing each award-vote row to be duplicated once per award. The totals are therefore inflated by the number of awards each player has.  
- \*\*Experiment 11, Interaction 8\*\*: The query computes \`SUM(S.SALARY)\` while joining both \`THEHISTORYOFBASEBALL\_PLAYER\_AWARD\` and \`THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE\`. These unnecessary one-to-many joins duplicate salary rows, so the sum counts each salary record multiple times.  
- \*\*Experiment 11, Interaction 9\*\*: The query uses \`COUNT(\*)\` to count National League awards, but it also joins \`THEHISTORYOFBASEBALL\_SALARY\` and \`THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE\`. These extra joins multiply the number of rows, so \`COUNT(\*)\` returns an inflated value rather than the true award count.  
- \*\*Experiment 11, Interaction 10\*\*: The query joins \`THEHISTORYOFBASEBALL\_PLAYER\_AWARD\` (filtering on \`A.LEAGUE\_ID \= 'NL'\`) without using \`DISTINCT\` or grouping by player. Because a player can have multiple NL awards, the query returns multiple identical rows per player instead of a single comparison row per player as the question requires.

### 3.3.4 History of Baseball – Gemini 3.6 Thinking

*(Combined results of several executions due to limitation of the tool)*

***Experiments 1-5***  
**Classification Summary**

* **Correct Queries:** 49  
* **Incorrect Queries:** 1

| Dialogue ID (experiment\_id) | Interaction ID (interaction\_id) | Natural Language Question | Ground-Truth SQL Query (golden\_sql) |
| ----- | ----- | ----- | ----- |
| 5 | 10 | For those highest-paid players, show their Hall of Fame year, voting body, votes, votes needed, and induction note, ordered by vote margin. | SELECT H.PLAYER\_ID, H.YEARID, H.VOTEDBY, H.VOTES, H.NEEDED, H.NEEDED\_NOTE, (H.VOTES \- H.NEEDED) AS VOTE\_MARGIN FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H WHERE (H.PLAYER\_ID) IN (SELECT DISTINCT P9.PLAYER\_ID FROM (SELECT DISTINCT PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME) H9 JOIN THEHISTORYOFBASEBALL\_PLAYER P9 ON H9.PLAYER\_ID \= P9.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S9 ON P9.PLAYER\_ID \= S9.PLAYER\_ID WHERE (P9.PLAYER\_ID) IN (SELECT P8.PLAYER\_ID FROM (SELECT DISTINCT PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME) H8 JOIN THEHISTORYOFBASEBALL\_PLAYER P8 ON H8.PLAYER\_ID \= P8.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S8 ON P8.PLAYER\_ID \= S8.PLAYER\_ID WHERE (P8.PLAYER\_ID) IN (SELECT DISTINCT H6.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H6 JOIN THEHISTORYOFBASEBALL\_PLAYER P6 ON H6.PLAYER\_ID \= P6.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S6 ON P6.PLAYER\_ID \= S6.PLAYER\_ID WHERE H6.INDUCTED \= 'Y' AND H6.CATEGORY \= 'Player' AND (H6.PLAYER\_ID) IN (SELECT DISTINCT P2.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H2 JOIN THEHISTORYOFBASEBALL\_PLAYER P2 ON H2.PLAYER\_ID \= P2.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_SALARY S2 ON P2.PLAYER\_ID \= S2.PLAYER\_ID WHERE (P2.PLAYER\_ID) IN (SELECT H1.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H1 JOIN THEHISTORYOFBASEBALL\_PLAYER P1 ON H1.PLAYER\_ID \= P1.PLAYER\_ID WHERE H1.YEARID \= 2015 AND H1.VOTEDBY \= 'BBWAA')))) GROUP BY P8.PLAYER\_ID, P8.NAME\_FIRST, P8.NAME\_LAST) AND S |

*(Note: The query in Dialogue 5, Interaction 10 is classified as **Incorrect** because it is truncated at AND S, making it incomplete and syntactically invalid).*  
***Experiments 6-11***

Out of the 57 total ground-truth SQL queries evaluated across all dialogues, 56 queries are classified as **Correct** and 1 query is classified as **Incorrect**.

**Classification Summary**

* **Correct Queries:** 56  
* **Incorrect Queries:** 1  
* **Total Queries Evaluated:** 57

**Incorrect SQL Query Details**

| Dialogue ID | Interaction ID | Natural Language Question | Ground-Truth SQL Query |
| :---- | :---- | :---- | :---- |
| 11 | 7 | Rank precisely the players retained in the preceding step by their 1936 Hall of Fame vote margin above the required total. | SELECT DISTINCT P.PLAYER\_ID, P.NAME\_FIRST, P.NAME\_LAST, H.VOTES \- H.NEEDED AS VOTE\_MARGIN FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H JOIN THEHISTORYOFBASEBALL\_PLAYER P ON H.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A ON A.PLAYER\_ID \= P.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V ON V.PLAYER\_ID \= P.PLAYER\_ID WHERE (P.PLAYER\_ID) IN (SELECT DISTINCT P1.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H1 JOIN THEHISTORYOFBASEBALL\_PLAYER P1 ON H1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD A1 ON A1.PLAYER\_ID \= P1.PLAYER\_ID JOIN THEHISTORYOFBASEBALL\_PLAYER\_AWARD\_VOTE V1 ON V1.PLAYER\_ID \= P1.PLAYER\_ID WHERE (P1.PLAYER\_ID) IN (SELECT P2.PLAYER\_ID FROM THEHISTORYOFBASEBALL\_HALL\_OF\_FAME H2 JOIN THEHISTORYOFBASEBALL\_PLAYER P2 ON H2.PLAYER\_ID \= P2.PLAYER\_ |

*Note: Query 11.7 is classified as incorrect because the SQL code string is truncated mid-statement, resulting in an invalid syntax error.*  
