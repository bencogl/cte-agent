
from decimal import Decimal as D
from typing import List, Dict, Any, Optional
import re

class Field:
    def __init__(self, nome: str, posizione: Optional[List[int]] = None, valore_fisso: Optional[Any] = None, formula: Optional[str] = None):
        self.nome = nome
        self.posizione = posizione
        self.valore_fisso = valore_fisso
        self.formula = formula

    def extract_value(self, content: List[List[str]]) -> Any:
        if self.valore_fisso is not None:
            return self.valore_fisso
        
        if self.formula is not None:
            try:
                return eval(self.formula)
            except Exception as e:
                print(f"Errore nel calcolo della formula per {self.nome}: {e}")
                return None
        
        if self.posizione is not None:
            for pos in self.posizione:
                try:
                    return to_num(content[pos[0]][pos[1]])
                except (IndexError, ValueError) as e:
                    continue
        
        return None


class ListinoTemplate:
    def __init__(self, codice: str, descrizione: str, riconoscimento: Dict[str, List[str]], campi: List[Dict[str, Any]]):
        self.codice = codice
        self.descrizione = descrizione
        self.riconoscimento = riconoscimento
        self.campi = [Field(**campo) for campo in campi]

    def match(self, filename: str, content: List[List[str]]) -> bool:
        # Controllo del nome del file
        if not any(marker in filename for marker in self.riconoscimento.get("nome_file", [])):
            return False
        
        # Controllo del contenuto del file
        for pattern in self.riconoscimento.get("pattern_contenuto", []):
            if not any(re.search(pattern, line) for page in content for line in page):
                return False
        
        return True

    def parse(self, content: List[List[str]]) -> Dict[str, Any]:
        data = {"Codice Listino": self.codice}
        for campo in self.campi:
            data[campo.nome] = campo.extract_value(content)
        return data


def load_listino_templates(knowledge_file: str) -> List[ListinoTemplate]:
    import yaml
    with open(knowledge_file, 'r', encoding='utf-8') as f:
        knowledge = yaml.safe_load(f)
    
    return [ListinoTemplate(**listino) for listino in knowledge.get("listini", [])]


def to_num(s: str) -> Decimal:
    return D(s.replace('.', '').replace(',', '.'))
