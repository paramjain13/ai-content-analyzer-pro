from PIL import Image
import pytesseract
import re
import os

def extract_text_from_image(file_path):
    """
    Extract text from image using OCR (Tesseract)
    Returns: (text, metadata)
    """
    try:
        # Open image
        image = Image.open(file_path)
        
        # Get image metadata
        metadata = {
            "format": image.format,
            "mode": image.mode,
            "size": f"{image.width}x{image.height}",
            "width": image.width,
            "height": image.height
        }
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Check if meaningful text was extracted
        if not text or len(text) < 20:
            raise Exception("No readable text found in image. The image might not contain text or the text is not clear enough.")
        
        # Get OCR confidence (optional but useful)
        try:
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            metadata["ocr_confidence"] = f"{round(avg_confidence, 1)}%"
        except:
            metadata["ocr_confidence"] = "N/A"
        
        return text, metadata
        
    except pytesseract.TesseractNotFoundError:
        raise Exception(
            "Tesseract OCR is not installed. "
            "Please install it: 'brew install tesseract' (macOS) or "
            "download from https://github.com/UB-Mannheim/tesseract/wiki (Windows)"
        )
    except Exception as e:
        raise Exception(f"Error reading image: {str(e)}")