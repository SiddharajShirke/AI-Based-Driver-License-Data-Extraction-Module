from google import genai
from google.genai import types
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Force convert image to clean JPEG using Pillow
img = Image.open("test_image.jpg")
img = img.convert("RGB")

buffer = io.BytesIO()
img.save(buffer, format="JPEG")
img_bytes = buffer.getvalue()

print("Image size after conversion:", len(img_bytes), "bytes")

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[
        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
        "What do you see in this image? One sentence only."
    ]
)

print(response.text)
