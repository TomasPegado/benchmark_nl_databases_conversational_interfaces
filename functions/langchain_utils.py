import openai
import os
import time
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.callbacks import get_openai_callback
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import time

import functions.gptconfig as gptconfig

def get_llm(temperature=0, n=1, max_tokens=400, model=gptconfig.MODEL_4O, logprobs=None, **model_kwargs):
    
    params = {
        "temperature": temperature,
        "model": model, 
        "n": n, 
        "openai_api_key":  gptconfig.OPENAI_API_KEY,  
        "openai_api_version":  gptconfig.OPENAI_API_VERSION,
        # "azure_endpoint": config['OPENAI']['OPENAI_API_BASE'],
        "azure_endpoint": gptconfig.AZURE_OPENAI_BASE_URL,
        
    }

    if logprobs is not None:
        params["logprobs"] = logprobs

    if model.startswith("o1") or model.startswith("o3"):
        params["temperature"] = 1
        params["max_completion_tokens"] = 4000
    else:
        params["max_tokens"] = max_tokens
            
    llm = AzureChatOpenAI(
       **params,
       **model_kwargs
    )

    return llm


def get_embeddings_model(model=gptconfig.MODEL_EMBEDDING):

    embeddings = AzureOpenAIEmbeddings(
        model=model,
        openai_api_key= gptconfig.OPENAI_API_KEY, 
        openai_api_version= gptconfig.OPENAI_API_VERSION,
        # azure_endpoint=config['OPENAI']['OPENAI_API_BASE'],
        azure_endpoint=gptconfig.AZURE_OPENAI_BASE_URL
    )
    return embeddings


# def get_llm(temperature=0, max_tokens=50, n=1, model="gpt-3.5-turbo"):
#     apikey = os.environ["OPENAI_API_KEY"]
#     openai.api_key = apikey
#     return ChatOpenAI(temperature=temperature, model=model, max_tokens=max_tokens, n=n)

def get_embeddings(text, model=gptconfig.MODEL_EMBEDDING, delay=None):

    embeddings = get_embeddings_model()
    
    if delay is not None:
        # Sleep for the delay
        time.sleep(delay)

    return embeddings.embed_query(text)

def get_openai_response_msg(model, messages, max_tokens=400, temperature=0, delay=None, **kwargs):
    
    llm =  get_llm(temperature=temperature, max_tokens=max_tokens, model=model, model_kwargs=kwargs)
    messages = convert_chat_models_to_langchain(messages, model)
    result={}
    
    with get_openai_callback() as cb:
        response = llm.invoke(messages)
        result['content'] = response.content
        result['usage'] = cb
        result['response'] = response

    if delay is not None:
        # Sleep for the delay
        time.sleep(delay)

   

    return result

# def get_openai_o3_response_msg(text, model=gptconfig.MODEL_o3_MINI, max_tokens=400, temperature=0, delay=None, **kwargs):

#     llm =  get_llm(temperature=temperature, max_tokens=max_tokens, model=model, model_kwargs=kwargs)
#     response = llm.invoke(text)
#     if delay is not None:
#         # Sleep for the delay
#         time.sleep(delay)

#     return response
    
def convert_chat_models_to_langchain(messages, model):
    langchain_chat_models = []
    for m in messages:
        if type(m)==dict:
            if m['role'].lower() == 'system':
                if model.startswith("o3"):
                    langchain_chat_models.append( HumanMessage(content=m['content']))
                else:
                    langchain_chat_models.append( SystemMessage(content=m['content']))
            elif m['role'].lower() == 'assistant':
                langchain_chat_models.append( AIMessage(content=m['content']))
            elif m['role'].lower() == 'user':
                langchain_chat_models.append( HumanMessage(content=m['content']))
        else:
            langchain_chat_models = messages
            break
    
    return langchain_chat_models