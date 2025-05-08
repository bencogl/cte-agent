# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from parsers.pdf_parser import ai_parse_pdf_bytes
from parsers.xls_parser import extract_xls_data_bytes
from comparator.compare import compare_listini
from comparator.report import generate_report
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/extract_pdf_ai")
async def api_extract_pdf_ai(file: UploadFile = File(...)):
    # Verifica che sia un PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Devi caricare un file PDF valido")
    content = await file.read()
    try:
        data = ai_parse_pdf_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nell’AI parser: {e}")
    return {"data": data}

@app.post("/extract_xls")
async def api_extract_xls(file: UploadFile = File(...)):
    # Verifica che sia un Excel (.xls o .xlsx)
    if file.content_type not in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ):
        raise HTTPException(status_code=400, detail="Devi caricare un file Excel (.xls o .xlsx)")
    content = await file.read()
    try:
        data = extract_xls_data_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel parser Excel: {e}")
    return {"data": data}

class CompareRequest(BaseModel):
    pdf: dict
    xls: dict

@app.post("/compare")
async def api_compare(req: CompareRequest):
    try:
        result = compare_listini(req.pdf, req.xls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel confronto: {e}")
    return result

class ReportRequest(BaseModel):
    results: list

@app.post("/report")
async def api_report(req: ReportRequest):
    try:
        report = generate_report(req.results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella generazione report: {e}")
    return report
