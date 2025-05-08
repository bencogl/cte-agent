# app.py

import os
import requests
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from parsers.pdf_parser import ai_parse_pdf_bytes
from parsers.xls_parser import extract_xls_data_bytes
from comparator.compare import compare_listini
from comparator.report import generate_report

# Load environment and configure OpenAI client
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}


class FileIdPayload(BaseModel):
    file: str  # OpenAI file ID, e.g. "file-XYZ..."


@app.post("/extract_pdf_ai")
async def api_extract_pdf_ai(payload: FileIdPayload):
    file_id = payload.file
    if not file_id.startswith("file-"):
        raise HTTPException(status_code=400,
                            detail="Parametro 'file' non valido: deve essere un file ID")

    # 1) Recupera metadata e URL di download dal nuovo client OpenAI
    try:
        file_meta = openai.files.retrieve(file_id)
        download_url = file_meta.get("url")
        if not download_url:
            raise ValueError("Nessuna URL di download trovata per il file")
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Errore retrieving file metadata: {e}")

    # 2) Scarica i byte del PDF
    try:
        resp = requests.get(download_url,
                            headers={"Authorization": f"Bearer {openai.api_key}"})
        resp.raise_for_status()
        pdf_bytes = resp.content
    except Exception as e:
        raise HTTPException(status_code=502,
                            detail=f"Errore scaricando il file da OpenAI: {e}")

    # 3) Passa i bytes al parser AI
    try:
        data = ai_parse_pdf_bytes(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Errore nel parsing PDF: {e}")

    return {"data": data}


@app.post("/extract_xls")
async def api_extract_xls(payload: FileIdPayload):
    file_id = payload.file
    if not file_id.startswith("file-"):
        raise HTTPException(status_code=400,
                            detail="Parametro 'file' non valido: deve essere un file ID")

    # Recupera metadata e scarica il file Excel
    try:
        file_meta = openai.files.retrieve(file_id)
        download_url = file_meta.get("url")
        if not download_url:
            raise ValueError("Nessuna URL di download trovata per il file")
        resp = requests.get(download_url,
                            headers={"Authorization": f"Bearer {openai.api_key}"})
        resp.raise_for_status()
        xls_bytes = resp.content
    except Exception as e:
        raise HTTPException(status_code=502,
                            detail=f"Errore scaricando il file da OpenAI: {e}")

    # Parsing Excel
    try:
        data = extract_xls_data_bytes(xls_bytes)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Errore nel parsing Excel: {e}")

    return {"data": data}


class CompareRequest(BaseModel):
    pdf: dict
    xls: dict


@app.post("/compare")
async def api_compare(req: CompareRequest):
    try:
        result = compare_listini(req.pdf, req.xls)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Errore nel confronto: {e}")
    return result


class ReportRequest(BaseModel):
    results: list


@app.post("/report")
async def api_report(req: ReportRequest):
    try:
        report = generate_report(req.results)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Errore nella generazione report: {e}")
    return report
