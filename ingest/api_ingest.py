# API ingestion script

import requests
import json
import csv
import psycopg2
import os
import pytz
from dateutil import parser
import time

host = os.environ.get("CONTAINER_IP")
port = os.environ.get("PORT")
database = os.environ.get("DATABASE")
user = os.environ.get("USER")
password = os.environ.get("PASS_WORD")
url = os.environ.get("API_LINK")

def sensor_api_connection():
    while True:
        api_data_list = []

        Url = url

        request1 = requests.get(Url)
        data1 = request1.json()
        

        # add_new_col = {"location": "Janonhanta1, Vantaa, Finland"}
        # add_new_col_serial = {}
        # data1.update(add_new_col_serial)
        # data1.update(add_new_col)

        # api_data_list.append(data1)

        print(data1)






sensor_api_connection()