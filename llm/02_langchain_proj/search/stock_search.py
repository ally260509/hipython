from dotenv import load_dotenv
import os
load_dotenv()
MIELIE_SEARCH_KEY = os.environ['MIELIE_SEARCH_KEY']

import meilisearch
client = meilisearch.Client("http://127.0.0.1:7700", MIELIE_SEARCH_KEY)

def stock_search(query):
    return client.index('kospi').search(query)