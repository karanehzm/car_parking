# Updated app.py
from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://root:password@localhost:27017/")
db = client["smart_parking"]
collection = db["parking_data"]

@app.route('/')
def index():
    # Fetch available spaces for Parking 1 (sensors)
    parking1_available = collection.count_documents({"parking_lot": "Parking_A", "occupied": 0})

    # Fetch available spaces for Parking 2 (camera/ML)
    parking2_available = collection.count_documents({"parking_lot": "Parking_B", "occupied": 0})

    # Get the latest timestamps for both parking lots
    parking1_latest = collection.find({"parking_lot": "Parking_A"}).sort("timestamp", -1).limit(1)
    parking2_latest = collection.find({"parking_lot": "Parking_B"}).sort("timestamp", -1).limit(1)

    # Extract timestamps
    parking1_timestamp = next(parking1_latest, {}).get("timestamp", "No data")
    parking2_timestamp = next(parking2_latest, {}).get("timestamp", "No data")

    return render_template(
        "index.html",
        parking1_available=parking1_available,
        parking2_available=parking2_available,
        parking1_timestamp=parking1_timestamp,
        parking2_timestamp=parking2_timestamp
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# Updated consumer_image.py
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient
from datetime import datetime
from ml_model import analyze_parking_image
import os

# Kafka Configuration
IMAGE_TOPIC = "parking_images"
DATA_TOPIC = "parking_data"
KAFKA_BROKER = "host.docker.internal:9092"

# Initialize Kafka consumer and producer
consumer = KafkaConsumer(IMAGE_TOPIC, bootstrap_servers=KAFKA_BROKER, auto_offset_reset='earliest')
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER, value_serializer=lambda v: v.encode('utf-8'))

# MongoDB Connection
client = MongoClient("mongodb://root:password@localhost:27017/")
db = client["smart_parking"]
image_stats_collection = db["image_stats"]

print("🔍 Listening for images...")

for message in consumer:
    # Save the received image
    image_path = "temp_image.jpg"
    with open(image_path, "wb") as img_file:
        img_file.write(message.value)

    # Process the image with YOLO
    print(f"🧠 Analyzing image: {image_path}")
    parking_data = analyze_parking_image(image_path)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert image stats into MongoDB
    available = sum(1 for entry in parking_data if entry["occupied"] == 0)
    occupied = sum(1 for entry in parking_data if entry["occupied"] == 1)
    total = available + occupied

    image_stats_collection.insert_one({
        "image_name": os.path.basename(image_path),
        "timestamp": current_time,
        "available_spaces": available,
        "occupied_spaces": occupied,
        "total_spaces": total
    })

    print(f"✅ Image processed: {available} available, {occupied} occupied.")

    # Add timestamp and parking lot info to each entry and send to Kafka
    for entry in parking_data:
        entry["parking_lot"] = "Parking_B"
        entry["timestamp"] = current_time

    producer.send(DATA_TOPIC, str(parking_data))
    print(f"📤 Processed data sent to Kafka.")


# Updated consumer.py
from kafka import KafkaConsumer
from pymongo import MongoClient
import ast

# Kafka Configuration
KAFKA_TOPIC = "parking_data"
KAFKA_BROKER = "host.docker.internal:9092"

# MongoDB Connection
client = MongoClient("mongodb://root:password@localhost:27017/")
db = client["smart_parking"]
collection = db["parking_data"]

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BROKER, auto_offset_reset='earliest')

print("🔍 Listening for processed data...")

for message in consumer:
    data = ast.literal_eval(message.value.decode('utf-8'))
    if data:
        latest_timestamp = data[0]['timestamp']
        collection.delete_many({"parking_lot": "Parking_B", "timestamp": latest_timestamp})
        collection.insert_many(data)
        print(f"✅ Data stored for timestamp {latest_timestamp}.")
    else:
        print("⚠️ Empty data received.")

