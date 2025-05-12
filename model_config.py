# define configuration options
import os
from enum import Enum
PERSIST_DIRECTORY = os.path.join("data", "vector_stores", "pension-martijn-embeddings")

class Embedding_Model(Enum):
    AZURE_TEXT_EMBEDDING_3_SMALL = {"display_name": "openai-text-embedding-3-small-v1", "model":"text-embedding-3-small", "data-ingestion-pipeline": "v1", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_TEXT_EMBEDDING_SMALL_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION", "persist_directory": PERSIST_DIRECTORY}
    AZURE_TEXT_EMBEDDING_3_SMALL_V2 = {"display_name": "openai-text-embedding-3-small+data-ingestion-v2.1", "data-ingestion-pipeline": "v2", "model":"text-embedding-3-small", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_TEXT_EMBEDDING_SMALL_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_V2.1", "persist_directory": PERSIST_DIRECTORY}
    # GEMINI_EMBEDDING_EXP_03_07 = {"model": "gemini-embedding-exp-03-07", "collection_name": "DATA_QUALITY_PENSION_GEMINI_EXP", "persist_directory": PERSIST_DIRECTORY}
    GEMINI_TEXT_EMBEDDING_004 = {"display_name": "gemini-text-embedding-004", "data-ingestion-pipeline": "v1", "model": "text-embedding-004", "api_key": os.environ["GOOGLE_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_GEMINI", "persist_directory": PERSIST_DIRECTORY}
    GEMINI_EMBEDDING_EXP_03_07 = {"display_name": "gemini-embedding-exp-03-07", "data-ingestion-pipeline": "v2", "model": "gemini-embedding-exp-03-07", "api_key": os.environ["GOOGLE_API_KEY"], "collection_name": "DATA_QUALITY_PENSION_v2.2_GEMINI", "persist_directory": PERSIST_DIRECTORY}

class Language_Model(Enum):
    AZURE_GPT_4O_MINI = {"model": "gpt-4o-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"], "api_version": os.environ["AZURE_4O_MINI_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY"], "temperature": 0.2}
    AZURE_OPENAI_O4_MINI = {"model": "o4-mini", "api_endpoint": os.environ["AZURE_OPENAI_ENDPOINT_SWEDEN"], "api_version": os.environ["AZURE_O4_MINI_VERSION"], "api_key": os.environ["AZURE_OPENAI_API_KEY_SWEDEN"], "temperature": 1}
    GEMINI_25_PRO_EXP = {"model": "gemini-2.5-pro-exp-03-25", "api_key": os.environ["GOOGLE_API_KEY"], "temperature": 0.2}
    GEMINI_25_PRO_PREVIEW = {"model": "gemini-2.5-pro-preview-03-25", "api_key": os.environ["GOOGLE_API_KEY"], "temperature": 0.2}