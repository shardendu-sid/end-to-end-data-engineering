# API ingestion script
import requests
import json
import csv
import os
import pytz
from dateutil import parser
import time
import sqlite3
from azure.iot.device import IoTHubDeviceClient, Message
from azure.eventhub import EventHubConsumerClient

primary_k_string = os.environ.get("primary_key_string")
event_hub_endpoint = os.environ.get("event_hub_conn_str")
event_name_of_end_point = os.environ.get("event_name")

host = os.environ.get("CONTAINER_IP")
port = os.environ.get("PORT")
database = os.environ.get("DATABASE")
user = os.environ.get("USER")
password = os.environ.get("PASS_WORD")
url = os.environ.get("API_URL")



def sensor_api_connection():
    while True:
        api_data_list = {}

        Url = url

        request1 = requests.get(Url)
        data1 = request1.json()
        

        add_new_col = {"location": "Janonhanta1, Vantaa, Finland"}
        add_new_col_serial = {}
        data1.update(add_new_col_serial)
        data1.update(add_new_col)

        api_data_list.update(data1)

        conn_str = primary_k_string

        client = IoTHubDeviceClient.create_from_connection_string(conn_str)

        msg = Message(json.dumps(api_data_list))

        client.send_message(msg)

        conn = sqlite3.connect("/Users/shardendujha/Documents/End-to-End_Data_eng_Project/database/aiq.db")
        cursor = conn.cursor()

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS awair_data (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp TEXT,
                       score REAL,
                        dew_point REAL,
                        temp REAL,
                        humid REAL,
                        abs_humid REAL,
                        co2 REAL,
                        co2_est REAL,
                        co2_est_baseline REAL,
                        voc REAL,
                        voc_baseline REAL,
                        voc_h2_raw REAL,
                        voc_ethanol_raw REAL,
                        pm25 REAL,
                        pm10_est REAL
                       )
                       """)
        conn.commit()

        eventhub_conn_str = event_hub_endpoint
        eventhub_name = event_name_of_end_point
        
        def on_event(partition_context, event):
            try:
                message = json.loads(event.body_as_str())
                cursor.execute("""
                    INSERT INTO awair_data (
                        timestamp, score, dew_point, temp, humid, abs_humid, co2,
                        co2_est, co2_est_baseline, voc, voc_baseline, voc_h2_raw,
                        voc_ethanol_raw, pm25, pm10_est
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.get("timestamp"),
                    message.get("score"),
                    message.get("dew_point"),
                    message.get("temp"),
                    message.get("humid"),
                    message.get("abs_humid"),
                    message.get("co2"),
                    message.get("co2_est"),
                    message.get("co2_est_baseline"),
                    message.get("voc"),
                    message.get("voc_baseline"),
                    message.get("voc_h2_raw"),
                    message.get("voc_ethanol_raw"),
                    message.get("pm25"),
                    message.get("pm10_est")
                ))
                conn.commit()

                partition_context.update_checkpoint(event)
                print("Saved message to SQLite:", message.get("timestamp"))

            except Exception as e:
                print("Error:", e)

        client = EventHubConsumerClient.from_connection_string(
            conn_str=eventhub_conn_str,
            consumer_group="$Default",
            eventhub_name=eventhub_name
        )

        with client:
            print("Listening for IoT Hub messages...")
            client.receive(
                on_event=on_event,
                starting_position="@latest"  
            )

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



# apenaq_api()