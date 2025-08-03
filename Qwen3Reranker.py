import requests
import json
from langchain_core.documents.base import Document
from langchain_core.documents import BaseDocumentCompressor
from typing import Any, Dict, List, Optional, Sequence, Union
from langchain_core.callbacks.manager import Callbacks
from copy import deepcopy
from langchain_core.utils import secret_from_env
from pydantic import ConfigDict, Field, SecretStr, model_validator

class Qwen3Reranker(BaseDocumentCompressor):
    model: Optional[str] = None
    """Model to use for reranking. Mandatory to specify the model name."""

    top_n: Optional[int] = 3
    """Number of documents to return."""

    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("COHERE_API_KEY", default=None)
    )
    """DeepInfra API key. Must be specified directly"""

    def __init__(self, model, api_key, top_n):
        super().__init__()
        self.model = model
        self.api_key = api_key
        self.top_n = top_n

    """
    Example output: [{'index': 0, 'relevance_score': 0.86413884},
    {'index': 2, 'relevance_score': 0.15784983},
    {'index': 1, 'relevance_score': 0.01999476}]
    """
    def rerank(self, documents: Sequence[Union[str, Document, dict]],
        query: str,
        top_n: Optional[int] = -1)  -> List[Dict[str, Any]]:
        # max chunks size of 32,768 tokens

        # Define the URL
        url = f"https://api.deepinfra.com/v1/inference/Qwen/{self.model}"

        # Define the headers
        headers = {
            "Authorization": f"bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # query = "What is the capital of United States of America?"
        # documents = ["The capital of USA is Washington DC.", "Pototoes are a type of vegetable.", "The capital of France is Paris."]
        queries = [query] * len(documents)

        page_contents = []

        # print(f"Documents: {documents}")
        for document in documents:
            if isinstance(document, Document):
                page_contents.append(document.page_content)
            elif isinstance(document, str):
                page_contents.append(document)
            else:
                raise Exception("Not Implemented: should be of type langchain Document")

        # Define the data payload
        data = {
            "queries": queries,
            "documents": page_contents,
        }

        # Make the POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Print the response from the server
        # print(response.json())

        reranked_format = []

        scores = response.json()['scores']


        top_n = top_n if (top_n is None or top_n > 0) else self.top_n

        indexed_scores = list(enumerate(scores))

        sorted_scores = sorted(indexed_scores, key=lambda item: item[1], reverse=True)

        top_n_slice = sorted_scores[:top_n]

        # print(f"top {self.top_n}")
        # print(f"Top {top_n} reranked documents: {top_n_slice}")

        reranked_format = [
            {
                "index": original_index,
                "relevance_score": score
            }
            for original_index, score in top_n_slice
        ]

        # print(f"Reranked format: {reranked_format}")
        return reranked_format
    
    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Compress documents using Deepinfra Qwen-3's rerank API.

        Args:
            documents: A sequence of documents to compress.
            query: The query to use for compressing the documents.
            callbacks: Callbacks to run during the compression process.

        Returns:
            A sequence of compressed documents.
        """
        compressed = []
        for res in self.rerank(documents, query):
            doc = documents[res["index"]]
            doc_copy = Document(doc.page_content, metadata=deepcopy(doc.metadata))
            doc_copy.metadata["relevance_score"] = res["relevance_score"]
            compressed.append(doc_copy)
        return compressed