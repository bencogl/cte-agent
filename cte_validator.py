from pathlib import Path
import csv
import datetime
from pathlib import Path
from pdf_utils import extract_from_pdf
from excel_utils import extract_from_excel
from parsers import get_listino_parser

class Log:
    def __init__(self, filename):
        self.filename = filename
        self.write('File pdf', 'File xls', 'Listino', 'Tipo', 'Descrizione')

class CTEValidator:
    def __init__(self, pdf_folder, xls_folder, knowledge_file, log_file_prefix):
        self.pdf_folder = Path(pdf_folder)
        self.xls_folder = Path(xls_folder)
        self.knowledge_file = knowledge_file
        self.log = Log(f"{log_file_prefix}{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv")


    def write(self, pdf_file=None, xls_file=None, listino=None, tipo=None, desc=None):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow((pdf_file, xls_file, listino, tipo, desc))
    
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
                data = extract_from_excel(xls_file)
                data['filename'] = xls_file.name
                xls_data[data['Codice Listino']] = data
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
