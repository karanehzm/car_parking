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

    # Extract image name
    image_name = os.path.basename(image_path)

    # Process the image with YOLO
    print(f"🧠 Analyzing image: {image_name}")
    parking_data = analyze_parking_image(image_path)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Count available and occupied spaces
    available = sum(1 for entry in parking_data if entry["occupied"] == 0)
    occupied = sum(1 for entry in parking_data if entry["occupied"] == 1)
    total = available + occupied

    # Insert image stats into MongoDB
    image_stats_collection.insert_one({
        "image_name": image_name,
        "timestamp": current_time,
        "available_spaces": available,
        "occupied_spaces": occupied,
        "total_spaces": total
    })

    print(f"✅ Image '{image_name}' processed: {available} available, {occupied} occupied.")

    # Add timestamp and parking lot info to each entry and send to Kafka
    for entry in parking_data:
        entry["parking_lot"] = "Parking_B"
        entry["timestamp"] = current_time

    # Send processed parking data to Kafka
    producer.send(DATA_TOPIC, str(parking_data))
    print(f"📤 Processed data sent to Kafka.")
