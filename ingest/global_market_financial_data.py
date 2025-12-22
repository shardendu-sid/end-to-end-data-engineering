import json
import os
import csv
import requests



def gloabal_financial_market_data():
    API_KEY = "5f133d5b2b64ec5f95e5d152090d3cd2"
    url = "http://api.marketstack.com/v1/eod" # /v1/eod,/v1/tickers,/v1/exchanges,/v1/intraday
    params = {
                "access_key": API_KEY,
                "symbols": "AAPL",
                "limit": 5
            }
    response = requests.get(url, params=params)
    data = response.json()
    for i in data.items():
        for y in i:
            print(y)
    
   
gloabal_financial_market_data()