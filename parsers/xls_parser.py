import pandas as pd

def extract_xls_data(path: str) -> dict:
    # legge tutti i fogli, filtra quello corretto e restituisce JSON
    dfs = pd.read_excel(path, sheet_name=None)
    for name, df in dfs.items():
        if df.columns[0].lower().startswith("codice prodotto"):
            df = df.fillna("")  # pulizia base
            # gruppa per 'Codice Listino' e converte in dict
            return {
                row["Codice Listino"]: {
                    col: row[col] for col in df.columns[1:]
                }
                for _, row in df.iterrows()
            }
    raise ValueError("Foglio XLS non trovato o mal formattato")
