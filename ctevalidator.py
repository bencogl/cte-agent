import csv
import datetime
import sys

from collections import Counter
from decimal import Decimal as D
from itertools import groupby
from pathlib import Path

from openpyxl import load_workbook
from pypdf import PdfReader

from rules import *
from natural_language_formatter import format_differences

input_dir = Path().absolute() / 'INPUT'

def toNum(s):
    return D(s.replace('.', '').replace(',', '.'))

def dictsDiff(a, b):
    return {x: (a.get(x, None), b.get(x, None)) for x in a.keys() | b.keys() if a.get(x, None) != b.get(x, None)}

def extractFromPdf(filename):
    reader = PdfReader(filename)
    return [p.extract_text().splitlines() for p in reader.pages]

def validate_files():
    '''
    FASE 1: Analisi CTE in pdf
    '''
    g001 = []
    pdf_files = input_dir.rglob('**/*.pdf')
    pdf_data = {}

    for pdf_file in pdf_files:
        try:
            fulltext = extractFromPdf(pdf_file)
            template = getInterpreter(pdf_file.name, fulltext)
            if template is None:
                pdf_data[pdf_file.name] = "missing_template"
                continue
            content = template(fulltext)
            g001.extend([[pdf_file.name, template.__name__, c] for c in content])
        except Exception as e:
            pdf_data[pdf_file.name] = f"error: {str(e)}"

    # Formattazione corretta
    def f002(filename, template, data):
        pricelist = data.get('Codice Listino', None)
        pricing = {x: y for x, y in data.items() if x not in ['Nome Listino', 'Codice Offerta']}
        other = {'pdf': filename, 'template': template, 'Nome Listino': data.get('Nome Listino', None), 'Codice Offerta': data.get('Codice Offerta', None)}
        return pricelist, pricing, other 

    g002 = [f002(*x) for x in g001]

    frequency = Counter(l for l, p, o in g002)

    for l, p, o in g002:
        if frequency[l] > 1:
            pdf_data[l] = "duplicate"
        else:
            pdf_data[l] = (p, o)         

    '''
    FASE 2: Tracciati listini in xls 
    '''
    full_data = []
    xls_data = {}

    xls_files = input_dir.rglob('*.xlsx')
    for xls_file in xls_files:
        try:
            wb = load_workbook(xls_file, data_only=True)
            wss = [x for x in wb.worksheets if x['A1'].value == 'Codice prodotto']
            datasheets = [list(ws.iter_rows(min_row=2, values_only=True)) for ws in wss]
            full_data.extend([(xls_file.name, ) + y for x in datasheets for y in x])
        except Exception as e:
            xls_data[xls_file.name] = f"error: {str(e)}"

    g005 = groupby(full_data, lambda x: (x[0], x[3])) #filename e listino
    g006 = ((k, v) for k, v in g005 if k[1] is not None and k[1] != '')

    def f007(k, v):
        try:
            price_name = k[1]
            other = {'xls': k[0]}
            p = {}
            for i, x in enumerate(v):
                if i == 0:
                    p['Codice Listino'] = x[3]
                    p['Prodotto'] = x[1]
                    p['Data fine vendibilità'] = '' if x[10] is None else x[10].strftime('%d/%m/%Y')                
                if x[5] is None or x[5].strip() == '':
                    p[x[2]] = D(str(x[6]))
                else:
                    p[x[2] + '|' + x[5]] = D(str(x[6]))            
                if x[7] is not None:
                    p['Percentuale prezzo fisso'] = D(str(x[7]))
            return price_name, p, other
        except Exception as e:
            return f"error: {str(e)}"

    g007 = [f007(k, v) for k, v in g006]

    frequency = Counter(l for l, p, o in g007 if isinstance(l, str))
    for l, p, o in g007:
        if isinstance(l, str):
            if frequency[l] > 1:
                xls_data[l] = "duplicate"
            else:
                xls_data[l] = (p, o)         

    '''
    FASE 3: Analisi differenze 
    '''
    diffs = {}
    all_keys = set(pdf_data.keys()) | set(xls_data.keys())
    for x in all_keys:
        if x not in pdf_data:
            diffs[x] = "missing_pdf"
        elif x not in xls_data:
            diffs[x] = "missing_xls"
        elif isinstance(pdf_data[x], str) or isinstance(xls_data[x], str):
            diffs[x] = pdf_data[x] if isinstance(pdf_data[x], str) else xls_data[x]
        else:
            diff = dictsDiff(pdf_data[x][0], xls_data[x][0])
            if diff:
                diffs[x] = diff

    return format_differences(diffs)