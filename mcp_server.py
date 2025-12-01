from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from app.tools.jurisprudencia import buscar_casos_parecidos
from app.tools.modelos_documentos import sugerir_modelos

from app.agents.critic_agent import review_answer
from app.agents.guidance_agent import build_guidance
from app.agents.legal_agent import analyze_case
from app.agents.triage_agent import triage
from app.tools.jurisprudencia import buscar_casos_parecidos

# -----------------------------
#  Pydantic models (structured)
# -----------------------------

class Triagem(BaseModel):
    categoria: str
    subcategoria: Optional[str] = None
    urgencia: Optional[str] = None
    resumo: Optional[str] = None
    

class CasoJurisprudencia(BaseModel):
    id: str
    categoria: str
    resumo: str
    fonte: str
    link: str


class ModeloDocumento(BaseModel):
    id: str
    categorias: List[str]
    descricao: str
    arquivo: str


class ResultadoFluxo(BaseModel):
    resposta_final: str
    triagem: Triagem


# Servidor MCP que expõe os componentes do fluxo jurídico
mcp = FastMCP(name="e-consumidor", json_response=True)

# -----------------------------
#  Tools ligadas a dados externos
# -----------------------------

@mcp.tool()
def processar_queixa(queixa: str) -> str:
    """
    Processa queixa de usuario
    """
    # 2. Triagem
    triagem = triage(queixa)

    # 3. Análise jurídica
    analise = analyze_case(queixa, triagem)

    # MCP: buscar casos parecidos (exemplo simples)
    casos = buscar_casos_parecidos(triagem.get("categoria", "outros"))
    casos_txt = ""
    if casos:
        casos_txt += "\n\n=== Exemplos de casos semelhantes ===\n"
        for c in casos:
            casos_txt += f"- ({c['fonte']}) {c['resumo']} [ver mais: {c['link']}]\n"

    # 4. Orientação prática
    guia = build_guidance(queixa, triagem, analise)

    resposta_bruta = f"""
=== Análise Jurídica ===
{analise}

{casos_txt}

=== Plano de Ação Sugerido ===
{guia}
"""

    # 5. Revisão crítica
    resposta_final = review_answer(resposta_bruta)

    # 6. mostrando a classificação
    print("=== Classificação da Triagem ===")
    print(f"Categoria:    {triagem.get('categoria')}")
    print(f"Subcategoria: {triagem.get('subcategoria')}")
    print(f"Urgência:     {triagem.get('urgencia')}")
    print(f"Resumo:       {triagem.get('resumo')}\n")
    print("=== Resposta do Assistente Jurídico ===")

    return resposta_final


#@mcp.tool()
#def buscar_jurisprudencia_por_categoria(categoria: str) -> List[CasoJurisprudencia]:
#    """
#    Retorna casos de jurisprudência semelhantes para a categoria informada.
#    """
#    casos_raw = buscar_casos_parecidos(categoria)
#    return [CasoJurisprudencia(**c) for c in casos_raw]


#@mcp.tool()
#def listar_modelos(categoria: str) -> List[ModeloDocumento]:
#    """
#    Lista modelos de documentos sugeridos para a categoria informada.
#    """
#    modelos_raw = sugerir_modelos(categoria)
#    return [ModeloDocumento(**m) for m in modelos_raw]


if __name__ == "__main__":
    # por padrão ele sobe em http://127.0.0.1:8000/mcp
    mcp.run(transport="streamable-http")
