import json
import os

CAMINHO_ARQUIVO = "data/financeiro.json"

def carregar_dados():
    if not os.path.exists(CAMINHO_ARQUIVO):
        return {"transacoes": []}
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
