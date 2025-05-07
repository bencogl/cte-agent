from pypdf import PdfReader

def extract_from_pdf(filepath):
    reader = PdfReader(filepath)
    return [p.extract_text().splitlines() for p in reader.pages]
