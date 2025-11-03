#import openai
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import pathlib
pyfile = pathlib.Path(__file__).parent.resolve()


##### CONFIF #######
AZURE_OPENAI_BASE_URL = os.environ["AZURE_OPENAI_BASE_URL"]
OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
OPENAI_API_VERSION = os.environ["AZURE_OPENAI_API_VERSION"]

###### MODELS #########
MODEL_35_TURBO = 'gpt-35-turbo'
MODEL_4O = 'gpt-4o'
MODEL_EMBEDDING = 'text-embedding-ada-002'
MODEL_O1_MINI = 'o1-mini'
MODEL_O3_MINI = 'o3-mini'




