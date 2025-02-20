from kafka import KafkaConsumer
from pymongo import MongoClient
import json

KAFKA_TOPIC = "parking_data_iot"
KAFKA_BROKER = "host.docker.internal:9092"

# Connect to MongoDB
client = MongoClient("mongodb://root:password@localhost:27017/")
db = client["smart_parking"]
collection = db["parking_data"]

# Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),  # Deserialize JSON properly
    auto_offset_reset='earliest'
)

print("🔍 Listening for IoT sensor data (Parking_A)...")

for message in consumer:
    try:
        data = message.value  # Already deserialized JSON object
        print(f"📩 Received message: {data}")

        # Add "parking_iot" field
        data["parking_iot"] = "Parking_A"

        # Store in MongoDB
        collection.insert_one(data)
        print(f"✅ IoT Data stored for Parking_A at timestamp {data['timestamp']}.")

    except Exception as e:
        print(f"❌ Error processing message: {e}")
