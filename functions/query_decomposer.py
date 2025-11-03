from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import re
import json


class QueryDecomposer:
    """
    Decomposes possible complex natural language questions into a list of simpler questions. Returns the original question as the first element
      
    Attributes:
        llm (langchain.ChatOpenAI): object to make calls to the LLM API
        prompt_path (str): Path to question decomposition task prompt
        use_columns (boolean): Indicates whether to pass attributes (columns) of entities in the prompt to the LLM
    """
    def __init__(self,llm,prompt_path, use_keywords=False, schema_description="") -> None:
        self.llm = llm
        self.use_keywords = use_keywords
        
        self.prompt_path = prompt_path
        with open(self.prompt_path,"r") as file:
            self.prompt_template = file.read()

        self.task_prompt = self.prompt_template
        if "{schema}" in self.prompt_template and schema_description == "":
            raise ValueError("Schema description is required for this prompt template")
        elif "{schema}" in self.prompt_template:
            self.task_prompt = self.prompt_template.replace("{schema}", schema_description)
        
        list_messages =  []
        list_messages.append(("system", self.task_prompt))
        if use_keywords:
            list_messages.append(("system","{keywords}"))
        list_messages.append(("human", "{question}"))

        self.prompt_builder = ChatPromptTemplate.from_messages(list_messages)
        self.query_analyzer = LLMChain(llm=llm, prompt=self.prompt_builder, verbose=False)

    def getPromptKeywords(self,keywords):
        """
        Function to wrap keywords to prompt. The decomposer may attempt to generate a subquestion for keyword
        Args:
            keywords (str or List(str)): Keywords that indicate entities or tables present in the question
        Returns:
            String with keywords for prompt
        """
        return f"These keywords are tips on which tables and attributes are used in the question: {keywords}.\n"
    
    def decompose(self,question,keywords=None):
        """
        Performs question decomposition
        Args:
            keywords (str or List(str)): Keywords that indicate entities or tables present in the question
        Returns:
            List(str): List of decompositions of the original question. Returns the original question as the first element
        """
        sub_queries = []
        if self.use_keywords and keywords != None:
            keywords_prompt = self.getPromptKeywords(keywords)
            result_sub = self.query_analyzer.invoke({"question": question,
                                                    "keywords": keywords_prompt
                                                    })
        else:
            result_sub = self.query_analyzer.invoke({"question": question})
        template = "\[.*\]"
        output = result_sub["text"].replace("-","\-")
        list_str = re.findall(template,output)
        if len(list_str) > 0:
            list_str = list_str[0].replace("\-",'-')
            sub_queries = json.loads(list_str)
        sub_queries = [question] + sub_queries
        return sub_queries
 