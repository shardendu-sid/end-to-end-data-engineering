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
    data.pop('pagination', None)

    dict_data = []
    for i in data.items():
        for row in i[1]:
            dict_data.append(row)
        
        print(dict_data)
       
            
            # print(value)
gloabal_financial_market_data()