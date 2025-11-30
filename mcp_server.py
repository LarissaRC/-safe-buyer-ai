from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from app.tools.jurisprudencia import buscar_casos_parecidos
from app.tools.modelos_documentos import sugerir_modelos


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
def buscar_jurisprudencia_por_categoria(categoria: str) -> List[CasoJurisprudencia]:
    """
    Retorna casos de jurisprudência semelhantes para a categoria informada.
    """
    casos_raw = buscar_casos_parecidos(categoria)
    return [CasoJurisprudencia(**c) for c in casos_raw]


@mcp.tool()
def listar_modelos(categoria: str) -> List[ModeloDocumento]:
    """
    Lista modelos de documentos sugeridos para a categoria informada.
    """
    modelos_raw = sugerir_modelos(categoria)
    return [ModeloDocumento(**m) for m in modelos_raw]


if __name__ == "__main__":
    # por padrão ele sobe em http://127.0.0.1:8000/mcp
    mcp.run(transport="streamable-http")
