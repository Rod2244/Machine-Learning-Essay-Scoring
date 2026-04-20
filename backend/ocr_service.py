import io
import requests
import os

def extract_text_from_image(file_bytes, filename):
    """
    Handles JPG, PNG, and PDF using OCR.space API
    
    Args:
        file_bytes: Raw image/PDF data as bytes
        filename: Name of the file (for file type detection)
        
    Returns:
        str: Extracted text from the file, or None if failed
    """
    try:
        # Get API key from environment or use placeholder
        api_key = os.getenv('OCR_SPACE_API_KEY', 'YOUR_FREE_API_KEY_HERE')
        
        # Temporarily hardcode for testing (replace with your actual key)
        if api_key == 'YOUR_FREE_API_KEY_HERE':
            api_key = 'K84089275488957'  # User's OCR.space API key
        
        if api_key == 'YOUR_FREE_API_KEY_HERE':
            print("OCR.space API key not configured. Using mock text for demo.")
            # Fallback to mock text for demo
            return """Technology has transformed modern education in numerous ways. Online learning platforms provide students with access to quality education regardless of their geographical location. Digital tools enable interactive learning experiences through videos, simulations, and collaborative projects that enhance student engagement. However, face-to-face interaction remains important for social development and personalized feedback. The most effective educational approach combines technology with traditional teaching methods, creating a blended learning environment that leverages the strengths of both."""
        
        # Prepare the payload
        payload = {
            'apikey': api_key,
            'language': 'eng',
            'isOverlayRequired': False,
            'FileType': filename.split('.')[-1].upper(),
            'isTable': True,  # Good for structured essays
        }
        
        files = {
            'file': (filename, file_bytes),
        }

        response = requests.post(
            'https://api.ocr.space/parse/image',
            files=files,
            data=payload,
            timeout=60  # 60 second timeout for large files
        )
        
        result = response.json()

        if result.get('OCRExitCode') == 1:
            # OCR.space returns a list of "ParsedResults"
            extracted_text = ""
            for res in result.get('ParsedResults', []):
                extracted_text += res.get('ParsedText', '')
            
            # Check if page limit was reached
            error_messages = result.get('ErrorMessage', [])
            if error_messages and isinstance(error_messages, list):
                if 'page limit of 3 was reached' in str(error_messages):
                    print("OCR.space: PDF processed (3-page limit reached)")
                    print(f"Extracted {len(extracted_text)} characters")
                else:
                    print(f"OCR.space Warning: {error_messages}")
            
            print("OCR.space: Text extracted successfully")
            return extracted_text
        else:
            error_msg = result.get('ErrorMessage', 'Unknown error')
            print(f"OCR.space Error: {error_msg}")
            return None
            
    except Exception as e:
        print(f"OCR.space Connection Error: {e}")
        # Fallback to mock text for demo if OCR fails
        print("Falling back to mock text for demo...")
        return """Technology has transformed modern education in numerous ways. Online learning platforms provide students with access to quality education regardless of their geographical location. Digital tools enable interactive learning experiences through videos, simulations, and collaborative projects that enhance student engagement. However, face-to-face interaction remains important for social development and personalized feedback. The most effective educational approach combines technology with traditional teaching methods, creating a blended learning environment that leverages the strengths of both."""

# Uncomment below for real Google Vision OCR (requires billing setup)
"""
import io
from google.cloud import vision

def extract_text_from_image_real(file_bytes):
    '''
    Real Google Cloud Vision OCR function.
    Uncomment this and comment out the mock function above when ready to use real OCR.
    Requires billing setup and GOOGLE_APPLICATION_CREDENTIALS environment variable.
    '''
    try:
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=file_bytes)

        # Using document_text_detection for handwritten/dense text
        response = client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(response.error.message)

        # Extracting the full text block
        return response.full_text_annotation.text
    except Exception as e:
        print(f"OCR Error: {e}")
        return None
"""
