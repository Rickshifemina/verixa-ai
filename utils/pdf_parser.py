import pdfplumber
from io import BytesIO

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    text = ""
    try:
        # Handle both file paths and file objects
        if isinstance(file, str):
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        else:
            # For uploaded file objects
            with pdfplumber.open(BytesIO(file.read())) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
    except Exception as e:
        text = f"Error extracting PDF: {str(e)}"
    return text 