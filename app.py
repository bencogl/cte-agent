# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from parsers.pdf_parser import ai_parse_pdf_bytes
from parsers.xls_parser import extract_xls_data_bytes
from comparator.compare import compare_listini
from comparator.report import generate_report

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/extract_pdf_ai")
async def api_extract_pdf_ai(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Devi caricare un PDF")
    content = await file.read()
    return ai_parse_pdf_bytes(content)

@app.post("/extract_xls")
async def api_extract_xls(file: UploadFile = File(...)):
    if not (file.filename.lower().endswith(".xls") or file.filename.lower().endswith(".xlsx")):
        raise HTTPException(400, "Devi caricare un file Excel")
    content = await file.read()
    return extract_xls_data_bytes(content)

@app.post("/compare")
async def api_compare(body: dict):
    # body = { "pdf": {...}, "xls": {...} }
    return compare_listini(body["pdf"], body["xls"])

@app.post("/report")
async def api_report(body: dict):
    # body = { "results": [ {status, ...}, … ] }
    return generate_report(body["results"])
