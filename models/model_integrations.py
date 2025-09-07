from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_xai import ChatXAI
from langchain_chroma import Chroma
from langchain_community.embeddings import DeepInfraEmbeddings
from models.model_config import Embedding_Model, Language_Model, Reranker_Model
from models.Qwen3Reranker import Qwen3Reranker
from langchain_cohere import CohereRerank
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore
import pickle
import os

def _create_azure_embedding_model(model, endpoint, api_version, api_key):
    return AzureOpenAIEmbeddings(
        model=model,
        azure_endpoint=endpoint,
        api_version=api_version,
        api_key=api_key
    )

def _create_gemini_embedding_model(model, api_key):
    print("[INFO] CHANGED THE GOOGLEGENERATIVEAIEMBEDDINGS SOURCE CODE TO NOT LOAD THE ASYNC CLIENT WITH MAGIC_load_async_client SET")
    # NOTE: CHANGED THE SOURCE CODE OF GoogleGenerativeAIEmbeddings to not load async client if MAGIC_load_async_client = False.

    # task_type defaults are "RETRIEVAL_QUERY" for (a)embed_query and for (a)embed_document "RETRIEVAL_DOCUMENT"
    # based on documentation this is the correct task_type for the use case
    # further reading: 
    # * https://ai.google.dev/gemini-api/docs/embeddings#task-types
    # * https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/task-types#retrieve_information_from_texts
    return GoogleGenerativeAIEmbeddings(
        model=f"models/{model}", 
        google_api_key=api_key,
        MAGIC_load_async_client=False
    )

def _create_qwen3_embedding_model(model, api_key):
    # QWen 3 is capable of instruction folllowing.
    instruction = "Given a search query on Solvency II regulation, retrieve relevant passages that answer the query"

    def get_detailed_query_instruct(task_description) -> str:
        # {Instruction} {Query}<|endoftext|>
        # The paper of Qwen3 has a different format than the README.md of Qwen-3 Embedding
        # page 3 of https://arxiv.org/pdf/2506.05176
        # README of says the same as deepinfra https://github.com/QwenLM/Qwen3-Embedding
        return f'Instruct: {task_description}\nQuery:'

    # https://deepinfra.com/Qwen/Qwen3-Embedding-8B
    # FROM DOCS: 📌 Tip: We recommend that developers customize the instruct according to their specific scenarios, tasks, and languages. Our tests have shown that in most retrieval scenarios, not using an instruct on the query side can lead to a drop in retrieval performance by approximately 1% to 5%.
    query_instruction = get_detailed_query_instruct(instruction)
    # related DeepInfraEmbedding source code:
    # [in DeepInfraEmbedding]  instruction_pair = f"{self.query_instruction}{text}"
    # [in DeepInfraEmbedding]  embedding = self._embed([instruction_pair])[0]

    # we do not want any magic instructions
    return DeepInfraEmbeddings(model_id=model, deepinfra_api_token=api_key, query_instruction=query_instruction)

def _create_qwen3_reranker_model(model, api_key, top_n):
    # Qwen 3 Reranker is capable of instruction following.
    # the code is based on https://github.com/QwenLM/Qwen3-Embedding

    instruction = 'Given a search query on Solvency II regulation, retrieve relevant passages that answer the query'

    return Qwen3Reranker(model=model, api_key=api_key, top_n=top_n, query_instruction=instruction)

def _create_cohere_reranker_model(model, api_key, top_n):
    return CohereRerank(
        model=model,
        cohere_api_key=api_key,
        top_n=top_n
    )

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
        print(f"[INFO] SETTING TEMPERATURE FOR MODEL TO {temperature}. NOT SUPPORTED FOR OpenAI O-series" \
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
        temperature=temperature,
        include_thoughts=True,
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

def set_up_multivector_retriever(embedding_model_option, vectorstore, search_kwargs={"k": 3}):
    # Multivector embedding
    # NOTE: ENTIRE DOCSTORE IS SAVED AS A PICKLE FILE FOR PROOF OF CONCEPT
    # loads in list(zip(chunk_ids, chunks))
    print("working dir: ", os.getcwd())
    print(os.path.join(embedding_model_option.value["doc_persist_directory"], embedding_model_option.value["collection_name"] + ".pkl"))
    with open(os.path.join(embedding_model_option.value["doc_persist_directory"], embedding_model_option.value["collection_name"] + ".pkl"), "rb") as f:
        doc_store = pickle.load(f)

    byte_store = InMemoryByteStore()
    id_key = embedding_model_option.value["foreign_key_id"]

    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        byte_store=byte_store,
        id_key=id_key,
        search_kwargs=search_kwargs
    )

    # load docstore into memory
    retriever.docstore.mset(doc_store)
    return retriever

def set_up_reranker_model(model_option: Reranker_Model, top_n: int = 3):
    reranker_model = None
    if model_option.name.startswith("QWEN"):
        reranker_model = _create_qwen3_reranker_model(
            model=model_option.value["model"], 
            api_key=model_option.value["api_key"],
            top_n=top_n
        )
    elif model_option.name.startswith("COHERE"):
        reranker_model = _create_cohere_reranker_model(
            model=model_option.value["model"], 
            api_key=model_option.value["api_key"],
            top_n=top_n
        )
    else:
        raise Exception("Unknown model")
    return reranker_model

def load_vectorstore(model_option: Embedding_Model):
    # load the vectorstore
    print("[INFO] LOADING VECTOR STORE...")
    embedding_model = set_up_embedding_model(model_option)
    vectorstore = Chroma(model_option.value["collection_name"], embedding_model, model_option.value["persist_directory"])
    print(f"[INFO] Vectorstore loaded in with count: {vectorstore._collection.count()}")
    return vectorstore