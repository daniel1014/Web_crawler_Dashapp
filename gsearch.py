from googleapiclient.discovery import build

my_api_key = "AIzaSyAWd9YsJLvzIiQViBppiiy9L3w_osvsuyU" #The API_KEY you acquired
my_cse_id = "c7176b7cccea54d9d" #The search-engine-ID you created


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

