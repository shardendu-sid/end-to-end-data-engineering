import requests
import os

api_key = os.environ.get("aiq_finland_api_key")
URL = os.environ.get("aiq_finland_url")

def apenaq_api():

    API_KEY = api_key
    url = URL

    # params = {
    #     "country_id": "FI",       # Finland
    #     "city": "Vantaa",         # City name
    #     "limit": 5,
    #     "sort": "desc",
    #     "order_by": "datetime"
    # }

    headers = {
        "x-api-key": API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    print(data)

apenaq_api()