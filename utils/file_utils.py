import os
import glob
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

def get_input_folder() -> str:
    """
    Ritorna il percorso della cartella di input, prelevato dalla variabile d'ambiente.
    """
    folder = os.getenv("INPUT_FOLDER", "./INPUT")
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Cartella di input non trovata: {folder}")
    return folder

def list_input_files() -> dict:
    """
    Elenca ricorsivamente tutti i file PDF e XLSX nella cartella di input.
    Restituisce un dizionario:
      {
        "pdfs": ["/path/a/file1.pdf", ...],
        "xlss": ["/path/a/file1.xlsx", ...]
      }
    """
    folder = get_input_folder()
    pdfs = glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True)
    xlss = glob.glob(os.path.join(folder, "**", "*.xlsx"), recursive=True)
    return {"pdfs": pdfs, "xlss": xlss}

def extract_raw_text(path: str) -> str:
    """
    Estrae e concatena tutto il testo di un file PDF.
    Ritorna una singola stringa con i contenuti di tutte le pagine.
    """
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)
