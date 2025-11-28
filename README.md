# regulatory search demo
This is a demo case for searching through regulations.

The repo contains data on:
* Data quality information for pension funds
* Solvency II regulations, guidelines, etc...

## run demo
This project uses uv for package management (for installation instructions please refer to https://docs.astral.sh/uv/getting-started/)

create .env file, insert own api keys
```
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_TEXT_EMBEDDING_SMALL_VERSION=
AZURE_TEXT_EMBEDDING_LARGE_VERSION=
AZURE_O4_MINI_VERSION=
AZURE_4O_MINI_VERSION=
AZURE_OPENAI_API_KEY_SWEDEN=
AZURE_OPENAI_ENDPOINT_SWEDEN=
GOOGLE_API_KEY=
XAI_API_KEY=
DEEPINFRA_API_KEY=
```
Either use streamlit within through uv
```
uv run python -m streamlit run regulatory-search-app.py
```
OR alternatively using VSCODE

by selecting'Python Debugger: Debug using launch.json' > 'Python Debugger: Module' 

Note: ./.vscode/launch.json is the config which invokes the module streamlit instead of python 

# version changes
## 1.0
- no hyperparameter tuning was done
such as temperature, top_k, top_p are left to default setting of provider
three files:
    - kader datakwaliteit - wet toekomst pensioen
    - pensioenregelement - Stichting Pensioenfonds DNB
    - pensioenreglement - Stichting Pensioenfonds Rockwool
- no special chunking strategy, no chunking hyperparameter tuning done default 1000 + 100 overlap
- no pdf cleaning, all left to default

### 1.1
improved formatting, added debugging and allowed user to change number of retrieved chunks

## 2.0
- improved data ingestion pipeline, for details see section 
    - extract tables
    - image parser within pdf
    - markdown to maintain structure instead of plain text
    - load pdf as whole, not per page which works helps in maintaining the overall structure through markdown
### 2.1
- improved markdown formatting
### 2.2
- removed logo images from formatting (in an attempt to make multipage tables better, did not fully succeed)

#### Notes on demo
Description: The demo was with the company to showcase the potential
Set-up: gemini-2.5-pro-preview-03-25

RAG vs CAG
A comparison between retrieval small chunks in context of text or preloading the entire documents into the context.
_Note: This is not an apple's to apple's comparison as document preprocessing of .pdf files with RAG is handled by researcher_

#### Test Setup
During development we also tested experimentally with smaller models or different model providers.
* GPT-4o-mini
* OpenAI o4-mini
* Gemini 2.5-pro-preview 
GPT-4o-mini struggled on more difficult questions requiring a multi-step solution. Additionally, less inclined to follow details in instruction, and gave an answer in most case even
if from the context the question could not be answered. I did not notice any systematic differences between OpenAI o4-mini and gemini 2.5 pro-preview.
_Note: OpenAI o3 was not considered, because of the pricing which for initial testing is too expensive_

Therefore, I chose to go with gemini 2.5 pro as it was currently scoring relatively high on all benchmarks.

The total number of input tokens were ~34K. Recent models score signficiantly better on longer context. Based on Fiction.LiveBench for Long Context Deep Comprehension.
https://fiction.live/stories/Fiction-liveBench-Mar-25-2025/oQdzQvKHw8JyXbN87. I made a small mistake in choosing the version of LLM, which seems significantly less consistent on longer context then gemeni-2.5-exp-03-25, gemini-2.5-pro-preview-03-25. The underlying assumption I made was that the between minor versions the performance on long context stayed relatively the same. According to the benchmark this is not the case.

Questions (in Dutch)
The question were sourced from a company employee and slightly adjusted by adding "voor/bij DNB pensioenfonds"
1. Wat zijn de stappen voor het uitvoeren van datakwaliteitscontroles tijdens het invaren voor DNB?
2. Wat zijn deze pensioenregelingskenmerken voor DNB pensioenfonds?
3. Hoeveel is aanspraak nabestaandenpensioen van aanspraak ouderdomspensioen bij DNB pensioenfonds? 
    - Answer = 70%
4. Hoeveel groot percentage is aanspraak wezenpensioen van aanspraak ouderdomspensioen bij DNB pensioenfonds? 
    - Answer: 20%*70% = 14%
The general answer were later also verified by the same employee

|ID|LLM|Embedding Model|API version|Method|Question 1 (basic)|Question 2 (basic)|Question 3 (medium|Question 4 (hard)|
|:----|:----|:----|:----|:----|:----|:----|:----|:----|
|1.1|gemini-2.5-pro-preview-03-25|OpenAI’s Text-embedding-3-small|2023-05-15|RAG|✔|✔|❌|❌|
|1.2|gemini-2.5-pro-preview-03-25|Google’s tekst-embedding-004|2024-03-14|RAG|✔|✔|❌|❌|
|1.3|gemini-2.5-pro-preview-03-25|OpenAI’s text-embedding-3-large|2024-02-01|RAG|✔|✔|❌|❌|
|1.4|gemini-2.5-pro-preview-03-25|gemini-embedding-exp-03-07|2025-03-07|RAG|✔|✔|✔|✔|
|1.5|gemini-2.5-pro-preview-03-25|-|-|CAG|✔|✔|✔|✔|

_Note: Configuration was number of text retrieved k=8 (chunks size 1000, with ExperimentalMarkdownSyntaxTextSplitter then RecursiveCharacterTextSplitter)_

_Note: Experiment 1.3, and 1.4 were added after the demo, as results indicated the embedding models were unable to retrieve correct information._

Based on literature research last year a big area of improved was multilingual capabilities for SOTA LLMs.

During our experiment reasoning models gave answer which at least to non-expert on pensioen regulations had satisfactory format, structure, and answer quality.

Conjencture based on experiments
1. Recent models (both LLM and embedding) have had more focus on multilingual capabilites. Therefore, recent embedding models perform better in multilingual settings especially were less common domain-specific words are used (e.g. 'nabestaandenpensioen', 'ouderdomspensioen' en 'wezenpensioen')
2. Chosing a 'fixed' chunk size of 1000 (in early RAG it used to be 300) may not be the most suitable approach for document including tables, and legal articles as the missing context may decrease contextual understanding

Future research
* Add multilingual embedding models, e.g. text-multilingual-embedding-002, Cohere-embed-multilingual-v3.0, gte-Qwen2-7B-instruct (see benchmark https://huggingface.co/spaces/mteb/leaderboard)
* Experiment with models such as GPT-4o, GPT-4.1 and Gemini 2.5 flash non-thinking to see non reasoning models performance.

### 2.3
- Added larger and modern embedding models based on https://huggingface.co/spaces/mteb/leaderboard: gemini-embedding-exp-03-07, text-embedding-3-large, and Qwen3-Embedding-8B

## 3.0 - Verifiability & UI
- added sources links within answer
- added list of sources with pdf links
- added reasoning summary
- Improved system prompt for factuality (say you do not know) && output latex for formula's

### 3.1 
- rendering of popover with markdown
- custom component for communicating document_link in popover from frontend to backend python
- changed regex for varability in LLM output for source references (e.g. Bron, Sources 1, Source 1, 2, 3)
- UI improvements

## 4.0 - Document Indexing Pipeline
- .md files solvency II, level 1 and level 2
    - major improved of markdown quality
    - removed CORRELATION_TABLES
    - removed Table of Content
    - fixed article heading misplacement for Article 84, 174, 266, 281 Solvency I
- added additional metadata
    - approximate page_number
    - short_title
- added reranker
    - instruction-aware / task_type reranker Qwen3-Reranker and Gemini Reranker
    - added UI indicators in case of extremely good or bad relevance scores of rerankers.

### 4.1 
- exposed new meta_data, such as page_numbers in UI
- consolidate pdf_to_display into one state.
- revamped the way sources are displayed
- .md files solvency II, level 1 and level 2 & guidelines
    - removal of unnecessary \n at page end and page start (interferes with recursive text splitting )
    - improved headers for guidelines files

## 5.0 - Modalities (images, tables, and equations)
- Improved data cleaning
- Specialised preprocessing of non-text modalities (images, tables, and equations)
    - Images (based on description)
        - Is image of equation? --> convert to equation
        - Is image of logo? --> remove
        - Is image summary --> remove .md markdown format
        - Add <image></image> block
    - Tables (based on size)
        - Merge multipage tables
        - Add <table></table> block
    - Equation
        - Detect equations
        - Find position of equation on page
        - Convert equation image to LaTeX format
        - Add <equation></equation>
- Chunking
    - Splitting while preserving blocks <tag></tag>
- Enrich (added to make equations and tables)
    - Generate summary of <equation> or <table>
- Embedding
    - Store enriched_chunks in vectorstore
    - Store original chunks in docstore
- Retrieval
    - Retrieve based on similarity score between enriched_chunk and query
    - Give original chunk to reranker
- UI
    - Warning for AI generated content
    - Support for markdown tables

## suggestions for future versions

### general
* Metadata filtering (on header 3 level, can be this granular through markdown text splitting)
* Add test cases to measure quality. Think about ways to measure performance
* Custom finetuned embedding model (using SentenceTransformer v4)
* Idea alternative flow: where the user can select which parts to use
* (Conjecture 2.) ParentRetriever
    * Reason CAG does on gemini 2.5 pro preview provides correct answers were convert pdf to markdown --> text-embedding-3-small (2023-05-15) --> gemini 2.5 pro preview
* (Conjecture 2.) Semantic chunking.
* trying docling 
    * (research behind it)

### retriever + storage
#### data preprocessing
##### pdf convertion
* contextual retrieval --> wfh/proposal-indexing
* Retriever may also benefit from having the context in which document placed, maybe or the header at least?
* Multimodal embedding
* adding table summaries
* Better preprocessing for tables
    * E.g. provide table summary
    * improved multipage tables support

##### chunking
* semantic chunk
* agentic chunking
* hierarchical chunking
* clustering chunking
* late chunking
* Also test with just putting the entire documents within the context of the llm, e.g. markdown, pdf, etc.
* topic clustering
* chunking based on sentence boundary detection: https://spacy.io/api/sentencizer

#### different retriever + storage
* GraphRAG (complex questions)
* BM25 (exact word matches)
* Custom finetuned vector embedding model

#### additional components in retrieval pipeline
* query rewriting
* Reranker

#### generation
* sampling: temperature, top_p, top_k
* different models: reasoning, non-reasoning

# overview of data preparation
 Examples of: 
 * MinerU, 
 * Markitdown, 
 * docling, 
 * marker, and
 * PyMuPDF4LLM.

 Libraries that I tried for convertion PDF to machine-readable format
* [PyPDF](https://pypdf.readthedocs.io/en/stable/)
* [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/)
* [Docling](https://arxiv.org/abs/2408.09869), uses a layout analysis model and TableFormer for table structure detection.

Tutorials
* [Tutorial on alternative with Multimodal LLM](https://medium.com/data-science/build-a-document-ai-pipeline-for-any-type-of-pdf-with-gemini-9221c8e143db)
* [Tutorial on text splitting](https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb)
* [Multimodal embedding models](https://github.com/langchain-ai/langchain/blob/master/cookbook/Multi_modal_RAG.ipynb)
* https://medium.com/data-science-collective/i-tried-every-pdf-parser-for-my-chat-app-only-one-worked-e20613835d27
* https://medium.com/data-science-collective/smoldocling-a-new-era-in-document-processing-3e9b044eeb4a
* https://arxiv.org/pdf/2503.11576
* [Transforming Unstructured Data](https://www.youtube.com/watch?v=_pEEJu-2KKM)
* [ParentDocumentRetriever disadvantages](https://medium.com/data-science/langchains-parent-document-retriever-revisited-1fca8791f5a0)




## PDF
Problem description:
Portable Document Format (PDF) is designed for displaying document content while preserving visual presentation accross platform, screen size or software configuration. However, the format was not designed machine-readability in mind.

*Note: A Tagged PDF may be more machine-readable, however not all PDF are tagged PDF (as far as I can see this is all behind a paywall + unsure if you can add if not original author)*

Some problems for pdfs include:
* Text flow (multi-column layout)
* Table are lines with pieces of text (no standard element)

When converting PDFs to machine-readable format two elements are particularly hard to extract consistently:
* images
* tables

Main questions:
* What format is machine-readble?
    * html, md, csv, json (or maybe even .xlsx, .png, jpeg)?
* How to chunk documents?
    * tables, law articles, images, etc.

### Image Preprocessing
Image detection:
* Images are embedded through /XObjects subtype /Image.

Image conversion:
* by OCR convert to text-based format
* by multimodal LLMs convert to text-based format
* by converting to raw bytes
    * for use with multimodal LLM 
    * OR multimodal embedding model

Subquestions
* What is an appropriate format for embedding of images?
* What is an appropriate format for using a images with an LLM?

### Tables
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

# personal notes
notes on experiment on regulatory search

## solvency II
only english dutch guidelines download instead of main one
alleen pdf geen excels
unclean scraping not verified.
some 429 status erros, added retry mechanism
improvements on guidelines scraping:
filename versions are to long (cannot save in github)
problems with github repository saving the name, for guidelines scraped as document names are to long
--> solvency-II-files/guidelines-level 3-v0.1/

 
