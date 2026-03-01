
# AI-Based Driver License Data Extraction Module

## Overview

This project is an AI-powered module that extracts structured data from driver license images of various formats and layouts, returning a standardized JSON response. It leverages advanced image preprocessing (OpenCV) and Google Gemini Vision AI for robust field extraction, even from noisy, rotated, or damaged images.

---

## How OpenCV Is Used

OpenCV is central to the image preprocessing pipeline:

- **Deskewing**: Detects and corrects image rotation/skew for better OCR and AI extraction.
- **Denoising**: Removes noise using `fastNlMeansDenoisingColored` for clearer text regions.
- **Contrast Enhancement**: Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) to improve text visibility.
- **Resizing & Color Conversion**: Ensures images are in optimal format and size for extraction.

All these steps are implemented in `app/preprocessing.py` and are automatically applied to uploaded images before AI extraction.

---

## Expected Deliverables

- **API Endpoint**: `/documents/driver-license/parse` (POST) — Accepts an image and returns extracted fields in JSON.
- **Standardized JSON Output**: Includes all readable fields (name, DOB, license number, address, expiry, etc.), confidence scores, reliability, and warnings for missing/uncertain fields.
- **Robust Extraction**: Handles blurry, rotated, multi-language, and damaged licenses.
- **Field Normalization**: Dates, license numbers, gender, and country codes are normalized for consistency.

---

## How to Run the Code


### Prerequisites

- Python 3.8+
- Install dependencies:
	```
	pip install -r requirements.txt
	```
- Set up environment variables in a `.env` file:
	```
	GEMINI_API_KEY=your_google_gemini_api_key
	MODEL_NAME=gemini-2.5-flash-lite
	```

### How to Run

#### 1. Start the Backend (API)

Open a terminal and run:
```
uvicorn app.main:app --port 8000
```

#### 2. Start the Frontend

Open a different terminal and run:
```
python -m http.server 8090
```

#### 3. Access the Application

Open your browser and go to:
```
http://localhost:8090/frontend.html
```

Upload a driver license image and view the extracted data directly in the browser. The frontend will communicate with the backend at port 8000.

---

---

## Architecture Diagram

```mermaid
flowchart TD
		A[Client Uploads Image] --> B[FastAPI Endpoint]
		B --> C[Preprocessing (OpenCV)]
		C --> D[Gemini Vision AI Extraction]
		D --> E[Pydantic Validation]
		E --> F[Standardized JSON Response]
```

---

## Workflow

1. **Image Upload**: User uploads a driver license image via API.
2. **Preprocessing**: Image is deskewed, denoised, and enhanced using OpenCV.
3. **AI Extraction**: Cleaned image is sent to Gemini Vision AI, which extracts all readable fields.
4. **Validation**: Extracted data is validated and normalized using Pydantic schemas.
5. **Response**: API returns a standardized JSON with all fields, confidence scores, reliability, and warnings.

---

## File Structure

- `app/preprocessing.py`: Image cleaning pipeline (OpenCV).
- `app/extractor.py`: Gemini Vision AI prompt and extraction logic.
- `app/routes.py`: API endpoints.
- `app/schemas.py`: Pydantic models for response validation.
- `app/main.py`: FastAPI app setup.
- `requirements.txt`: Dependencies.

---

## Contact & Support

For issues or feature requests, please open an issue in this repository.
