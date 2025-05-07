def format_differences(diffs):
    if not diffs:
        return "✅ Tutti i listini sono coerenti tra PDF ed Excel."
    
    messages = []
    for listino, changes in diffs.items():
        if changes == "missing_pdf":
            messages.append(f"⚠️ Il listino `{listino}` è presente nel tracciato Excel ma manca nel PDF.")
        elif changes == "missing_xls":
            messages.append(f"⚠️ Il listino `{listino}` è presente nel PDF ma manca nel tracciato Excel.")
        elif changes == "duplicate":
            messages.append(f"⚠️ Il listino `{listino}` è duplicato e non è stato elaborato.")
        elif isinstance(changes, str) and changes.startswith("error"):
            messages.append(f"❌ Errore durante l'elaborazione del listino `{listino}`: {changes[7:]}")
        else:
            changes_text = "\n".join([f"  - `{field}`: PDF = {pdf_val}, Excel = {xls_val}" for field, (pdf_val, xls_val) in changes.items()])
            messages.append(f"⚠️ Differenze trovate nel listino `{listino}`:\n{changes_text}")

    return "\n\n".join(messages)