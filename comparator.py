def describe_differences(pdf_data, xls_data):
    responses = []
    all_keys = set(pdf_data.keys()) | set(xls_data.keys())

    for key in sorted(all_keys):
        if key not in pdf_data:
            responses.append(f"Il listino `{key}` è presente nel tracciato Excel ma manca nel PDF.")
        elif key not in xls_data:
            responses.append(f"Il listino `{key}` è presente nel PDF ma manca nel tracciato Excel.")
        else:
            pdf_vals = pdf_data[key][0]
            xls_vals = xls_data[key][0]
            diffs = {k for k in pdf_vals.keys() | xls_vals.keys() if pdf_vals.get(k) != xls_vals.get(k)}
            if diffs:
                descr = "\n".join(
                    f"  - Campo `{field}`: PDF = {pdf_vals.get(field)}, Excel = {xls_vals.get(field)}"
                    for field in diffs
                )
                responses.append(f"⚠️ Differenze trovate nel listino `{key}`:\n{descr}")
            else:
                responses.append(f"✅ Il listino `{key}` è coerente tra PDF e Excel.")
    return "\n\n".join(responses)