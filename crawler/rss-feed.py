import feedparser
import json
import os
import time

PROGRAM_FILE_PATH = os.path.dirname(__file__)
rss_url = 'https://www.eiopa.europa.eu/node/4755/rss_en'

# page is zero-indexed!!!!!
def parse_rss_feed(base_rss_url, limit, page):
  offset = page * limit
  rss_url = f"{base_rss_url}?limit={limit}&offset={offset}"

  print(f"Fetching feed from: {rss_url}")
  feed = feedparser.parse(rss_url)
#   print("FEED PUBLISHED ON:", feed.published_parsed)
# #   print(feed)
  if feed.bozo == 1:
      print(f"Warning: Feed parsing errors (bozo=1) at {rss_url}. Proceeding with caution.")

  if feed.get('entries'):
      print(f"Fetched {len(feed.entries)} entries from URL with item limit parameter.") # Check number of entries
      return feed
  else:
      print(f"No entries found in the feed at {rss_url}")
      return None
  
def save_entries(filename, entries):
  with open(os.path.join(PROGRAM_FILE_PATH, "entries", filename), "w") as f:
    json.dump(entries, f, indent=2)

limit = 100
start_page = 0
number_of_pages = 1
crawl_delay = 5
for current_page in range(start_page, number_of_pages):
  feed = parse_rss_feed(rss_url, limit, current_page)
  if not feed or not feed.entries:
    print(f"Could not fetch for limit {limit} and current_page {current_page}")
    continue
  print("ENTRIES TYPE: ", type(feed.entries))
  save_entries(f"entries-limit-{limit}-current_page-{current_page}.json", feed.entries)
  save_entries(f"feed-entries-limit-{limit}-current_page-{current_page}.json", feed)
  time.sleep(crawl_delay)

