# # API ingestion script
# import requests
# import json
# import csv
# import os
# import pytz
# from dateutil import parser
# import threading
# import time
# import sqlite3
# from azure.iot.device import IoTHubDeviceClient, Message
# from azure.eventhub import EventHubConsumerClient
# from azure.
# from datetime import datetime

# primary_k_string = os.environ.get("primary_key_string")
# event_hub_endpoint = os.environ.get("event_hub_conn_str")
# event_name_of_end_point = os.environ.get("event_name")
# sqllite_database_path = os.environ.get("sql_path")

# host = os.environ.get("CONTAINER_IP")
# port = os.environ.get("PORT")
# database = os.environ.get("DATABASE")
# user = os.environ.get("USER")
# password = os.environ.get("PASS_WORD")
# url = os.environ.get("API_URL")



# def sensor_api_connection():
#     conn_str = primary_k_string
#     client = IoTHubDeviceClient.create_from_connection_string(conn_str)
#     while True:
#         try:
#             resp = requests.get(url, timeout=10)
#             resp.raise_for_status()
#             data = resp.json()
#         except Exception as e:
#             print("Error fetching API:", e)
#             time.sleep(60)
#             continue

#         # Add extra info
#         data.update({"location": "Janonhanta1, Vantaa, Finland"})

#         # Send to IoT Hub
#         msg = Message(json.dumps(data))
#         client.send_message(msg)
#         print(f"✅ Sent message: {data.get('timestamp')}")
#         time.sleep(300)

# def listen_to_eventhub():
#     print("Listening for IoT Hub messages...")

    
#     os.makedirs(os.path.dirname(sqllite_database_path), exist_ok=True)
#     conn = sqlite3.connect(sqllite_database_path, check_same_thread=False)
#     cursor = conn.cursor()

#     cursor.execute("""
#                     CREATE TABLE IF NOT EXISTS awair_data (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     timestamp TEXT,
#                     score REAL,
#                     dew_point REAL,
#                     temp REAL,
#                     humid REAL,
#                     abs_humid REAL,
#                     co2 REAL,
#                     co2_est REAL,
#                     co2_est_baseline REAL,
#                     voc REAL,
#                     voc_baseline REAL,
#                     voc_h2_raw REAL,
#                     voc_ethanol_raw REAL,
#                     pm25 REAL,
#                     pm10_est REAL
#                     )
#                     """)
#     conn.commit()

#     eventhub_conn_str = event_hub_endpoint
#     eventhub_name = event_name_of_end_point

#     def on_event(partition_context, event):
#         try:
#             message = json.loads(event.body_as_str())
#             cursor.execute("""
#                 INSERT INTO awair_data (
#                     timestamp, score, dew_point, temp, humid, abs_humid, co2,
#                     co2_est, co2_est_baseline, voc, voc_baseline, voc_h2_raw,
#                     voc_ethanol_raw, pm25, pm10_est
#                 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 message.get("timestamp"),
#                 message.get("score"),
#                 message.get("dew_point"),
#                 message.get("temp"),
#                 message.get("humid"),
#                 message.get("abs_humid"),
#                 message.get("co2"),
#                 message.get("co2_est"),
#                 message.get("co2_est_baseline"),
#                 message.get("voc"),
#                 message.get("voc_baseline"),
#                 message.get("voc_h2_raw"),
#                 message.get("voc_ethanol_raw"),
#                 message.get("pm25"),
#                 message.get("pm10_est")
#             ))
#             conn.commit()

#             partition_context.update_checkpoint(event)
#             print("Saved message to SQLite:", message.get("timestamp"))

#         except Exception as e:
#             print("Error:", e)

#     client = EventHubConsumerClient.from_connection_string(
#         conn_str=eventhub_conn_str,
#         consumer_group="$Default",
#         eventhub_name=eventhub_name
#     )

#     with client:
#         # print("Listening for IoT Hub messages...")
#         client.receive(
#             on_event=on_event,
#             starting_position="@latest"  
#         )
# if __name__ == "__main__":
#     sender_thread = threading.Thread(target=sensor_api_connection, daemon=True)
#     listener_thread = threading.Thread(target=listen_to_eventhub, daemon=False)

#     sender_thread.start()
#     listener_thread.start()

#     sender_thread.join()
#     listener_thread.join()
    
# cloud_ingest_flask.py
from flask import Flask, jsonify
import requests
import json
import os
import time
import threading
from azure.iot.device import IoTHubDeviceClient, Message
from azure.storage.blob import BlobServiceClient
from datetime import datetime

app = Flask(__name__)

# Environment variables (set in Azure App Service)
PRIMARY_KEY_STRING = os.environ.get("primary_key_string")
API_URL = os.environ.get("API_URL")  # if you have an external sensor API
BLOB_CONN_STRING = os.environ.get("BLOB_CONN_STRING")
BLOB_CONTAINER = os.environ.get("BLOB_CONTAINER", "sensor-data")

# IoT Hub client
iot_client = IoTHubDeviceClient.create_from_connection_string(PRIMARY_KEY_STRING)

# Azure Blob client
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)

# Ensure container exists
try:
    blob_service_client.create_container(BLOB_CONTAINER)
except Exception:
    pass  # container likely already exists

# Function to fetch from sensor API and store
def fetch_and_store_sensor_data():
    while True:
        try:
            resp = requests.get(API_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[{datetime.utcnow()}] Error fetching API:", e)
            time.sleep(60)
            continue

        data.update({"location": "Janonhanta1, Vantaa, Finland"})
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        # Send to IoT Hub
        try:
            msg = Message(json.dumps(data))
            iot_client.send_message(msg)
            print(f"[{timestamp}] ✅ Sent message to IoT Hub")
        except Exception as e:
            print(f"[{timestamp}] ❌ Failed to send to IoT Hub:", e)

        # Store in Blob
        try:
            blob_name = f"{timestamp.replace(':','-')}.json"
            blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER, blob=blob_name)
            blob_client.upload_blob(json.dumps(data), overwrite=True)
            print(f"[{timestamp}] ✅ Stored message in Blob: {blob_name}")
        except Exception as e:
            print(f"[{timestamp}] ❌ Failed to store in Blob:", e)

        time.sleep(300)  # wait 5 minutes

# Start the fetch loop in a separate thread
threading.Thread(target=fetch_and_store_sensor_data, daemon=True).start()

# Flask endpoint (optional: you can check API health)
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0")
