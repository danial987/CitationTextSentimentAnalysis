from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_file):
    """
    Extract text from the uploaded PDF file.
    """
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text.strip() + "\n"
    return text.strip()
