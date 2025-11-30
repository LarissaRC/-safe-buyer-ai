"""
Tool de jurisprudência: retorna exemplos simples de casos por categoria.
Usada para enriquecer a resposta do fluxo principal; versão mock para demo.
"""

# Versão simples só para demonstração no projeto
# No futuro, isso pode virar uma busca vetorial (RAG) de verdade.

EXEMPLOS_JURIS = [
    {
        "id": "procon_sp_produto_defeituoso_tv",
        "categoria": "produto_defeituoso",
        "resumo": "Consumidor obteve substituição de TV com defeito em menos de 90 dias.",
        "fonte": "Procon-SP",
        "link": "https://exemplo.procon.sp.gov.br/caso_tv_defeituosa",
    },
    {
        "id": "juizado_servico_nao_prestado_internet",
        "categoria": "serviço_não_prestado",
        "resumo": "Operadora condenada a ressarcir valores cobrados por serviço de internet não prestado.",
        "fonte": "Juizado Especial Cível",
        "link": "https://exemplo.tj.gov.br/caso_internet",
    },
]


def buscar_casos_parecidos(categoria: str):
    return [c for c in EXEMPLOS_JURIS if c["categoria"] == categoria]
