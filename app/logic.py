from datetime import datetime
from .storage import salvar_dados

def adicionar_transacao(dados, tipo, valor, descricao):
    transacao = {
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    dados["transacoes"].append(transacao)
    salvar_dados(dados)
