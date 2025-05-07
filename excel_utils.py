from openpyxl import load_workbook
from decimal import Decimal as D

def to_num(s):
    return D(s.replace('.', '').replace(',', '.'))

def extract_from_excel(filepath):
    wb = load_workbook(filepath, data_only=True)
    data = []
    for ws in wb.worksheets:
        if ws['A1'].value == 'Codice prodotto':
            for row in ws.iter_rows(min_row=2, values_only=True):
                listino_data = {
                    "filename": filepath,
                    "Codice Listino": row[3] if row[3] else "",
                    "Prodotto": row[1] if row[1] else "",
                    "Data fine vendibilità": row[10].strftime('%d/%m/%Y') if row[10] else "",
                }
                # Conversione delle colonne numeriche
                for i, cell in enumerate(row):
                    if cell is not None and isinstance(cell, (int, float, D)):
                        listino_data[f"Colonna_{i}"] = to_num(str(cell))
                data.append(listino_data)
    return data
