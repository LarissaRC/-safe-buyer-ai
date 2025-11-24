# Aqui você pode depois ligar com arquivos reais (DOCX/PDF) na pasta /assets/modelos/

MODELOS_BASE = [
    {
        "id": "carta_reclamacao_fornecedor",
        "categorias": ["produto_defeituoso", "atraso_entrega", "outros"],
        "descricao": "Carta formal para reclamar diretamente ao fornecedor sobre o problema.",
        "arquivo": "assets/modelos/carta_reclamacao_fornecedor.docx",
    },
    {
        "id": "reclamacao_procon",
        "categorias": [
            "produto_defeituoso",
            "serviço_não_prestado",
            "publicidade_enganosa",
            "cobrança_indevida",
        ],
        "descricao": "Modelo de texto para registrar reclamação no Procon.",
        "arquivo": "assets/modelos/reclamacao_procon.docx",
    },
    {
        "id": "peticao_juizado_especial",
        "categorias": ["produto_defeituoso", "serviço_não_prestado", "cobrança_indevida"],
        "descricao": "Modelo simplificado de petição para o Juizado Especial Cível.",
        "arquivo": "assets/modelos/peticao_juizado_especial.docx",
    },
]


def sugerir_modelos(categoria: str):
    return [m for m in MODELOS_BASE if categoria in m["categorias"]]
