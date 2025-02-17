from ultralytics import YOLO

# Load the trained YOLO model
model = YOLO('best.pt')

def analyze_parking_image(image_path):
    """
    Analyze a parking image using YOLO model.
    Returns a list of parking space statuses.
    """
    # Run the model on the image
    results = model.predict(image_path, conf=0.25, imgsz=4096)[0]

    # Initialize the status list
    parking_data = []

    # Check if there are any detections
    if results.boxes:
        for i, box in enumerate(results.boxes):
            class_id = int(box.cls.item())
            confidence = float(box.conf.item())
            class_name = results.names[class_id]

            # Determine if the spot is available or occupied
            occupied = 1 if class_name == "space-occupied" else 0

            # Append the status to the list
            parking_data.append({
                "lot_id": f"Lot_{i+1}",
                "occupied": occupied,
                "confidence": round(confidence, 2)
            })

    # If no detections, assume all spots are unknown
    if not parking_data:
        print("⚠️ No detections found. Defaulting all spots to occupied.")
        parking_data = [{"lot_id": f"Lot_{i+1}", "occupied": 1} for i in range(100)]

    return parking_data
