import httpx

url = "http://127.0.0.1:8000/documents/driver-license/parse"

with open("test_image.jpg", "rb") as f:
    files = {"file": ("test_image.jpg", f, "image/jpeg")}
    response = httpx.post(url, files=files, timeout=60)

import json
print(json.dumps(response.json(), indent=2))
