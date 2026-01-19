# regulatory search demo
This is a demo case for searching through regulations.

The repo contains data on (located at /data):
* Data quality information for pension funds
* Solvency II level 1, level 2, and 20 level 3 documents.

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
Either use streamlit through uv
```
uv run python -m streamlit run regulatory-search-app.py
```
OR alternatively using VSCODE

by selecting'Python Debugger: Debug using launch.json' > 'Python Debugger: Module' 

Note: ./.vscode/launch.json is the config which invokes the module streamlit instead of python 

# Changelog
## 1.0
- default hyperparameters
such as temperature, top_k, top_p are left to default setting of provider
three files:
    - kader datakwaliteit - wet toekomst pensioen
    - pensioenregelement - Stichting Pensioenfonds DNB
    - pensioenreglement - Stichting Pensioenfonds Rockwool
- no special chunking strategy, default fixed window chunking 1000 + 100 overlap
- no pdf cleaning

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

The total number of input tokens were ~34K. Recent models score signficantly better on longer context. Based on Fiction.LiveBench for Long Context Deep Comprehension.
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
|1.2|gemini-2.5-pro-preview-03-25|Google’s text-embedding-004|2024-03-14|RAG|✔|✔|❌|❌|
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
_Note: Switched to different use case for Solvency II._
- added sources links within answer
- added list of sources with pdf links
- added reasoning summary
- Improved system prompt for factuality (say you do not know) && output latex for formula's

### 3.1 
- rendering of popover with markdown
- custom component for communicating document_link in popover from frontend to backend python
- changed regex for variability in LLM output for source references (e.g. Bron, Sources 1, Source 1, 2, 3)
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
