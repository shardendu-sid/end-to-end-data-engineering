# API ingestion script

import requests
import json
import csv
import os
import pytz
from dateutil import parser
import time

host = os.environ.get("CONTAINER_IP")
port = os.environ.get("PORT")
database = os.environ.get("DATABASE")
user = os.environ.get("USER")
password = os.environ.get("PASS_WORD")
url = os.environ.get("API_URL")



def sensor_api_connection():
    while True:
        api_data_list = []

        Url = url

        request1 = requests.get(Url)
        data1 = request1.json()
        

        add_new_col = {"location": "Janonhanta1, Vantaa, Finland"}
        add_new_col_serial = {}
        data1.update(add_new_col_serial)
        data1.update(add_new_col)

        api_data_list.append(data1)

        print(api_data_list)


sensor_api_connection()

# def apenaq_api():

#     API_KEY = "972f1e65eae2c6241edea134055c60a4b3ad9bb7b75a1c2cccf77f835cb29aa0"
#     url = "https://api.openaq.org/v3/locations/2178"

#     params = {
#         "country_id": "FI",       # Finland
#         "city": "Vantaa",         # City name
#         "limit": 5,
#         "sort": "desc",
#         "order_by": "datetime"
#     }

#     headers = {
#         "x-api-key": API_KEY
#     }

#     response = requests.get(url, headers=headers)
#     data = response.json()
#     print(data)



apenaq_api()