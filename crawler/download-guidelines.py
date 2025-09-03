import requests
from bs4 import BeautifulSoup
import os
import time
import json

PROGRAM_FILE_PATH = os.path.dirname(__file__)
with open(os.path.join(PROGRAM_FILE_PATH, 'intermediate_results/dedeuplicated_urls.json'), "r") as file:
    urls = json.load(file)
    print(type(urls))
    print(urls[0])
    
# urls = ["https://www.eiopa.europa.eu/publications/joint-guidelines-oversight-cooperation-and-information-exchange-between-esas-and-competent_en", "https://www.eiopa.europa.eu/publications/joint-guidelines-estimation-aggregated-annual-costs-and-losses-caused-major-ict-related-incidents_en"]

def download_files(urls):
    """
    Visits each URL, finds download buttons, and downloads the files.
    """
    request_delay = 5
    retry_delay = 10


    for url in urls:
        max_retries = 3
        for retry in range(max_retries):
            try:
                print("Making request to: " + url)
                response = requests.get(str(url))
                print("RESPONSE: " + str(response))
                
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)


                soup = BeautifulSoup(response.content, "html.parser")
                download_links = soup.find_all("a", class_="ecl-file__download", attrs={"data-wt-preview": "pdf"})


                if download_links:
                    print("Downloading "  + str(len(download_links)) + " files")
                    for link in download_links:
                        download_url = link["href"]
                        file_name = download_url.split("/")[-1].split("?")[1].split("filename=")[1]  # Get the file name from the URL
                        file_name = file_name.replace("%20", " ")

                        # Ensure the download_url is a full url.
                        if not download_url.startswith('http'):
                            download_url = "https://www.eiopa.europa.eu" + download_url

                        file_data = requests.get(download_url)
                        file_data.raise_for_status()

                        # Save the file
                        with open(os.path.join(PROGRAM_FILE_PATH, 'guidelines', file_name), "wb") as file:
                            file.write(file_data.content)
                        print(f"Downloaded: {file_name}")

                        time.sleep(request_delay)
                
                else:
                    print(f"No download links found on {url}")
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    print(f"Too many requests! Waiting {retry_delay} seconds before retry {retry}/{max_retries}.")
                    time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                print(f"Error accessing {url}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            time.sleep(request_delay) #be nice to the server.

# Run the script
download_files(urls)