import cv2
import numpy as np
from PIL import Image
import io


def preprocess_image(file_bytes: bytes) -> bytes:
    """
    Full preprocessing pipeline:
    1. Decode image bytes
    2. Convert to RGB
    3. Deskew / fix rotation
    4. Denoise
    5. Enhance contrast (CLAHE)
    6. Resize if too small
    7. Return clean JPEG bytes
    """
    img = _decode_image(file_bytes)
    img = _deskew(img)
    img = _denoise(img)
    img = _enhance_contrast(img)
    img = _resize(img)
    return _to_jpeg_bytes(img)



# STEP 1 — Decode incoming bytes to numpy array

def _decode_image(file_bytes: bytes) -> np.ndarray:
    pil_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return np.array(pil_img)



# STEP 2 — Deskew (fix rotation/skew)

def _deskew(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Threshold to find text regions
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find coordinates of all non-zero pixels
    coords = np.column_stack(np.where(thresh > 0))

    if len(coords) == 0:
        return img

    # Find minimum area rectangle around text
    angle = cv2.minAreaRect(coords)[-1]

    # Correct the angle
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90

    # Only rotate if skew is significant (more than 0.5 degrees)
    if abs(angle) < 0.5:
        return img

    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img, matrix, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


# STEP 3 — Denoise

def _denoise(img: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(
        img,
        None,
        h=10,           # filter strength for luminance
        hColor=10,      # filter strength for color
        templateWindowSize=7,
        searchWindowSize=21
    )



# STEP 4 — Enhance contrast using CLAHE

def _enhance_contrast(img: np.ndarray) -> np.ndarray:
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE only on L (lightness) channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)

    # Merge back and convert to RGB
    enhanced = cv2.merge([l_enhanced, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)



# STEP 5 — Resize if image is too small

def _resize(img: np.ndarray, min_width: int = 1024) -> np.ndarray:
    h, w = img.shape[:2]
    if w < min_width:
        scale = min_width / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    return img



# STEP 6 — Convert numpy array → JPEG bytes

def _to_jpeg_bytes(img: np.ndarray) -> bytes:
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()
