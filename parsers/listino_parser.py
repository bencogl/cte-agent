from decimal import Decimal as D
import yaml
import re

def load_listino_templates(knowledge_file):
    with open(knowledge_file, "r") as f:
        return yaml.safe_load(f)["listini"]

def to_num(s):
    return D(s.replace('.', '').replace(',', '.'))

def get_listino_parser(filename, content, knowledge_file):
    templates = load_listino_templates(knowledge_file)
    
    for template in templates:
        # Verifica se il nome del file corrisponde a uno dei pattern
        for nome_file in template.get("riconoscimento", {}).get("nome_file", []):
            if nome_file in filename:
                # Verifica se uno dei pattern di contenuto corrisponde
                patterns = template.get("riconoscimento", {}).get("pattern_contenuto", [])
                
                # Assicurati che pattern_contenuto sia una lista
                if isinstance(patterns, str):
                    patterns = [patterns]
                
                for pattern in patterns:
                    # Verifica che il pattern sia una stringa prima di usare re.search()
                    if isinstance(pattern, str) and re.search(pattern, content):
                        return ListinoParser(template)
    
    # Nessun template trovato
    return None

class ListinoParser:
    def __init__(self, config):
        self.config = config

    def parse(self, content):
        data = {}
        for campo in self.config["campi"]:
            if "valore_fisso" in campo:
                data[campo["nome"]] = campo["valore_fisso"]
            elif "posizione" in campo:
                try:
                    pos = campo["posizione"]
                    data[campo["nome"]] = to_num(content[pos[0]][pos[1]])
                except (IndexError, ValueError, KeyError):
                    print(f"Errore nel calcolo del campo {campo['nome']}")
            elif "formula" in campo:
                try:
                    data[campo["nome"]] = eval(campo["formula"])
                except Exception as e:
                    print(f"Errore nel calcolo della formula per {campo['nome']}: {e}")
        return data
