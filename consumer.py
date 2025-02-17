from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import ast

# Kafka Configuration
KAFKA_TOPIC = "parking_data"
KAFKA_BROKER = "host.docker.internal:9092"

# MongoDB Connection
client = MongoClient("mongodb://root:password@localhost:27017/")
db = client["smart_parking"]
collection = db["parking_data"]

# Kafka Consumer
consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BROKER, auto_offset_reset='earliest')

print("🔍 Listening for processed data...")

for message in consumer:
    data = ast.literal_eval(message.value.decode('utf-8'))
    collection.delete_many({"parking_lot": "Parking_B"})  # Remove old data for this parking
    collection.insert_many(data)
    print("✅ Processed data stored in MongoDB.")
