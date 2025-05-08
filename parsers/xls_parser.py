import pandas as pd
from io import BytesIO

def extract_xls_data_bytes(content: bytes) -> dict:
    # legge tutti i fogli
    xls = pd.read_excel(BytesIO(content), sheet_name=None)
    for _, df in xls.items():
        cols = [c.lower() for c in df.columns]
        if cols and cols[0].startswith("codice prodotto"):
            df = df.fillna("")
            result = {}
            for _, row in df.iterrows():
                key = row["Codice Listino"]
                result[key] = {col: row[col] for col in df.columns if col != "Codice Listino"}
            return result
    raise ValueError("Foglio Excel non trovato o mal formattato")
