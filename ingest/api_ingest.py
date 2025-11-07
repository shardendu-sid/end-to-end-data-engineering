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
#             List2 = []

#             Url = url  # api url path
#             request1 = requests.get(Url, timeout=30)
#             data1 = request1.json()

#             # Parse the timestamp using dateutil.parser
#             utc_timestamp = parser.parse(data1["timestamp"])

#             # Convert to Helsinki time
#             helsinki_timezone = pytz.timezone("Europe/Helsinki")
#             helsinki_timestamp = utc_timestamp.astimezone(helsinki_timezone)

#             # Format the timestamp to display only date and time
#             data1["timestamp"] = helsinki_timestamp.strftime("%Y-%m-%d %H-%M-%S")  # Use - instead of : for Blob

#             # Add location and other columns
#             add_new_col = {"location": "Janonhanta1,Vantaa,Finland"}
#             add_bew_col_serial = {}
#             data1.update(add_bew_col_serial)
#             data1.update(add_new_col)

#             List2.append(data1)

#             # Send to IoT Hub
#             msg = Message(json.dumps(data1))
#             client.send_message(msg)
#             print(f"✅ Sent message: {data1.get('timestamp')}")
#             print(List2)

#             # Safe Blob storage
#             blob_name = re.sub(r'[^a-z0-9\-]', '-', data1["timestamp"].lower()) + ".json"
#             blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER, blob=blob_name)
#             blob_client.upload_blob(json.dumps(data1), overwrite=True)
#             print(f"✅ Stored in Blob: {blob_name}")

#         except Exception as e:
#             print(f"[{datetime.utcnow().isoformat()}] ❌ Error: {e}")

#         time.sleep(300)  # every 5 minutes


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
    
# # cloud_ingest_flask.py
# from flask import Flask, jsonify
# import os
# import re 
# import json
# import time
# import threading
# from azure.iot.device import IoTHubDeviceClient, Message
# from azure.storage.blob import BlobServiceClient
# from dateutil import parser
# import pytz
# import requests

# app = Flask(__name__)

# # =========================
# # Environment variables
# # =========================
# PRIMARY_KEY_STRING = os.environ.get("primary_key_string")  # IoT Hub device key
# API_URL = os.environ.get("API_URL")  # optional: external sensor API
# BLOB_CONN_STRING = os.environ.get("BLOB_CONN_STRING")
# BLOB_CONTAINER = os.environ.get("BLOB_CONTAINER", "sensor-data")
# url = API_URL  # keep your variable naming

# # =========================
# # Initialize Azure clients
# # =========================
# iot_client = IoTHubDeviceClient.create_from_connection_string(PRIMARY_KEY_STRING)
# blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)
# try:
#     blob_service_client.create_container(BLOB_CONTAINER)
# except Exception:
#     pass  # container likely exists

# # =========================
# # Global latest data for Flask endpoint
# # =========================
# latest_data = {}

# # =========================
# # Helper to sanitize blob names
# # =========================
# def sanitize_blob_name(s):
#     """
#     Convert string to valid Azure blob name:
#     lowercase letters, numbers, dash, underscore
#     """
#     s = s.lower()
#     s = re.sub(r'[^a-z0-9\-]', '-', s)
#     s = re.sub(r'-+', '-', s)
#     return s.strip('-') + ".json"


# # =========================
# # Sensor ingestion function
# # =========================
# def sensor_api_connection():
#     conn_str = PRIMARY_KEY_STRING
#     client = IoTHubDeviceClient.create_from_connection_string(conn_str)
#     while True:
#         try:
#             List2 = []

#             Url = url  # API URL path

#             request1 = requests.get(Url, timeout=30)
#             data1 = request1.json()

#             # Update latest_data for Flask endpoint
#             global latest_data
#             latest_data = data1

#             # Parse timestamp from sensor
#             utc_timestamp = parser.parse(data1["timestamp"])

#             # Convert to Helsinki timezone
#             helsinki_timezone = pytz.timezone("Europe/Helsinki")
#             helsinki_timestamp = utc_timestamp.astimezone(helsinki_timezone)

#             # Format timestamp safely for blob
#             safe_ts = helsinki_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
#             data1["timestamp"] = safe_ts

#             # Add extra info
#             data1.update({"location": "Janonhanta1,Vantaa,Finland"})

