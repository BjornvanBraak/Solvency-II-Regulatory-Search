from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_xai import ChatXAI
from langchain_chroma import Chroma
from langchain_community.embeddings import DeepInfraEmbeddings
from model_config import Embedding_Model, Language_Model

def _create_azure_embedding_model(model, endpoint, api_version, api_key):
    return AzureOpenAIEmbeddings(
        model=model,
        azure_endpoint=endpoint,
        api_version=api_version,
        api_key=api_key
    )

def _create_gemini_embedding_model(model, api_key):
    return GoogleGenerativeAIEmbeddings(
        model=f"models/{model}", 
        google_api_key=api_key
    )

def _create_qwen3_embedding_model(model, api_key):
    return DeepInfraEmbeddings(model_id=model, deepinfra_api_token=api_key)

def _create_azure_llm(model, endpoint, api_version, api_key, temperature):
    # based on https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#list---assistants
    # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    # We generally recommend altering this or top_p but not both.
    # defaults to 1

    # default to 1 as reasoning model do not support temperature other than 1
    #https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/reasoning?tabs=python-secure%2Cpy
    # Not Supported
    # The following are currently unsupported with reasoning models:
    # temperature, top_p, presence_penalty, frequency_penalty, logprobs, top_logprobs, logit_bias, max_tokens

    if temperature:
        print("SETTING TEMPERATURE FOR MODEL, PLEASE NOT FOR O series" \
        " Only the default (1) value is supported.")

    return AzureChatOpenAI(
        model=model,
        azure_endpoint=endpoint,
        api_version=api_version,
        api_key=api_key,
        temperature=temperature
    )

def _create_gemini_llm(model, api_key, temperature):
    return ChatGoogleGenerativeAI(
        model=model, 
        api_key=api_key, 
        temperature=temperature
    )

def _create_xai_llm(model, api_key, temperature):
    return ChatXAI(
        model=model,
        api_key=api_key,
        temperature=temperature
    )

def set_up_llm(model_option: Language_Model):
    llm = None
    if model_option.name.startswith("AZURE"):
        llm = _create_azure_llm(
            model=model_option.value["model"], 
            endpoint=model_option.value["api_endpoint"],
            api_version=model_option.value["api_version"],
            api_key=model_option.value["api_key"],
            temperature=model_option.value["temperature"]
        )
    elif model_option.name.startswith("GEMINI"):
        llm = _create_gemini_llm(
            model=model_option.value["model"], 
            api_key=model_option.value["api_key"],
            temperature=model_option.value["temperature"]
        )
    elif model_option.name.startswith("GROK"):
        llm = _create_xai_llm(
            model=model_option.value["model"], 
            api_key=model_option.value["api_key"],
            temperature=model_option.value["temperature"]
        )
    else:
        raise Exception("Unknown model")
    return llm

def set_up_embedding_model(model_option: Embedding_Model):
    embedding_model = None
    if model_option.name.startswith("AZURE"):
        embedding_model = _create_azure_embedding_model(
            model=model_option.value["model"], 
            endpoint=model_option.value["api_endpoint"],
            api_version=model_option.value["api_version"],
            api_key=model_option.value["api_key"],
        )
    elif model_option.name.startswith("GEMINI"):
        embedding_model = _create_gemini_embedding_model(
            model=model_option.value["model"], 
            api_key=model_option.value["api_key"]
        )
    elif model_option.name.startswith("QWEN"):
        embedding_model = _create_qwen3_embedding_model(
            model=model_option.value["model"], 
            api_key=model_option.value["api_key"]
        )
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