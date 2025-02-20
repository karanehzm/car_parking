from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Connection
client = MongoClient("mongodb://root:password@localhost:27017/")
db = client["smart_parking"]
parking_collection = db["parking_data"]
image_stats_collection = db["image_stats"]

@app.route('/')
def index():
    total_spaces = 100  # Total parking spaces in Parking_A

    # Step 1: Get the latest timestamp for Parking_A
    latest_entry = parking_collection.find_one(
        {"parking_lot": "Parking_A"}, sort=[("timestamp", -1)]
    )

    if latest_entry:
        latest_timestamp = latest_entry["timestamp"]

        # Step 2: Count occupied spaces only for the latest timestamp
        occupied_count = parking_collection.count_documents(
            {"parking_lot": "Parking_A", "timestamp": latest_timestamp, "occupied": 1}
        )

        # Step 3: Calculate available spaces
        available_spaces_parking = max(total_spaces - occupied_count, 0)
    else:
        available_spaces_parking = "N/A"
        latest_timestamp = "N/A"

    # Fetch latest available spaces from image_stats
    latest_image_stats = image_stats_collection.find_one({}, sort=[("timestamp", -1)])
    available_spaces_image = latest_image_stats.get("available_spaces", "N/A") if latest_image_stats else "N/A"

    # Debugging Output
    print("\n🔍 Latest Data Fetched from MongoDB:")
    print(f"📌 Parking_A - Latest Timestamp: {latest_timestamp}")
    print(f"📌 Parking_A - Available Spaces: {available_spaces_parking} (Occupied: {occupied_count if latest_entry else 'N/A'})")
    print(f"📌 Image Stats - Available Spaces: {available_spaces_image}")

    return render_template("index.html", 
                           available_spaces_parking=available_spaces_parking,
                           available_spaces_image=available_spaces_image,
                           latest_timestamp=latest_timestamp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
