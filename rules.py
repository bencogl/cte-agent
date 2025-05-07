import datetime
from decimal import Decimal as D

def toNum(s):
    return D(s.replace('.', '').replace(',', '.'))

def getInterpreter(filename, content):
    interpreter = None

    listino = content[0][-1] 
    if len(match := listino.split('_')) == 3:
        if match[1] == 'CL3PUNHYB':
            interpreter = read_CL3PUNHYB_V1 #100% indicizzato
        elif match[1] == 'SMGPSV':
            interpreter = read_SMGPSV
        elif match[1] == 'IMPHYBGAS' and 'all’intero suo fabbisogno, ad un prezzo fisso P pari a:' in content[0][1]:
            interpreter = read_IMPHYBGAS_F1
        elif match[1] == 'IMPHYBGAS' and 'all’intero suo fabbisogno, ad un prezzo fisso P pari a:' in content[0][3]:
            interpreter = read_IMPHYBGAS_F1
        elif match[1] == 'IMPHYBGAS' and 'P = PSV + fee pari a' in content[0][-24]:
            interpreter = read_IMPHYBGAS_V3
        elif match[1] == 'IMPHYBGAS' and 'Prezzo Indicizzato Gas = Prezzo PSV + Fee:' in content[0][10]:
            interpreter = read_IMPHYBGAS_V1
        elif match[1] == 'IMPHYBGAS' and 'P = PSV + fee pari a' in content[0][-21]:
            interpreter = read_IMPHYBGAS_V2
        elif match[1] == 'IMPHYB' and 'Fix' in filename:
            interpreter = read_IMPHYB_V4
        elif match[1] == 'IMPHYB' and match[0] in ['L1', 'L3', 'L9', 'L11']:
            interpreter = read_IMPHYB_V1
        elif match[1] == 'IMPHYB':
            interpreter = read_IMPHYB_V2
        elif match[1] == 'IMPHYB+':
            interpreter = read_IMPHYB_V3
        elif match[1] == 'IMPPUN':
            interpreter = read_IMPPUN            
    if interpreter is not None:
        return interpreter

    listino = content[1][-1]
    if len(match := listino.split('_')) == 3:
        if match[1] == 'NEGVAR':
            interpreter = read_NEGVAR
        if match[1] == 'NELVAR':
            interpreter = read_NELVAR_V2
        elif match[1] == 'NELPUN':
            interpreter = read_NELPUN
        elif match[1] == 'NEGFIXHYB' and '                   €/Smc (il “Prezzo Gas”), applicato ad una percentuale, indicata nella tabella che segue, del gas naturale consumato.' in content[1]:
            interpreter = read_NEGFIXHYB_V2 #hybrid
        elif match[1] == 'NEGFIXHYB':
            interpreter = read_NEGFIXHYB_V1 #100% fisso
        elif match[1] == 'NELFIXHYB': #100% fisso
            interpreter = read_NELFIXHYB_V1
        elif match[1] == 'NELVAREBUS': 
            interpreter = read_NELVAREBUS

    listino = content[1][-4]
    if len(match := listino.split('_')) == 3:
        if match[1] == 'NELFIXEBUSHYB' and 'Il Prezzo Fisso Luce, al netto delle perdite di rete' in content[1][10]:
            interpreter = read_NELFIXEBUSHYB_F1

            
    if interpreter is not None: 
        return interpreter

    listino = content[1][-2]
    if len(match := listino.split('_')) == 3:
        if match[1] == 'NELVAR':
            interpreter = read_NELVAR
        if match[1] == 'NELFIXHYB':
            interpreter = read_NELFIXHYB_V2 #hybrid
    if interpreter is not None:
        return interpreter

    if len(content[0]) >= 17 and len(match1 := content[0][-17].split('_')) == 3 and len(match2 := content[0][-12].split('_')) == 3:
        if match1[1] == 'OL1AFIX011119' and match2[1] == 'OL2AFIX011119':
            interpreter = read_OLxAFIX011119
    if interpreter is not None:
        return interpreter

    return None

