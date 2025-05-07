import os
from pathlib import Path
import csv
import datetime
from pdf_utils import extract_from_pdf
from excel_utils import extract_from_excel
from parsers import get_listino_parser

class Log:
    def __init__(self, filename):
        self.filename = filename
        
        # Creazione della directory se non esiste
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Scrivi l'intestazione del file di log
        self.write('File pdf', 'File xls', 'Listino', 'Tipo', 'Descrizione')

    def write(self, pdf_file=None, xls_file=None, listino=None, tipo=None, desc=None):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow((pdf_file, xls_file, listino, tipo, desc))

class CTEValidator:
    def __init__(self, pdf_folder, xls_folder, knowledge_file, log_file_prefix):
        self.pdf_folder = Path(pdf_folder)
        self.xls_folder = Path(xls_folder)
        self.knowledge_file = knowledge_file
        
        # Percorso del log in /tmp/logs
        log_dir = Path("/tmp/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome del file di log
        log_file = log_dir / f"{log_file_prefix}{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        print(f"Log file creato in: {log_file}")  # Debug
        
        # Creazione del log
        self.log = Log(log_file)

    def process_pdfs(self):
        pdf_data = {}
        for pdf_file in self.pdf_folder.rglob("*.pdf"):
            try:
                print(f"Processing {pdf_file.name}...")
                content = extract_from_pdf(pdf_file)
                template = get_listino_parser(pdf_file.name, content, self.knowledge_file)
                if template is None:
                    self.log.write(pdf_file.name, tipo='Errore', desc='Template non trovato')
                    continue
                data = template.parse(content)
                data['filename'] = pdf_file.name
                pdf_data[data['Codice Listino']] = data
                self.log.write(pdf_file=pdf_file.name, tipo='Elaborazione', desc='Processato con successo')
            except Exception as e:
                self.log.write(pdf_file=pdf_file.name, tipo='Errore', desc=str(e))
        return pdf_data

    def process_excels(self):
        xls_data = {}
        for xls_file in self.xls_folder.rglob("*.xlsx"):
            try:
                print(f"Processing {xls_file.name}...")
                # Estrazione dei dati come dizionario
                data_dict = extract_from_excel(xls_file)
            
            # Verifica che data_dict sia effettivamente un dizionario
                if not isinstance(data_dict, dict):
                    raise ValueError(f"Formato non valido per {xls_file.name}, atteso un dizionario")
            
            # Inserisce ogni entry in xls_data usando il Codice Listino come chiave
                for codice_listino, data in data_dict.items():
                    if not codice_listino:
                        raise ValueError(f"Il file {xls_file.name} non contiene 'Codice Listino'")
                
                # Aggiungi il nome del file ai dati
                    data['filename'] = xls_file.name
                    xls_data[codice_listino] = data
            
            # Log del successo
                self.log.write(xls_file=xls_file.name, tipo='Elaborazione', desc='Processato con successo')
            
            except Exception as e:
                self.log.write(xls_file=xls_file.name, tipo='Errore', desc=str(e))
    
        return xls_data


    def run(self):
        pdf_data = self.process_pdfs()
        xls_data = self.process_excels()

        # Analisi delle differenze
        for listino in pdf_data.keys() | xls_data.keys():
            if listino not in pdf_data:
                self.log.write(None, xls_data[listino]['filename'], listino, 'Errore', 'Non trovato pdf')
                continue
            if listino not in xls_data:
                self.log.write(pdf_data[listino]['filename'], None, listino, 'Errore', 'Non trovato xls')
                continue

            # Confronto tra PDF e Excel
            pdf_entry = pdf_data[listino]
            xls_entry = xls_data[listino]
            diffs = {k: pdf_entry[k] for k in pdf_entry if pdf_entry.get(k) != xls_entry.get(k)}
            if diffs:
                self.log.write(pdf_entry['filename'], xls_entry['filename'], listino, 'Errore', f'Differenze: {diffs}')
            else:
                self.log.write(pdf_entry['filename'], xls_entry['filename'], listino, 'Elaborazione', 'Coerenza verificata')
