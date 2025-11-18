import time
import httpx
import functions.gptconfig as gptconfig
from openai import AzureOpenAI


def get_openai_function_call(
    model,
    messages,
    functions=[],
    function_call="auto",
    temperature=0,
    max_tokens=50,
    delay=None,
    **kwargs
):

    response = get_client().chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        #top_p=gptconfig.top_p,
        #frequency_penalty=0,
        #presence_penalty=0,
        stop=None,
        n=1,
        max_tokens=max_tokens,
        functions=functions,
        function_call=function_call,
        **kwargs
    )
    if delay is not None:
        # Sleep for the delay
        time.sleep(delay)
    message={}
    message["content"] = response.choices[0].message.content
    message["usage"] = response.usage
    return message


def get_openai_response_msg(model, messages, max_tokens=400, temperature=0, delay=None, **kwargs):
    response = get_client().chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        #frequency_penalty=0,
        #presence_penalty=0,
        **kwargs
    )
    if delay is not None:
        # Sleep for the delay
        time.sleep(delay)

    message={}
    message["content"] = response.choices[0].message.content
    message["usage"] = response.usage
    return message


def get_openai_response(model, prompt, q, max_tokens=400, temperature=0, delay=None):
    return get_openai_response_msg( model,
        [{"role": "system", "content": prompt}, {"role": "user", "content": q}],
        max_tokens,
        temperature,
        delay,
    )


def get_embeddings(text, model=gptconfig.MODEL_EMBEDDING):
    response = get_client().embeddings.create(input=text, model=model)
    return response.data[0].embedding
    #embeddings = response.data[0].embedding 
    #return np.array(embeddings)

def get_client()->AzureOpenAI:
    http_client = httpx.Client(verify=gptconfig.CA_CERTIFICATE)

    client = AzureOpenAI(
        api_key= gptconfig.OPENAI_API_KEY,  
        api_version= gptconfig.OPENAI_API_VERSION,
        # azure_endpoint=config['OPENAI']['OPENAI_API_BASE'],
        base_url=gptconfig.AZURE_OPENAI_BASE_URL,
        http_client=http_client
    )

    return client
