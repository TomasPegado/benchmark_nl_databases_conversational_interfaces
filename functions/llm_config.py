
from langchain_openai import AzureChatOpenAI
import httpx

class LLMConfig:
    def __init__(self, provider: str = "azure", environment: str= "tec"):

        if environment == "tec":
            from functions.gptconfig import OPENAI_API_KEY, OPENAI_API_VERSION, AZURE_OPENAI_BASE_URL, MODEL_4O
            self.http_client = None
            self.params = {
                "azure_endpoint": AZURE_OPENAI_BASE_URL
            }
        
        else:
            raise ValueError(f"Enter a valid value for the 'enviroment' attribute: ['tec']")

        self.params["openai_api_key"] = OPENAI_API_KEY
        self.params["openai_api_version"] = OPENAI_API_VERSION
          
        self.environment = environment
        self.DEFAULT_AZURE_MODEL = MODEL_4O
        self.provider = provider

    def get_llm(self, **kwargs):
        if self.provider == "azure":
            return self.get_azure_llm(**kwargs)
        elif self.provider == "aws_bedrock" and self.environment == "tec":
            return self.get_aws_bedrock_llm(**kwargs)
        else:
            raise ValueError(f"Provider {self.provider} not supported")

    def get_azure_llm(self, **kwargs):        

        if "model" not in kwargs: kwargs["model"] = self.DEFAULT_AZURE_MODEL

        if kwargs.get("model").startswith("o1") or kwargs.get("model").startswith("o3"):
            # constraints of o1 and o3 family
            kwargs["temperature"] = 1
            kwargs["disabled_params"] = {"parallel_tool_calls": None}
            
        return AzureChatOpenAI(**self.params, **kwargs)

    def get_aws_bedrock_llm(self, **kwargs):
        pass
