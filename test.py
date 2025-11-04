# from azure.eventhub import EventHubConsumerClient
# import os

# conn_str = os.environ["event_hub_conn_str"]
# eventhub_name = os.environ["event_name"]

# client = EventHubConsumerClient.from_connection_string(
#     conn_str=conn_str,
#     consumer_group="$Default",
#     eventhub_name=eventhub_name
# )
# print("✅ Connection created successfully")
# client.close()


from azure.iot.device import IoTHubDeviceClient, Message
import os, json

conn_str = os.environ["primary_key_string"]

client = IoTHubDeviceClient.create_from_connection_string(conn_str)

test_msg = {"timestamp": "2025-11-03T12:00:00Z", "temp": 25, "humid": 60, "co2": 400}
client.send_message(Message(json.dumps(test_msg)))
client.shutdown()
print("✅ Test message sent")
