def generate_report(results: list) -> dict:
    ok = [r for r in results if r["status"]=="ok"]
    ko = [r for r in results if r["status"]=="ko"]
    text = (
      f"Totale: {len(results)} listini\n"
      f"- OK: {len(ok)}\n"
      f"- Con discrepanze: {len(ko)}\n"
    )
    return {"summary": text, "details": results}
