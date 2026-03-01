from pydantic import BaseModel, field_validator
from typing import Optional, Dict, List, Any


class ConfidenceScores(BaseModel):
    fullName: Optional[float] = None
    licenseNumber: Optional[float] = None
    dateOfBirth: Optional[float] = None
    issueDate: Optional[float] = None
    expiryDate: Optional[float] = None
    gender: Optional[float] = None
    address: Optional[float] = None
    issuingAuthority: Optional[float] = None


class DriverLicenseResponse(BaseModel):
    documentType: str = "driver_license"
    fullName: Optional[str] = None
    licenseNumber: Optional[str] = None
    dateOfBirth: Optional[str] = None
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    issuingAuthority: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    confidenceScores: ConfidenceScores = ConfidenceScores()
    warnings: List[str] = []

    @field_validator("address", mode="before")
    @classmethod
    def flatten_address(cls, v: Any) -> Optional[str]:
        """
        If Gemini returns address as a nested dict,
        flatten it into a single string.
        """
        if isinstance(v, dict):
            parts = [
                v.get("street", ""),
                v.get("city", ""),
                v.get("state", ""),
                v.get("zip", ""),
                v.get("country", "")
            ]
            return ", ".join(p for p in parts if p)
        return v

    @field_validator("gender", mode="before")
    @classmethod
    def normalize_gender(cls, v: Any) -> Optional[str]:
        """
        Normalize gender to M or F only.
        """
        if isinstance(v, str):
            v = v.strip().upper()
            if v in ["M", "MALE"]:
                return "M"
            if v in ["F", "FEMALE"]:
                return "F"
        return None

    @field_validator("confidenceScores", mode="before")
    @classmethod
    def handle_confidence(cls, v: Any) -> Any:
        if v is None:
            return ConfidenceScores()
        return v
