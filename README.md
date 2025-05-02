

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