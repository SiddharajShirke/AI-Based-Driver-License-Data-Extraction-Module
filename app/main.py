from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Driver License Extractor",
    description="AI-powered driver license data extraction API",
    version="1.0.0"
)

# CORS — needed for frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "running"}
