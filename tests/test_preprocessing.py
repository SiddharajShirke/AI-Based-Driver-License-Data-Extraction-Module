from app.preprocessing import preprocess_image

with open("test_image.jpg", "rb") as f:
    raw_bytes = f.read()

print("Input size:", len(raw_bytes), "bytes")

clean_bytes = preprocess_image(raw_bytes)

print("Output size:", len(clean_bytes), "bytes")

# Save output to verify visually
with open("test_output.jpg", "wb") as f:
    f.write(clean_bytes)

print("Saved to test_output.jpg — open it to verify")
