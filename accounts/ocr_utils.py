import pytesseract
import re
from PIL import Image
from django.conf import settings

# Configure tesseract path for Windows
TESSERACT_PATH = getattr(settings, 'TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_aadhaar_no(image_path):
    """
    Extracts 12-digit Aadhaar number using OCR and Regex.
    Pattern: XXXX XXXX XXXX or XXXXXXXXXXXX
    """
    if not getattr(settings, 'ENABLE_TESSERACT', True):
        return "123456789012" # Simulated fallback for testing/PythonAnywhere
        
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', text)
        if match:
            return match.group(0).replace(" ", "")
    except Exception as e:
        print(f"OCR Error (Aadhaar): {e}")
    return None

def extract_pan_no(image_path):
    """
    Extracts 10-character PAN number.
    Pattern: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
    """
    if not getattr(settings, 'ENABLE_TESSERACT', True):
        return "ABCDE1234F" # Simulated fallback
        
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text.upper())
        if match:
            return match.group(0)
    except Exception as e:
        print(f"OCR Error (PAN): {e}")
    return None

def verify_id_document(id_type, image_path):
    """Router for ID verification based on type."""
    if id_type == 'AADHAAR':
        return extract_aadhaar_no(image_path)
    elif id_type == 'PAN':
        return extract_pan_no(image_path)
    return None
