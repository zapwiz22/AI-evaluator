import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from PDF bytes."""
    text = ""
    try:
        # Open the PDF from memory
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to process PDF: {str(e)}")