#             List2.append(data1)

#             # Send to IoT Hub
#             msg = Message(json.dumps(data1))
#             client.send_message(msg)
#             print(f"✅ Sent message: {data1.get('timestamp')}")
            

#             # Store in Azure Blob
#             blob_name = f"{safe_ts}.json"  # only timestamp in blob name
#             blob_client = blob_service_client.get_blob_client(
#                 container=BLOB_CONTAINER, blob=blob_name
#             )
#             blob_client.upload_blob(json.dumps(data1), overwrite=True)
#             print(f"✅ Stored in Blob: {blob_name}")

            

#         except Exception as e:
#             print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error: {e}")

#         time.sleep(300)  # every 5 minutes


# # =========================
# # Start ingestion in background thread
# # =========================
# threading.Thread(target=sensor_api_connection, daemon=True).start()


# # =========================
# # Flask endpoints
# # =========================
# @app.route("/air-data/latest", methods=["GET"])
# def air_data_latest():
#     if latest_data:
#         return jsonify(latest_data)
#     return jsonify({"message": "No data yet"}), 503

# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"status": "running"}), 200


# # =========================
# # Main entry
# # =========================
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     app.run(host="0.0.0.0", port=port)
  
    
# cloud_ingest_flask.py
from flask import Flask, jsonify
import os
import re 
import json
import time
import threading
import logging
from azure.iot.device import IoTHubDeviceClient, Message
from azure.storage.blob import BlobServiceClient
from dateutil import parser
import pytz
import requests

app = Flask(__name__)

# =========================
# Logging setup
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Environment variables
# =========================
PRIMARY_KEY_STRING = os.environ.get("primary_key_string")  # IoT Hub device key
API_URL = os.environ.get("API_URL")  # optional: external sensor API
BLOB_CONN_STRING = os.environ.get("BLOB_CONN_STRING")
BLOB_CONTAINER = os.environ.get("BLOB_CONTAINER", "sensor-data")
url = API_URL  # keep your variable naming

# =========================
# Initialize Azure clients
# =========================
iot_client = IoTHubDeviceClient.create_from_connection_string(PRIMARY_KEY_STRING)
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)
try:
    blob_service_client.create_container(BLOB_CONTAINER)
except Exception:
    pass  # container likely exists

# =========================
# Global latest data for Flask endpoint
# =========================
latest_data = {}

# =========================
# Helper to sanitize blob names
# =========================
def sanitize_blob_name(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\-]', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-') + ".json"

# =========================
# Sensor ingestion function
# =========================
def sensor_api_connection():
    conn_str = PRIMARY_KEY_STRING
    client = IoTHubDeviceClient.create_from_connection_string(conn_str)
    logger.info("🟢 Sensor ingestion thread started")
    
    while True:
        try:
            Url = url
            response = requests.get(Url, timeout=30)
            data1 = response.json()

            # Update latest_data for Flask endpoint
            global latest_data
            latest_data = data1

            # Parse timestamp from sensor
            utc_timestamp = parser.parse(data1["timestamp"])
            helsinki_timezone = pytz.timezone("Europe/Helsinki")
            helsinki_timestamp = utc_timestamp.astimezone(helsinki_timezone)
            safe_ts = helsinki_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
            data1["timestamp"] = safe_ts

            # Add extra info
            data1.update({"location": "Janonhanta1,Vantaa,Finland"})

            # Send to IoT Hub
            msg = Message(json.dumps(data1))
            client.send_message(msg)
            logger.info(f"✅ Sent message: {data1.get('timestamp')}")

            # Store in Azure Blob
            blob_name = f"{safe_ts}.json"
            blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER, blob=blob_name)
            blob_client.upload_blob(json.dumps(data1), overwrite=True)
            logger.info(f"✅ Stored in Blob: {blob_name}")

        except Exception as e:
            logger.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error: {e}")

        # Sleep at end of loop (applies to success and failure)
        time.sleep(300)  # every 5 minutes

# =========================
# Start ingestion in background thread
# =========================
threading.Thread(target=sensor_api_connection, daemon=True).start()

# =========================
# Flask endpoints
# =========================
@app.route("/air-data/latest", methods=["GET"])
def air_data_latest():
    if latest_data:
        return jsonify(latest_data)
    return jsonify({"message": "No data yet"}), 503

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

# =========================
# Main entry
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

