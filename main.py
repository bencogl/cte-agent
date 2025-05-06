from fastapi import FastAPI, UploadFile, File
from pdf_parser import extract_from_pdf
from excel_parser import parse_excel, group_by_listino, interpret_excel_group
from comparator import describe_differences
from tempfile import NamedTemporaryFile

app = FastAPI()

@app.post("/compare")
async def compare_files(pdf: UploadFile = File(...), xlsx: UploadFile = File(...)):
    with NamedTemporaryFile(delete=False) as tmp_pdf, NamedTemporaryFile(delete=False) as tmp_xlsx:
        tmp_pdf.write(await pdf.read())
        tmp_xlsx.write(await xlsx.read())

    pdf_content = extract_from_pdf(tmp_pdf.name)
    pdf_data = {
        item["Codice Listino"]: (item, {"pdf": pdf.filename})
        for item in pdf_content
    }

    xls_raw = parse_excel(tmp_xlsx.name)
    xls_grouped = group_by_listino(xls_raw)
    xls_data = {
        k[1]: interpret_excel_group(k, v)
        for k, v in xls_grouped.items()
    }

    result_text = describe_differences(pdf_data, xls_data)
    return {"response": result_text}