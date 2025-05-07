from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from cte_validator import CTEValidator

app = FastAPI()

# Configurazione della cartella di upload
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Abilitazione CORS (opzionale, se vuoi permettere richieste da altre origini)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_files")
async def process_files(files: list[UploadFile] = File(...)):
    # Creazione di una cartella unica per ogni sessione
    session_id = str(uuid.uuid4())
    upload_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(upload_dir, exist_ok=True)

    # Salvataggio dei file caricati
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    
    # Inizializzazione del validatore
    try:
        validator = CTEValidator(
            pdf_folder=upload_dir,
            xls_folder=upload_dir,
            knowledge_file="knowledge_listini.yaml",
            log_file_prefix=f"log_{session_id}_"
        )
        # Esecuzione del validatore
        validator.run()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    # Recupero del file di log generato
    log_file = [f for f in os.listdir(upload_dir) if f.startswith(f"log_{session_id}_")]
    if not log_file:
        raise HTTPException(status_code=500, detail="Log file not generated")
    
    # Lettura del contenuto del log
    log_path = os.path.join(upload_dir, log_file[0])
    with open(log_path, 'r') as f:
        log_content = f.read()
    
    # Ritorno del log come JSON strutturato
    return JSONResponse(content={"session_id": session_id, "log": log_content})

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
