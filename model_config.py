# define configuration options
import os
from enum import Enum
DUMMY_CASE_DATA_QUALITY_PENSION_FUNDS_PERSIST_DIRECTORY = os.path.join("data", "vector_stores", "pension-martijn-embeddings")
SOLVENCY_II_REGULATION_SEARCH_PERSIST_DIRECTORY = os.path.join("data", "vector_stores", "solvency-II-files")

class Embedding_Model(Enum):
    # AZURE_TEXT_EMBEDDING_3_SMALL = {"display_name": "openai-text-embedding-3-small-v1", "model":"text-embedding-3-small", "data-ingestion-pipeline": "v1", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_TEXT_EMBEDDING_SMALL_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION", "persist_directory": DUMMY_CASE_DATA_QUALITY_PENSION_FUNDS_PERSIST_DIRECTORY}
    # AZURE_TEXT_EMBEDDING_3_SMALL_V2 = {"display_name": "openai-text-embedding-3-small+data-ingestion-v2.1", "data-ingestion-pipeline": "v2", "model":"text-embedding-3-small", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_TEXT_EMBEDDING_SMALL_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_V2.1", "persist_directory": DUMMY_CASE_DATA_QUALITY_PENSION_FUNDS_PERSIST_DIRECTORY}
    # AZURE_TEXT_EMBEDDING_3_LARGE_V2 = {"display_name": "openai-text-embedding-3-LARGE+data-ingestion-v2.2", "data-ingestion-pipeline": "v2", "model":"text-embedding-3-large", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_TEXT_EMBEDDING_LARGE_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_V2.3_OPENAI_3_LARGE", "persist_directory": DUMMY_CASE_DATA_QUALITY_PENSION_FUNDS_PERSIST_DIRECTORY}
    # GEMINI_EMBEDDING_EXP_03_07 = {"model": "gemini-embedding-exp-03-07", "collection_name": "DATA_QUALITY_PENSION_GEMINI_EXP", "persist_directory": PERSIST_DIRECTORY}
    # GEMINI_TEXT_EMBEDDING_004 = {"display_name": "gemini-text-embedding-004", "data-ingestion-pipeline": "v1", "model": "text-embedding-004", "api_key": os.environ["GOOGLE_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_GEMINI", "persist_directory": DUMMY_CASE_DATA_QUALITY_PENSION_FUNDS_PERSIST_DIRECTORY}
    # GEMINI_EMBEDDING_EXP_03_07 = {"display_name": "gemini-embedding-exp-03-07", "data-ingestion-pipeline": "v2", "model": "gemini-embedding-exp-03-07", "api_key": os.environ["GOOGLE_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_v2.2_GEMINI", "persist_directory": DUMMY_CASE_DATA_QUALITY_PENSION_FUNDS_PERSIST_DIRECTORY}
    # https://developers.googleblog.com/en/gemini-embedding-available-gemini-api/
    # If you are using the experimental gemini-embedding-exp-03-07, you won’t need to re-embed your contents but it will no longer be supported by the Gemini API on August 14, 2025. Legacy models will also be deprecated in the coming months:
    #     embedding-001 on August 14, 2025 and
    #     text-embedding-004 on January 14, 2026
    GEMINI_EMBEDDING_001_SOLVENCY_II = {"display_name": "gemini-embedding-001", "data-ingestion-pipeline": "v2", "model": "gemini-embedding-001", "api_key": os.environ["GOOGLE_API_KEY"], "collection_name": "GEMINI_SOLVENCY_II_V1", "persist_directory": SOLVENCY_II_REGULATION_SEARCH_PERSIST_DIRECTORY}
    QWEN_3_EMBEDDING_SOLVENCY_II = {"display_name": "Qwen3-Embedding-8B", "data-ingestion-pipeline": "v2", "model": "Qwen/Qwen3-Embedding-8B", "api_key": os.environ["DEEPINFRA_API_KEY"], "collection_name": "QWEN_SOLVENCY_II_V1", "persist_directory": SOLVENCY_II_REGULATION_SEARCH_PERSIST_DIRECTORY}
    AZURE_TEXT_EMBEDDING_3_LARGE_SOLVENCY_V2 = {"display_name": "openai-text-embedding-3-large-v2", "data-ingestion-pipeline": "v3", "model":"text-embedding-3-large", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_TEXT_EMBEDDING_LARGE_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "OPENAI_SOLVENCY_II_V2.2", "persist_directory": SOLVENCY_II_REGULATION_SEARCH_PERSIST_DIRECTORY}
    QWEN_3_EMBEDDING_SOLVENCY_II_V2 = {"display_name": "Qwen3-Embedding-8B-v2", "data-ingestion-pipeline": "v3", "model": "Qwen/Qwen3-Embedding-8B", "api_key": os.environ["DEEPINFRA_API_KEY"], "collection_name": "QWEN_SOLVENCY_II_V2.2", "persist_directory": SOLVENCY_II_REGULATION_SEARCH_PERSIST_DIRECTORY}

class Language_Model(Enum):
    AZURE_GPT_4O_MINI = {"model": "gpt-4o-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_4O_MINI_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "temperature": 0.2}
    AZURE_OPENAI_O4_MINI = {"model": "o4-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT_SWEDEN"], "api_version": os.environ["AZURE_O4_MINI_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY_SWEDEN"], "temperature": 1}
    GEMINI_25_PRO_EXP = {"model": "gemini-2.5-pro-exp-03-25", "api_key": os.environ["GOOGLE_API_KEY"], "temperature": 0.2}
    GEMINI_25_PRO_PREVIEW = {"model": "gemini-2.5-pro-preview-03-25", "api_key": os.environ["GOOGLE_API_KEY"], "temperature": 0.2}
    GEMINI_25_PRO = {"model": "gemini-2.5-pro", "api_key": os.environ["GOOGLE_API_KEY"], "temperature": 0.2}
    GROK_4 = {"model": "grok-4", "api_key": os.environ["XAI_API_KEY"], "temperature": 0.2}
    AZURE_GPT_5 = {"model": "gpt-5-chat", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT_SWEDEN"], "api_version": os.environ["AZURE_GPT_5_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY_SWEDEN"], "temperature": 0.2}

class Reranker_Model(Enum):
    QWEN_3_RERANKER = {"model": "Qwen3-Reranker-8B", "api_key": os.environ["DEEPINFRA_API_KEY"]}
    COHERE_35_RERANKER = {"model": "rerank-v3.5", "api_key": os.environ["COHERE_API_KEY"]}