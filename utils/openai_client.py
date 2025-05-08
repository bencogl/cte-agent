import os, openai, json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai_function(name: str, prompt: str) -> dict:
    # Configura la Function Call con il JSON schema di parse_listino
    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        functions=[{
          "name": "parse_listino",
          "parameters": {
            "type":"object",
            "properties": {
              "codice_listino": {"type":"string"},
              "prodotto": {"type":"string"},
              "data_fine_vendibilita": {"type":"string"},
              "codice_offerta": {"type":"string"},
              "campi_prezzo": {
                "type":"object",
                "additionalProperties":{"type":"number"}
              }
            },
            "required":["codice_listino","campi_prezzo"]
          }
        }],
        function_call={"name": name}
    )
    args = res.choices[0].message.function_call.arguments
    return json.loads(args)
