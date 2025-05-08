# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from parsers.pdf_parser import ai_parse_pdf_bytes
from parsers.xls_parser import extract_xls_data_bytes
from comparator.compare import compare_listini
from comparator.report import generate_report
import base64
from pydantic import BaseModel

app = FastAPI()

class FilePayload(BaseModel):
    file: str
class ExcelPayload(BaseModel):
    file: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/extract_pdf_ai")
async def api_extract_pdf_ai(payload: FilePayload):
    try:
        content = base64.b64decode(payload.file)
    except Exception:
        raise HTTPException(400, "Impossibile decodificare il file base64")
    return ai_parse_pdf_bytes(content)

@app.post("/extract_xls")
async def api_extract_xls(payload: ExcelPayload):
    try:
        content = base64.b64decode(payload.file)
    except:
        raise HTTPException(400, "Impossibile decodificare il file base64")
    return extract_xls_data_bytes(content)

@app.post("/compare")
async def api_compare(body: dict):
    # body = { "pdf": {...}, "xls": {...} }
    return compare_listini(body["pdf"], body["xls"])

@app.post("/report")
async def api_report(body: dict):
    # body = { "results": [ {status, ...}, … ] }
    return generate_report(body["results"])
