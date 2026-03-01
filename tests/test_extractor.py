from app.preprocessing import preprocess_image
from app.extractor import extract_license_data
import json

with open("test_image.jpg", "rb") as f:
    raw_bytes = f.read()

# Step 1 — Preprocess
clean_bytes = preprocess_image(raw_bytes)
print("Preprocessing done")

# Step 2 — Extract
result = extract_license_data(clean_bytes)

# Step 3 — Print result
print(json.dumps(result, indent=2))