def read_OLxAFIX011119(content):
    return [{'Codice Listino': content[0][-17],
             'Prodotto': 'OL1AFIX011119',
             'Data fine vendibilità': content[0][-1],
             'Codice Offerta': content[2][-3],
             
             'Nome Listino': content[0][-18],
             'Prezzo Base FASCE Listino|F1': toNum(content[0][-16]),
             'Prezzo Base FASCE Listino|F2': toNum(content[0][-15]),
             'Prezzo Base FASCE Listino|F3': toNum(content[0][-14]),
             'Fee Listino': toNum(content[0][-8])
             }, 

            {'Codice Listino': content[0][-12],
             'Prodotto': 'OL2AFIX011119',
             'Data fine vendibilità': content[0][-1],
             'Codice Offerta': content[2][-2],
             
             'Nome Listino': content[0][-18],
             'Prezzo Base FASCE Listino|F1': toNum(content[0][-11]),
             'Prezzo Base FASCE Listino|F2': toNum(content[0][-11]),
             'Prezzo Base FASCE Listino|F3': toNum(content[0][-10]),
             'Fee Listino': toNum(content[0][-7])
             }, 

            ]

def read_IMPHYBGAS_F1(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYBGAS',
             'Data fine vendibilità': content[0][-2],
             'Codice Offerta': content[2][-2],
             
             'Prezzo Gas Percentuale': toNum(content[0][-6]),
             'Percentuale prezzo fisso': 100,
             'Fee Gas Percentuale': 0,
             'Fee Gas Listino': toNum(content[0][-5]),
             'QVD Fissa Listino': toNum(content[1][-5])/12
             }
            ]

def read_IMPHYBGAS_V3(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYBGAS',
             'Data fine vendibilità': content[0][-2],
             'Codice Offerta': content[2][-2],
             
             'Prezzo Gas Percentuale': 0,
             'Percentuale prezzo fisso': 0,
             'Fee Gas Percentuale': toNum(content[0][-6]),
             'Fee Gas Listino': toNum(content[0][-5]),
             'QVD Fissa Listino': toNum(content[1][-5])/12
             }
            ]

def read_IMPHYBGAS_V1(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYBGAS',
             'Data fine vendibilità': content[0][-10],
             'Codice Offerta': content[1][-2],
             
             'Prezzo Gas Percentuale': 0,
             'Percentuale prezzo fisso': 0,
             'Fee Gas Percentuale': toNum(content[0][-7]),
             'Fee Gas Listino': toNum(content[0][-6]),
             'QVD Fissa Listino': toNum(content[0][-5])
             }
            ]

def read_IMPHYBGAS_V2(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYBGAS',
             'Data fine vendibilità': content[0][-2],
             'Codice Offerta': content[2][-2],
             
             'Prezzo Gas Percentuale': 0,
             'Percentuale prezzo fisso': 0,
             'Fee Gas Percentuale': toNum(content[0][-6]),
             'Fee Gas Listino': toNum(content[0][-5]),
             'QVD Fissa Listino': toNum(content[1][-5])/12
             }
            ]

def read_IMPPUN(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPPUN',
             'Data fine vendibilità': content[0][-19],
             'Codice Offerta': content[2][-2],
            
             'FeeMISURATORE PrimoAnno|F1': toNum(content[0][-18]),
             'FeeMISURATORE PrimoAnno|F2': toNum(content[0][-17]),
             'FeeMISURATORE PrimoAnno|F3': toNum(content[0][-16]),
             'FeeMISURATORE PrimoAnno|Totale': toNum(content[0][-15]),
             'FeeMISURATORE SecondoAnno|F1': toNum(content[0][-12]),
             'FeeMISURATORE SecondoAnno|F2': toNum(content[0][-11]),
             'FeeMISURATORE SecondoAnno|F3': toNum(content[0][-10]),
             'FeeMISURATORE SecondoAnno|Totale': toNum(content[0][-9]),
             'PCV Fissa Listino': toNum(content[0][-8]),
             }
            ]


def read_NELVAR(content):
    return [{'Codice Listino': content[1][-2],
             'Prodotto': 'NELVAR',
             'Data fine vendibilità': content[1][-14],
             'Codice Offerta': content[3][-1],
            
             'PCV Fissa Listino': toNum(content[1][-9]),
             'Fee Listino PrimoAnno': toNum(content[1][-11]),
             'FeeLuceListino perdite incluse': toNum(content[1][-1])
             }
            ]

