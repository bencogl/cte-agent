from io import BytesIO
from PyPDF2 import PdfReader
from utils.openai_client import call_openai_function

def extract_raw_text_bytes(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n\n".join(pages)

def ai_parse_pdf_bytes(content: bytes) -> dict:
    text = extract_raw_text_bytes(content)
    prompt = (
        "Sei un parser esperto di listini. Estrai questi campi:\n"
        "- codice_listino (formato XXX_YYY_ZZZ)\n"
        "- prodotto\n"
        "- data_fine_vendibilita (YYYY-MM-DD)\n"
        "- codice_offerta\n"
        "- campi_prezzo (ogni etichetta → numero)\n\n"
        f"Testo del PDF:\n{text}"
    )
    return call_openai_function("parse_listino", prompt)
