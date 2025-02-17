from ultralytics import YOLO

# Load your trained model
model = YOLO('best.pt')

# Perform inference on a single image
results = model('image.jpg')

# Display results
results.show()

# Save the annotated image
results.save('output/')

# Print detected objects
for result in results:
    print(result.names, result.boxes)
