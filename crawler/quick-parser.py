import re
import json
import os

PROGRAM_FILE_PATH = os.path.dirname(__file__)

try:
    with open(os.path.join(PROGRAM_FILE_PATH, 'entries/feed-entries.txt'), 'r', encoding='utf-8') as file:
        text = file.read()
except FileNotFoundError:
    raise Exception("File not found. Please check the filepath.")

# This is the pattern we are looking for.
url_pattern = r"\"https://www.eiopa.europa.eu/publications/.*\""

# Find all the urls that match the pattern in the text.
urls = re.findall(url_pattern, text)

for idx, url in enumerate(urls):
    urls[idx] = re.sub(r"\"", "", url) 

# print(urls)
print(len(urls))

# Remove duplicates
deduplicated_urls = list(dict.fromkeys(urls))

print(len(deduplicated_urls))

with open(os.path.join(PROGRAM_FILE_PATH, 'intermediate_results/dedeuplicated_urls.json'), "w") as file:
    file.write(json.dumps(deduplicated_urls))