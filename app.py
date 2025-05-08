from fastapi import FastAPI, HTTPException
from utils.file_utils import list_input_files
from parsers.pdf_parser import ai_parse_pdf
from parsers.xls_parser import extract_xls_data
from comparator.compare import compare_listini
from comparator.report import generate_report

app = FastAPI()

@app.get("/list_files")
def api_list_files():
    """
    Restituisce le liste di file PDF e XLSX presenti nella cartella di input.
    """
    return list_input_files()

@app.post("/extract_pdf_ai")
def api_extract_pdf(body: dict):
    """
    Estrae i dati da un PDF utilizzando l'IA.
    Body: { "path": "percorso/del/file.pdf" }
    """
    path = body.get("path")
    if not path:
        raise HTTPException(status_code=400, detail="Missing 'path' in request body")
    return ai_parse_pdf(path)

@app.post("/extract_xls")
def api_extract_xls(body: dict):
    """
    Estrae i dati da un file Excel.
    Body: { "path": "percorso/del/file.xlsx" }
    """
    path = body.get("path")
    if not path:
        raise HTTPException(status_code=400, detail="Missing 'path' in request body")
    return extract_xls_data(path)

@app.post("/compare")
def api_compare(body: dict):
    """
    Confronta i dati estratti da PDF e XLSX.
    Body: { "pdf": {...}, "xls": {...} }
    """
    pdf = body.get("pdf")
    xls = body.get("xls")
    if pdf is None or xls is None:
        raise HTTPException(status_code=400, detail="Missing 'pdf' or 'xls' in request body")
    return compare_listini(pdf, xls)

@app.post("/report")
def api_report(body: dict):
    """
    Genera un report di sintesi dai risultati di confronto.
    Body: { "results": [...] }
    """
    results = body.get("results")
    if results is None:
        raise HTTPException(status_code=400, detail="Missing 'results' in request body")
    return generate_report(results)

@app.get("/")
def read_root():
    return {"message": "Listini Validator Agent is running"}
