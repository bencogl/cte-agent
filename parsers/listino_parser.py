from decimal import Decimal as D
import yaml
import re

def load_listino_templates(knowledge_file):
    with open(knowledge_file, "r") as f:
        return yaml.safe_load(f)

def to_num(s):
    return D(s.replace('.', '').replace(',', '.'))


def get_listino_parser(filename, content, knowledge_file):
    templates = load_listino_templates(knowledge_file)
    
    for template in templates:
        # Verifica se il nome del file corrisponde a uno dei pattern
        for nome_file in template['riconoscimento']['nome_file']:
            if nome_file in filename:
                # Verifica se uno dei pattern di contenuto corrisponde
                for pattern in template['riconoscimento']['pattern_contenuto']:
                    if re.search(pattern, content):
                        return template
    
    # Nessun template trovato
    return None

class ListinoParser:
    def __init__(self, config):
        self.config = config

    def parse(self, content):
        data = {}
        for campo in self.config['campi']:
            if 'valore_fisso' in campo:
                data[campo['nome']] = campo['valore_fisso']
            elif 'posizione' in campo:
                for pos in campo['posizione']:
                    try:
                        data[campo['nome']] = to_num(content[pos[0]][pos[1]])
                    except (IndexError, ValueError):
                        continue
            elif 'formula' in campo:
                try:
                    data[campo['nome']] = eval(campo['formula'])
                except Exception as e:
                    print(f"Errore nel calcolo della formula per {campo['nome']}: {e}")
        return data
