from PyPDF2 import PdfReader
from utils.openai_client import call_openai_function

def extract_raw_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n\n".join(page.extract_text() for page in reader.pages)

def ai_parse_pdf(path: str) -> dict:
    text = extract_raw_text(path)
    prompt = (
      "Sei un parser esperto di listini. Estrai da questo testo i campi:\n"
      "- codice_listino (formato XXX_YYY_ZZZ)\n"
      "- prodotto\n"
      "- data_fine_vendibilita (YYYY-MM-DD)\n"
      "- codice_offerta\n"
      "- campi_prezzo (ogni etichetta → numero)\n\n"
      f"Testo:\n{text}"
    )
    # call_openai_function invia a GPT-4 con Function Calls
    return call_openai_function("parse_listino", prompt)
