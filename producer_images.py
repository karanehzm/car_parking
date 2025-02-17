from kafka import KafkaProducer
import time
import os

# Kafka Configuration
KAFKA_TOPIC = "parking_images"
KAFKA_BROKER = "host.docker.internal:9092"

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

# Folder containing images
image_folder = "images"

while True:
    images = sorted(os.listdir(image_folder))
    if not images:
        print("📸 No images found.")
        time.sleep(60)
        continue

    # Send one image at a time
    image = images[0]
    image_path = os.path.join(image_folder, image)

    with open(image_path, "rb") as img_file:
        img_data = img_file.read()

    # Send image to Kafka
    producer.send(KAFKA_TOPIC, img_data)
    print(f"📤 Sent image: {image}")

    # Remove the processed image
    os.remove(image_path)

    time.sleep(60)  # Send one image every minute
