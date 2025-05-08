def compare_listini(pdf: dict, xls: dict) -> dict:
    diffs = {}
    for k in set(pdf) | set(xls):
        a, b = pdf.get(k), xls.get(k)
        if a != b:
            diffs[k] = {"pdf": a, "xls": b}
    status = "ok" if not diffs else "ko"
    return {"status": status, "diffs": diffs}
