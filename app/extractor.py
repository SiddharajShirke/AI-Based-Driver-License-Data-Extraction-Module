from google import genai
from google.genai import types
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL  = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")



# PROMPT

EXTRACTION_PROMPT = """
You are an expert forensic document analyst specializing in driver's licenses
from all countries. Your task is to extract every readable field with maximum
accuracy even from blurry, rotated, low-resolution, or partially damaged images.

═══════════════════════════════════════════
EXTRACTION RULES
═══════════════════════════════════════════

RULE 1 — OUTPUT FORMAT
- Return ONLY a valid JSON object.
- No explanation, no markdown, no code blocks, no preamble.
- Start directly with { and end with }

RULE 2 — MISSING FIELDS
- If a field is completely unreadable after all attempts, set it to null.
- NEVER guess or hallucinate a value.
- NEVER leave a field out of the JSON — always include all keys.

RULE 3 — DATE NORMALIZATION
- Normalize ALL dates to YYYY-MM-DD format.
- Handle all variations:
    05/12/1990  → 1990-12-05
    12-JAN-1990 → 1990-01-12
    12.01.1990  → 1990-01-12
    JAN 12 1990 → 1990-01-12
    12/01/90    → 1990-01-12
- If day/month is ambiguous, prefer DD/MM/YYYY interpretation.

RULE 4 — LICENSE NUMBER
- Remove ALL spaces, hyphens, special characters.
- Return only the raw alphanumeric string.
- Handle label variations:
    DL No, License No, Driving Licence No, Lic. No,
    DL#, Licence #, Driving License Number, No., ID No.

RULE 5 — GENDER
- Return "M" for male, "F" for female, null if not present.
- Handle variations: Male/Female, M/F, 1/2, Masc/Fem

RULE 6 — COUNTRY CODE
- Return 2-letter ISO country code: IN, US, UK, AU, CA, NZ, etc.
- Detect from issuing authority name, state name, or visual design.

RULE 7 — CONFIDENCE SCORES
- Rate EACH field from 0.0 to 1.0 based on how clearly you read it:
    1.0 = perfectly clear, no doubt
    0.8 = clearly readable with minor blur
    0.6 = partially readable, some characters uncertain
    0.4 = heavily blurred but partially inferred
    0.2 = mostly guessed from context
    0.0 = completely unreadable
- If confidence > 0.6 → reliability = "high"
- If confidence ≤ 0.6 → reliability = "low"

RULE 8 — WARNINGS
- List ALL mandatory fields that are missing or had confidence below 0.7.
- Format each warning as a plain string: "fieldName: reason"
- Example: "expiryDate: not visible", "address: low confidence 0.5"

RULE 9 — LABEL VARIATIONS
Recognize ALL of these label patterns:
- Name:       Full Name, Name, Holder Name, Surname/Given Name, Last/First
- DOB:        Date of Birth, D.O.B, Birth Date, DOB, Born, Dt. of Birth
- License No: DL No, License No, Lic. No, DL#, Driving Licence No, No.
- Address:    Add., Addr, Permanent Address, Residential Address
- Expiry:     Expiry, Exp, Valid Until, Valid To, Validity, Expiration Date
- Issue Date: Issue Date, Issued, Date of Issue, Issue Dt, Valid From
- Authority:  Issuing Authority, Issued By, RTO, Authority, Licensing Office

RULE 10 — BLURRY IMAGE HANDLING
- Distinguish similar characters: 0 vs O, 1 vs I vs l, 5 vs S, 8 vs B, 2 vs Z
- Use surrounding context to infer unclear characters.
- Cross-reference name against any repeated text on the license.
- Use document layout to locate fields even without visible labels.
- If a date is partially visible, infer missing parts from context.

RULE 11 — MULTI-LANGUAGE SUPPORT
- Licenses may have Hindi, Tamil, Arabic, French or other languages.
- Extract the English transliteration or translation if available.
- If only non-English text is present, transliterate it.

RULE 12 — FIELD LOCATION AWARENESS
- US licenses:    Name top-left, DOB middle, License# top-right
- Indian licenses: DL No top, Name middle, DOB bottom-left
- UK licenses:    Surname field 1, First names field 2, DOB field 3
- Australian:     Card Number top-right, DOB middle

═══════════════════════════════════════════
OUTPUT JSON STRUCTURE — STRICTLY FOLLOW
═══════════════════════════════════════════

{
  "documentType":     "driver_license",
  "fullName":         null,
  "licenseNumber":    null,
  "dateOfBirth":      null,
  "issueDate":        null,
  "expiryDate":       null,
  "gender":           null,
  "address":          null,
  "issuingAuthority": null,
  "country":          null,
  "state":            null,
  "confidenceScores": {
    "fullName":         null,
    "licenseNumber":    null,
    "dateOfBirth":      null,
    "issueDate":        null,
    "expiryDate":       null,
    "gender":           null,
    "address":          null,
    "issuingAuthority": null
  },
  "reliability": {
    "fullName":         null,
    "licenseNumber":    null,
    "dateOfBirth":      null,
    "issueDate":        null,
    "expiryDate":       null,
    "gender":           null,
    "address":          null,
    "issuingAuthority": null
  },
  "warnings": []
}

Analyze the provided driver's license image now and return the JSON.
"""



