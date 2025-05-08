# app.py

import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from parsers.pdf_parser import ai_parse_pdf_bytes
from parsers.xls_parser import extract_xls_data_bytes
from comparator.compare import compare_listini
from comparator.report import generate_report

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

class FileBase64Payload(BaseModel):
    file: str  # base64 del contenuto del PDF o XLS

@app.post("/extract_pdf_ai")
async def api_extract_pdf_ai(payload: FileBase64Payload):
    try:
        pdf_bytes = base64.b64decode(payload.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Impossibile decodificare il base64")
    try:
        data = ai_parse_pdf_bytes(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel parsing PDF: {e}")
    return {"data": data}


@app.post("/extract_xls")
async def api_extract_xls(payload: FileBase64Payload):
    try:
        xls_bytes = base64.b64decode(payload.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Impossibile decodificare il base64")
    try:
        data = extract_xls_data_bytes(xls_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel parsing Excel: {e}")
    return {"data": data}


class CompareRequest(BaseModel):
    pdf: dict
    xls: dict

@app.post("/compare")
async def api_compare(req: CompareRequest):
    try:
        return compare_listini(req.pdf, req.xls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel confronto: {e}")

class ReportRequest(BaseModel):
    results: list

@app.post("/report")
async def api_report(req: ReportRequest):
    try:
        return generate_report(req.results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione report: {e}")
