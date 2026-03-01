# Edge Cases

This document outlines the key edge cases handled by the system.

---

## 1. Blurry or Low-Resolution Images
- Automatically upscaled to minimum 1024px width
- CLAHE contrast enhancement applied
- AI uses context to infer unclear text

## 2. Rotated or Skewed Images
- Automatic deskewing detects rotation angle
- Only rotates if skew exceeds 0.5 degrees
- Handles upside-down licenses

## 3. Missing or Inconsistent Fields
- All fields are optional (null if missing)
- Warnings generated for missing mandatory fields
- Handles 50+ label variations (DL No, License #, etc.)

## 4. Character Confusion
- AI distinguishes similar characters (0 vs O, 1 vs I, 5 vs S)
- Context used to resolve ambiguity
- Confidence scores indicate uncertainty

## 5. Multiple Date Formats
- All dates normalized to YYYY-MM-DD
- Handles DD/MM/YYYY, MM/DD/YYYY, text dates
- Defaults to DD/MM/YYYY when ambiguous
- All fields are optional in the schema
- Missing fields are set to `null` rather than throwing errors
- Warnings array lists all missing mandatory fields

