# app.py

from flask import Flask, request, jsonify
import os
import uuid
from cte_validator import CTEValidator

app = Flask(__name__)

UPLOAD_FOLDER = "/app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/process_files', methods=['POST'])
def process_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    # Creazione di una cartella unica per ogni sessione
    session_id = str(uuid.uuid4())
    upload_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(upload_dir, exist_ok=True)

    # Salvataggio dei file caricati
    for file in request.files.getlist('files'):
        file.save(os.path.join(upload_dir, file.filename))
    
    # Inizializzazione del validatore
    validator = CTEValidator(
        pdf_folder=upload_dir,
        xls_folder=upload_dir,
        knowledge_file="knowledge/knowledge_listini.yaml",
        log_file_prefix=f"log_{session_id}_"
    )
    
    # Esecuzione del validatore
    validator.run()
    
    # Recupero del file di log generato
    log_file = [f for f in os.listdir(upload_dir) if f.startswith(f"log_{session_id}_")]
    if not log_file:
        return jsonify({"error": "Log file not generated"}), 500
    
    # Lettura del contenuto del log
    log_path = os.path.join(upload_dir, log_file[0])
    with open(log_path, 'r') as f:
        log_content = f.read()
    
    # Ritorno del log come JSON
    return jsonify({"log": log_content})

if __name__ == "__main__":
    app.run(port=8080)
