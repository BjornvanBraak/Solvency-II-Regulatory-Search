import os
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from enum import Enum

PERSIST_DIRECTORY = os.path.join("data", "vector_stores", "pension-martijn-embeddings")

# define configuration options
class Embedding_Model(Enum):
    AZURE_TEXT_EMBEDDING_3_SMALL = {"model":"text-embedding-3-small", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION", "persist_directory": PERSIST_DIRECTORY}
    # GEMINI_EMBEDDING_EXP_03_07 = {"model": "gemini-embedding-exp-03-07", "collection_name": "DATA_QUALITY_PENSION_GEMINI_EXP", "persist_directory": PERSIST_DIRECTORY}
    GEMINI_TEXT_EMBEDDING_004 = {"model": "text-embedding-004", "collection_name": "DATA_QUALITY_PENSION_GEMINI", "persist_directory": PERSIST_DIRECTORY}

class Language_Model(Enum):
    AZURE_GPT_4O_MINI = {"model": "gpt-4o-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "temperature": 0.2}
    AZURE_OPENAI_O4_MINI = {"model": "o4-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT_SWEDEN"], "api_key": os.environ["AZURE_OPENAI_API_KEY_SWEDEN"]}
    GEMINI_25_PRO_EXP = {"model": "gemini-2.5-pro-exp-03-25"}

def _create_azure_embedding_model(model_options: Embedding_Model):
    endpoint = model_options.value["api_endpoint"] #or os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = model_options.value["api_key"] #or os.environ["AZURE_OPENAI_API_KEY"]
    return AzureOpenAIEmbeddings(
        model=model_options.value["model"],
        azure_endpoint=endpoint,
        api_version="2023-05-15",
        api_key=api_key
    )

def _create_gemini_embedding_model(model):
    return GoogleGenerativeAIEmbeddings(
        model=f"models/{model}", 
        google_api_key=os.environ["GOOGLE_API_KEY"]
    )

def _create_azure_llm(model_options: Language_Model):
    # based on https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#list---assistants
    # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    # We generally recommend altering this or top_p but not both.
    # defaults to 1

    # default to 1 as reasoning model do not support temperature other than 1
    #https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/reasoning?tabs=python-secure%2Cpy
    # Not Supported
    # The following are currently unsupported with reasoning models:
    # temperature, top_p, presence_penalty, frequency_penalty, logprobs, top_logprobs, logit_bias, max_tokens
    temperature = 1
    if "temperature" in model_options.value:
        print("SETTING TEMPERATURE FOR MODEL, PLEASE NOT FOR O series" \
        " Only the default (1) value is supported.")
        temperature = model_options.value["temperature"]


    print("temperature setting is changed")
    endpoint = model_options.value["api_endpoint"] #or os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = model_options.value["api_key"] #or os.environ["AZURE_OPENAI_API_KEY"]
    return AzureChatOpenAI(
        model=model_options.value["model"],
        azure_endpoint=endpoint,
        api_version="2025-01-01-preview",
        api_key=api_key,
        temperature=temperature
    )

def _create_gemini_llm(model):
    return ChatGoogleGenerativeAI(
        model=model, 
        api_key=os.getenv("GOOGLE_API_KEY"), 
        temperature=0.2
    )

def set_up_llm(model_option: Language_Model):
    llm = None
    if model_option.name.startswith("AZURE"):
        llm = _create_azure_llm(model_option)
    elif model_option.name.startswith("GEMINI"):
        llm = _create_gemini_llm(model_option.value["model"])
    else:
        raise Exception("Unknown model")
    return llm

def set_up_embedding_model(model_option: Embedding_Model):
    embedding_model = None
    if model_option.name.startswith("AZURE"):
        embedding_model = _create_azure_embedding_model(model_option)
    elif model_option.name.startswith("GEMINI"):
        embedding_model = _create_gemini_embedding_model(model_option.value["model"])
    else:
        raise Exception("Unknown model")
    return embedding_model

def load_vectorstore(model_option: Embedding_Model):
    # load the vectorstore
    print("LOADING VECTOR STORE...")
    embedding_model = set_up_embedding_model(model_option)
    vectorstore = Chroma(model_option.value["collection_name"], embedding_model, model_option.value["persist_directory"])
    print(f"Vectorstore loaded in with count: {vectorstore._collection.count()}")
    return vectorstore