

# regulatory search demo


To run the demo
This project uses uv for package management (for installation instructions please refer to https://docs.astral.sh/uv/getting-started/)

create .env file, insert own api keys
```
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY_SWEDEN=
AZURE_OPENAI_ENDPOINT_SWEDEN=
GOOGLE_API_KEY=
```
Either use streamlit within through uv
```
uv run python -m streamlit run .\regulatory-search-app.py
```
OR alternatively using VSCODE

by selecting'Python Debugger: Debug using launch.json' > 'Python Debugger: Module' 

Note: ./.vscode/launch.json is the config which invokes the module streamlit instead of python 

# 1.0
- no hyperparameter tuning was done
such as temperature, top_k, top_p are left to default setting of provider
three files:
* kader datakwaliteit - wet toekomst pensioen
* pensioenregelement - Stichting Pensioenfonds DNB
* pensioenreglement - Stichting Pensioenfonds Rockwool


- no special chunking strategy, no chunking hyperparameter tuning done default 1000 + 100 overlap
- no pdf cleaning, all left to default


## 1.1 minor version
improved formatting, added debugging and allowed user to change number of retrieved chunks

# 2.0
- improved data ingestion pipeline
    - extract tables
    - image parser within pdf
    - markdown to maintain structure instead of plain text
    - load pdf as whole, not per page which works helps in maintaining the overall structure through markdown

# Suggestions for future
* Better preprocessing for tables
    * E.g. provide table summary
    * improved multipage tables support
* Metadata filtering (on header 3 level, can be this granular through markdown text splitting)
* Add test cases to measure quality. Think about ways to measure performance
* Reranker
* Custom finetuned embedding model (using SentenceTransformer v4)
* Idea alternative flow: where the user can select which parts to use
* Add BM25
* topic clustering
* GraphRAG
* query rewriting
* Agentic RAG, RAG Agent etc. (letting an llm identify when to call the vectorstore and with what query), similar goals as with query rewriting (solving the problem step-by-step). Reasoning models may be particularly well suited for this task.



# notes
notes on experiment on regulatory search

only english dutch guidelines download instead of main one

alleen pdf geen excels

unclean scraping not verified.

some 429 status erros, added retry mechanism

improvements on guidelines scraping:
filename versions are to long (cannot save in github

not saved in repository as filenames of guidelines too long
 solvency-II-files/guidelines-level 3-v0.1/


 different chunking for pdfs applied
https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb
multimodal embedding
https://github.com/langchain-ai/langchain/blob/master/cookbook/Multi_modal_RAG.ipynb
adding table summararies
Maybe also using agent RAG


Retriever may also benefit from having the context in which document placed, maybe or the header at least?

Also test with just putting the entire documents within the context of the llm

Pareto curve

semantic chunk
agentic chunking
hierarchical chunking
clustering chunking
late chunking
contextual retrieval
https://spacy.io/api/sentencizer

from langchain import hub
from langchain.pydantic_v1 import BaseModel


example proposition extraction code
def create_propositions(paragraph: str) -> list[str]:
    print(paragraph)
    propositioning_prompt = hub.pull("wfh/proposal-indexing")

    class Sentences(BaseModel):
        sentences: list[str]

    propositioning_llm = llm.with_structured_output(Sentences)

    propositioning_chain = propositioning_prompt | propositioning_llm

    sentences = propositioning_chain.invoke(paragraph)

    return sentences.sentences

props = [prop for para in text.split("\n\n") for prop in create_propositions(para)]


# overview of data preparation
 MinerU, Markitdown, docling, marker, and PyMuPDF4LLM.

 Experiment with docling, seems interesting

## approaches we have seen in the wild for data preparation into vector database

### PDF
Problem description:
Portable Document Format (PDF) is designed for displaying document content while preserving visual presentation accross platform, screen size or software configuration. However, the format was not designed machine-readability in mind.

*Note: A Tagged PDF may be more machine-readable, however not all PDF are tagged PDF (as far as I can see this is all behind a paywall + unsure if you can add if not original author)*

Some problems for pdfs include:
* Text flow (multi-column layout)
* Table are lines with pieces of text (no standard element)

When converting PDFs to machine-readable format two elements are particularly hard to extract consistently:
    * images
    * tables

Libraries for convertion PDF to machine-readable format
* [Docling](https://arxiv.org/abs/2408.09869), uses a layout analysis model and TableFormer for table structure detection.
* [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/)
* [PyPDF](https://pypdf.readthedocs.io/en/stable/)
* [Tutorial on alternative with Multimodal LLM](https://medium.com/data-science/build-a-document-ai-pipeline-for-any-type-of-pdf-with-gemini-9221c8e143db)

Main questions:
* What format is machine-readble?
    * html, md, csv, json (or maybe even .xlsx, .png, jpeg)?
* How to chunk documents?
    * tables, law articles, images, etc.

#### Image Preprocessing
Image detection:
* Images are embedded through /XObjects subtype /Image.

Image conversion:
* by OCR convert to text-based format
* by multimodal LLMs convert to text-based format
* by converting to raw bytes (e.g. by base64)

Subquestions
* What is an appropriate format for embedding of tables?
* What is an appropriate format for using a table with an LLM?

#### Tables
Table detection (or more general layout detectino):
* Table Prediction ML model
* Using multimodal LLMs to detect tables from images
* Rule-based table extraction tools

Table conversion:
* by OCR convert to text-based format
* by multimodal LLMs convert to text-based format
* Rule-based table extraction tools
* Use as is text-based format

Problems in table convertion
* multipage tables
* empty cells within table
* merged cells within table
* complex table structure
* no lines

Subquestions
* What is an appropriate format for embedding of tables?
* What is an appropriate format for using a table with an LLM?

 