def read_NELVAR_V2(content):
    return [{'Codice Listino': content[1][-1],
             'Prodotto': 'NELVAR',
             'Data fine vendibilità': content[1][-14],
             'Codice Offerta': content[3][-1],
            
             'PCV Fissa Listino': toNum(content[1][-9]),
             'Fee Listino PrimoAnno': toNum(content[1][-11]),
             'FeeLuceListino perdite incluse': toNum(content[1][-2])
             }
            ]

def read_NELVAREBUS(content):
    return [{'Codice Listino': content[1][-1],
             'Prodotto': 'NELVAREBUS',
             'Data fine vendibilità': content[1][-14],
             'Codice Offerta': content[3][-4],
            
             'PCV Fissa Listino': toNum(content[1][-9]),
             'Fee Listino PrimoAnno': toNum(content[1][-11]),
             'FeeLuceListino perdite incluse': toNum(content[1][-2])
             }
            ]

def read_NEGVAR(content):
    return [{'Codice Listino': content[1][-1],
             'Prodotto': 'NEGVAR',
             'Data fine vendibilità': content[1][-11],
             'Codice Offerta': content[2][-7],

             'QVD Fissa Listino': toNum(content[1][-5]),            
             'Fee Gas Listino PrimoAnno': toNum(content[1][-8]),
             'Fee Gas Listino': toNum(content[1][-7])
             }
            ]

def read_CL3PUNHYB_V1(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'CL3PUNHYB',
             'Data fine vendibilità': content[0][-2],
             'Codice Offerta': content[2][-2],

             'Nome Listino': content[0][-8],
             'Prezzo Fisso percentuale': 0,
             'Percentuale prezzo fisso': 0,
             'Fee percentuale senza perdite': toNum(content[0][-7]),
             'Fee Listino': toNum(content[0][-6])
             }
            ]


def read_SMGPSV(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'SMGPSV',
             'Data fine vendibilità': content[0][-2],
             'Codice Offerta': content[2][-2],

             'Nome Listino': toNum(content[0][-7]),
             'Fee Gas Listino PrimoAnno': toNum(content[0][-6]),
             'Fee Gas Listino': toNum(content[0][-5]),
             'QVD Fissa Listino': 'Non so'
             }
            ]

def read_IMPHYB_V1(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYB',
             'Data fine vendibilità': content[0][-18],
             'Codice Offerta': content[2][-2], 

             'Prezzo Fisso percentuale': toNum(content[0][-17]),
             'Percentuale prezzo fisso': toNum(content[0][-11][:-1]),
             'Fee Primo Anno': toNum(content[0][-12]),
             'FeeLuceListino perdite incluse': toNum(content[0][-7]),
             'PCV Fissa Listino': toNum(content[0][-9])/12
             }
            ]

def read_IMPHYB_V2(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYB',
             'Data fine vendibilità': content[0][-18],
             'Codice Offerta': content[2][-2], 

             'Prezzo Fisso percentuale': toNum(content[0][-17]),
             'Percentuale prezzo fisso': toNum(content[0][-10][:-1]),
             'Fee Primo Anno': toNum(content[0][-11]),
             'FeeLuceListino perdite incluse': toNum(content[0][-7]),
             'PCV Fissa Listino': toNum(content[0][-8])/12
             }
            ]

def read_IMPHYB_V3(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYB+',
             'Data fine vendibilità': content[0][-19],
             'Codice Offerta': content[2][-2],

             'Prezzo Fisso percentuale': toNum(content[0][-18]),
             'Percentuale prezzo fisso': toNum(content[0][-11][:-1]),
             'Fee Primo Anno': toNum(content[0][-12]),
             'FeeLuceListino perdite incluse': toNum(content[0][-7]),
             'PCV Fissa Listino': toNum(content[0][-9])
             }
            ]

