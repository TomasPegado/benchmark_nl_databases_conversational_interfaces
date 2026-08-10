
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrockConverse
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

        if kwargs.get("model").startswith("o1") or kwargs.get("model").startswith("o3") or "5.6" in kwargs.get("model"):
            # constraints of o1 and o3 family
            kwargs["temperature"] = 1
            kwargs["disabled_params"] = {"parallel_tool_calls": None}
            if "max_tokens" in kwargs:
                kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
        
        if "model" in kwargs:
            kwargs["azure_deployment"] = kwargs.pop("model")
       
        final_kwargs = {**self.params, **kwargs}  
        llm = AzureChatOpenAI(**final_kwargs)

        return llm

    def get_aws_bedrock_llm(self, **kwargs):
        if "model" not in kwargs:
            kwargs["model_id"] = "deepseek.v3.2"
        else:
            kwargs["model_id"] = kwargs.pop("model")
        if "temperature" not in kwargs:
            kwargs["temperature"] = 0
        if "region_name" not in kwargs:
            kwargs["region_name"] = "us-east-2"

        return ChatBedrockConverse(**kwargs)
