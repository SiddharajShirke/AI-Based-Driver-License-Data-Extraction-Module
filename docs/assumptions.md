# Assumptions

This document outlines the assumptions made during the development of the Driver License Data Extraction Module.

---

## 1. Input Assumptions

### Image Format
- Images are in JPEG, PNG, or WebP format
- Images are readable by standard image libraries (PIL, OpenCV)
- File size is reasonable (< 10MB recommended)

### Image Content
- Image contains a driver's license (not other document types)
- License is the primary object in the image
- Text is visible (not completely obscured or blank)
- Image is not encrypted or password-protected

### Image Quality
- Minimum resolution of at least 300x300 pixels
- Text is at least partially readable by human eye
- License is not completely torn or destroyed

---

## 2. System Assumptions

### Environment
- Python 3.8+ is installed
- Required dependencies can be installed via pip
- Sufficient memory available for image processing (minimum 2GB RAM)
- Internet connection is available for Gemini API calls

### Configuration
- `.env` file contains valid Gemini API key
- API key has sufficient quota/credits
- Environment variables are properly loaded

### Deployment
- Single-threaded processing (one request at a time)
- Frontend and backend run on localhost
- Ports 8000 and 8090 are available

---

## 3. API Assumptions

### Gemini API
- Google Gemini API is accessible and operational
- API returns responses in reasonable time (< 30 seconds)
- API supports image input and JSON output
- Model `gemini-2.5-flash-lite` is available

### Request/Response
- Single image per API request
- Image uploaded via HTTP POST multipart/form-data
- Response is returned synchronously (not async)

---

## 4. Data Assumptions

### License Format
- Driver's license follows standard international formats
- Text fields are in Latin script or transliterable scripts
- Key fields (name, license number, DOB) are present
- Dates are in recognizable formats (DD/MM/YYYY, MM/DD/YYYY, etc.)

### Field Values
- Names contain alphabetic characters
- License numbers are alphanumeric
- Dates are valid calendar dates
- Gender is represented as M/F or Male/Female
- Country codes follow ISO 3166-1 alpha-2 standard

---

## 5. User Assumptions

### User Intent
- User intends to extract data from driver's licenses only
- User provides legitimate documents (not attempting fraud)
- User has rights to process the uploaded image
- User understands data is processed via external API

### User Expectations
- Extracted data may not be 100% accurate
- Manual verification may be required
- Processing takes a few seconds
- Internet connection is needed

---

## 6. Processing Assumptions

### OpenCV Pipeline
- Rotation angle can be detected from text regions
- Denoising improves text readability
- CLAHE enhances contrast effectively
- Upscaling to 1024px improves extraction

### AI Extraction
- Gemini Vision AI can understand image context
- AI follows prompt instructions accurately
- JSON output is parseable
- Confidence scores reflect actual accuracy

---

## 7. Security Assumptions

### Data Privacy
- Images are not stored permanently on server
- API provider (Google) adheres to privacy policies
- No third parties access the images
- Local processing is secure

### Authentication
- No user authentication required (open API)
- API key protection is user's responsibility
- Frontend served over HTTP (not HTTPS in local mode)

---

## 8. Operational Assumptions

### Error Handling
- Temporary API failures are rare
- Network interruptions are handled by retry at user level
- Malformed images are caught by validation

### Performance
- Processing one image at a time is acceptable
- 3-8 second response time is tolerable
- No real-time processing requirement

---

## 9. Scope Assumptions

### Document Types
- Only driver's licenses are supported (not passports, ID cards, etc.)
- Only physical license images (not digital/PDF copies)

### Language Support
- Primary language is English
- Multi-language support relies on Gemini's capabilities
- Non-Latin scripts may have lower accuracy

### Geographic Coverage
- Licenses from major countries (US, India, UK, Australia, Canada)
- Other countries may work but are not explicitly tested

---

## 10. Future Assumptions

### Maintenance
- Gemini API remains available and pricing is acceptable
- OpenCV library continues to be maintained
- Python ecosystem remains stable

### Updates
- Code can be updated to support new license formats
- New fields can be added to schema without breaking changes
- Frontend can be enhanced independently of backend
