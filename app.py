# app.py
import os
import requests
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from parsers.pdf_parser import ai_parse_pdf_bytes
from parsers.xls_parser import extract_xls_data_bytes
from comparator.compare import compare_listini
from comparator.report import generate_report
from dotenv import load_dotenv

load_dotenv()  # per leggere OPENAI_API_KEY da .env
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

#
# Payload che arriva da Custom GPT: contiene il file-ID
#
class FileIdPayload(BaseModel):
    file: str

@app.post("/extract_pdf_ai")
async def api_extract_pdf_ai(payload: FileIdPayload):
    file_id = payload.file
    if not file_id.startswith("file-"):
        raise HTTPException(status_code=400, detail="Parametro 'file' non valido: deve essere un file ID")
    # 1) Recupera la metadata del file da OpenAI
    try:
        file_meta = openai.File.retrieve(file_id)
        download_url = file_meta.get("url")
        if not download_url:
            raise ValueError("Nessuna URL di download trovata per il file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore retrieving file metadata: {e}")

    # 2) Scarica il contenuto binario del PDF
    try:
        resp = requests.get(download_url, headers={"Authorization": f"Bearer {openai.api_key}"})
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Errore scaricando il file da OpenAI: {e}")

    # 3) Passa i bytes al parser AI
    try:
        data = ai_parse_pdf_bytes(resp.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel parsing PDF: {e}")

    return {"data": data}


@app.post("/extract_xls")
async def api_extract_xls(payload: FileIdPayload):
    file_id = payload.file
    if not file_id.startswith("file-"):
        raise HTTPException(status_code=400, detail="Parametro 'file' non valido: deve essere un file ID")
    # metadata + download come sopra
    try:
        file_meta = openai.File.retrieve(file_id)
        download_url = file_meta.get("url")
        if not download_url:
            raise ValueError("Nessuna URL di download trovata per il file")
        resp = requests.get(download_url, headers={"Authorization": f"Bearer {openai.api_key}"})
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Errore scaricando il file da OpenAI: {e}")

    # parsing Excel
    try:
        data = extract_xls_data_bytes(resp.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel parsing Excel: {e}")

    return {"data": data}


#
# Confronto e report come prima
#
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
