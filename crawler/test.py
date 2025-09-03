import requests
import os
response = requests.get("https://www.eiopa.europa.eu/publications/joint-guidelines-oversight-cooperation-and-information-exchange-between-esas-and-competent_en")

file_data = requests.get("https://www.eiopa.europa.eu/document/download/243b423e-404d-4a4d-bd2b-b7a0fa4779ed_en?filename=Joint-guidelines-on-oversight-cooperation-and-information-exchange-between-the-ESAs-and-the-competent-authorities-under-DORA_EN.pdf")

PROGRAM_FILE_PATH = os.path.dirname(__file__)
with open(os.path.join(PROGRAM_FILE_PATH, 'test', "test"), "wb") as file:
                        file.write(file_data.content)