def read_IMPHYB_V4(content):
    return [{'Codice Listino': content[0][-1],
             'Prodotto': 'IMPHYB',
             'Data fine vendibilità': content[0][-14],
             'Codice Offerta': content[1][-2],

             'Prezzo Fisso percentuale': toNum(content[0][-13]),
             'Percentuale prezzo fisso': 100,
             'Fee Primo Anno': 0,
             'FeeLuceListino perdite incluse': toNum(content[0][-8]),
             'PCV Fissa Listino': toNum(content[0][-11])/12
             }
            ]

def read_NELPUN(content):
    return [{'Codice Listino': content[1][-1],
             'Prodotto': 'NELPUN',
             'Data fine vendibilità': content[1][-14],
             'Codice Offerta': content[3][-1],

             'Fee Listino PrimoAnno': toNum(content[1][-11]),
             'FeeLuceListino perdite incluse': toNum(content[1][-2]),
             'PCV Fissa Listino': toNum(content[1][-9])
             }
            ]

def read_NEGFIXHYB_V1(content): #fisso
    return [{'Codice Listino': content[1][-1],
             'Prodotto': 'NEGFIXHYB',
             'Data fine vendibilità': content[1][-9],
             'Codice Offerta': content[2][-7],

             'Prezzo Gas Percentuale': toNum(content[1][-8]),
             'Percentuale prezzo fisso': 100,
             'Fee Gas Percentuale': 0,
             'Fee Gas Listino': toNum(content[1][-5]),
             'QVD Fissa Listino': toNum(content[1][-6])
             }
            ]

def read_NEGFIXHYB_V2(content): #hybrid
    return [{'Codice Listino': content[1][-1],
             'Prodotto': 'NEGFIXHYB',
             'Data fine vendibilità': content[1][-14],
             'Codice Offerta': content[2][-7],

             'Prezzo Gas Percentuale': toNum(content[1][-13]),
             'Percentuale prezzo fisso': toNum(content[1][-7][:-1]),
             'Fee Gas Percentuale': toNum(content[1][-10]),
             'Fee Gas Listino': toNum(content[1][-5]),
             'QVD Fissa Listino': toNum(content[1][-8])
             }
            ]

def read_NELFIXHYB_V1(content): #fisso
    return [{'Codice Listino': content[1][-1],
             'Prodotto': 'NELFIXHYB',
             'Data fine vendibilità': content[1][-15],
             'Codice Offerta': content[3][-1], 

             'Prezzo Fisso percentuale': toNum(content[1][-14]),
             'Percentuale prezzo fisso': 100,
             'Fee Primo Anno': 0,
             'PCV Fissa Listino': toNum(content[1][-11]),
             'FeeLuceListino perdite incluse': toNum(content[1][-2]),
             }
            ]

def read_NELFIXHYB_V2(content): #hybrid
    return [{'Codice Listino': content[1][-2],
             'Prodotto': 'NELFIXHYB',
             'Data fine vendibilità': content[1][-20],
             'Codice Offerta': content[3][-1],

             'Prezzo Fisso percentuale': toNum(content[1][-19]),
             'Percentuale prezzo fisso': toNum(content[1][-12][:-1]),
             'Fee Primo Anno': toNum(content[1][-13]),
             'PCV Fissa Listino': toNum(content[1][-9]),
             'FeeLuceListino perdite incluse': toNum(content[1][-1]),
             }
            ]

def read_NELFIXEBUSHYB_F1(content): 
    return [{'Codice Listino': content[1][-4],
             'Prodotto': 'NELFIXEBUSHYB',
             'Data fine vendibilità': content[1][-21],
             'Codice Offerta': content[3][-4],

             'Percentuale prezzo fisso': 100,
             'PrezzoMisuratore percentuale|F1': toNum(content[1][-20]),
             'PrezzoMisuratore percentuale|F2': toNum(content[1][-19]),
             'PrezzoMisuratore percentuale|F3': toNum(content[1][-18]),
             'PrezzoMisuratore percentuale|Totale': toNum(content[1][-17]),
             'Fee Primo Anno': 0,
             'PCV Fissa Listino': toNum(content[1][-11]),
             'FeeLuceListino perdite incluse': toNum(content[1][-1])
             }
            ]

