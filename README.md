

# regulatory search demo


To run the demo
Install & activate conda environment
```
conda env create -f environment.yml
conda activate RegulationSearch-Demo
```
Either use streamlit within conda environment
```
streamlit run ./regulatory-search.py
```
OR in vscode use Python Debugger (accompanied in this package .vscode/launch.json)

# first version
- no hyperparameter tuning was done
such as temperature, top_k, top_p are left to default setting of provider
three files:
* kader datakwaliteit - wet toekomst pensioen
* pensioenregelement - Stichting Pensioenfonds DNB
* pensioenreglement - Stichting Pensioenfonds Rockwool


- no special chunking strategy, no chunking hyperparameter tuning done default 1000 + 100 overlap
- no pdf cleaning, all left to default

## minor version
improved formatting, added debugging and allowed user to change number of retrieved chunks

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