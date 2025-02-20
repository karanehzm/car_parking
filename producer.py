from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

KAFKA_TOPIC = "parking_data_iot"  
KAFKA_BROKER = "host.docker.internal:9092"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    api_version=(0, 10, 1)
)

space_ids = [f"Lot_{i}" for i in range(1, 101)]

while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for space_id in space_ids:
        status = random.choice([0, 1])  
        parking_data = {
            "parking_lot": "Parking_A",
            "lot_id": space_id,
            "occupied": status,
            "timestamp": current_time
        }

        producer.send(KAFKA_TOPIC, parking_data)
        print(f"🚗 Sent IoT Data to Kafka: {parking_data}")

    time.sleep(60)
