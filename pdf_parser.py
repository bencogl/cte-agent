from pypdf import PdfReader
from rules import getInterpreter

def extract_from_pdf(file_path):
    reader = PdfReader(file_path)
    fulltext = [page.extract_text().splitlines() for page in reader.pages]
    template = getInterpreter(file_path, fulltext)
    if not template:
        raise ValueError("Template non trovato")
    return template(fulltext)