from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# Kafka Configuration
KAFKA_TOPIC = "parking_data"
KAFKA_BROKER = "host.docker.internal:9092"

# MongoDB Connection (with authentication)
client = MongoClient("mongodb://root:password@localhost:27017/")
db = client["smart_parking"]
collection = db["parking_data"]

# Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    group_id='parking-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🔍 Listening for Kafka messages...")

for message in consumer:
    parking_data = message.value
    # Ensure authentication for delete and insert operations
    try:
        # Delete existing records
        collection.delete_many({})
        
        # Insert new data
        collection.insert_many(parking_data)
        print(f"✅ Updated parking data in MongoDB with {len(parking_data)} entries.")

    except Exception as e:
        print(f"❌ Failed to insert data: {e}")
