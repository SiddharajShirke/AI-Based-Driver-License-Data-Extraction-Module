from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.preprocessing import preprocess_image
from app.extractor import extract_license_data
from app.schemas import DriverLicenseResponse

router = APIRouter()


@router.post("/documents/driver-license/parse")
async def parse_driver_license(file: UploadFile = File(...)):

    # Step 1 — Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Upload a JPEG or PNG image."
        )

    # Step 2 — Read file bytes
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # Step 3 — Preprocess image
    try:
        clean_bytes = preprocess_image(file_bytes)
    except Exception as e:
        return JSONResponse(
            status_code=422,
            content={
                "documentType": "driver_license",
                "warnings": [f"Preprocessing failed: {str(e)}"]
            }
        )

    # Step 4 — Extract data using Gemini Vision
    raw_result = extract_license_data(clean_bytes)

    # Step 5 — Validate and enforce JSON shape using Pydantic
    try:
        validated = DriverLicenseResponse(**raw_result)
        return validated.model_dump()
    except Exception as e:
        # Even if validation fails, return valid JSON
        return JSONResponse(
            status_code=200,
            content={
                "documentType": "driver_license",
                "warnings": [f"Validation error: {str(e)}"]
            }
        )