# MAIN EXTRACTION FUNCTION

def extract_license_data(image_bytes: bytes) -> dict:
    try:
        raw_response = _call_gemini(image_bytes)
        parsed       = _parse_json_response(raw_response)
        sanitized    = _sanitize_warnings(parsed)
        validated    = _add_warnings(sanitized)
        return validated

    except Exception as e:
        return _fallback_response(str(e))



# STEP 1 — Call Gemini Vision API

def _call_gemini(image_bytes: bytes) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            EXTRACTION_PROMPT
        ]
    )
    return response.text



# STEP 2 — Parse JSON from Gemini response

def _parse_json_response(raw: str) -> dict:
    cleaned = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from Gemini response: {raw[:200]}")



# STEP 3 — Sanitize warnings → always List[str]

def _sanitize_warnings(data: dict) -> dict:
    raw_warnings = data.get("warnings", [])
    clean        = []

    for w in raw_warnings:
        if isinstance(w, str):
            clean.append(w)
        elif isinstance(w, dict):
            field   = w.get("field", "unknown")
            message = w.get("message", str(w))
            clean.append(f"{field}: {message}")
        else:
            clean.append(str(w))

    data["warnings"] = clean
    return data



# STEP 4 — Add warnings for missing/low confidence

def _add_warnings(data: dict) -> dict:
    mandatory_fields = [
        "fullName", "licenseNumber", "dateOfBirth",
        "issueDate", "expiryDate", "address", "issuingAuthority"
    ]

    warnings   = data.get("warnings", [])
    confidence = data.get("confidenceScores", {})

    for field in mandatory_fields:
        value = data.get(field)
        score = confidence.get(field)

        if value is None:
            warnings.append(f"Missing field: {field}")
        elif score is not None and score < 0.7:
            warnings.append(f"Low confidence on field: {field} ({score})")

    data["warnings"] = warnings
    return data



# FALLBACK — Always return valid structure on failure

def _fallback_response(error_msg: str) -> dict:
    return {
        "documentType":     "driver_license",
        "fullName":         None,
        "licenseNumber":    None,
        "dateOfBirth":      None,
        "issueDate":        None,
        "expiryDate":       None,
        "gender":           None,
        "address":          None,
        "issuingAuthority": None,
        "country":          None,
        "state":            None,
        "confidenceScores": {
            "fullName":         None,
            "licenseNumber":    None,
            "dateOfBirth":      None,
            "issueDate":        None,
            "expiryDate":       None,
            "gender":           None,
            "address":          None,
            "issuingAuthority": None
        },
        "reliability": {
            "fullName":         None,
            "licenseNumber":    None,
            "dateOfBirth":      None,
            "issueDate":        None,
            "expiryDate":       None,
            "gender":           None,
            "address":          None,
            "issuingAuthority": None
        },
        "warnings": [f"Extraction failed: {error_msg}"]
    }
