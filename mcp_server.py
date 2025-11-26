from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from app.agents.critic_agent import review_answer
from app.agents.guidance_agent import build_guidance
from app.agents.legal_agent import analyze_case
from app.agents.triage_agent import triage
from app.tools.jurisprudencia import buscar_casos_parecidos
from app.tools.modelos_documentos import sugerir_modelos
from app.workflow.e_consumidor import processar_queixa


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
#  Tool de alto nível
# -----------------------------


@mcp.tool()
def fluxo_e_consumidor(queixa: str) -> ResultadoFluxo:
    """
    Executa o fluxo completo:
    - triagem
    - análise jurídica
    - busca de casos
    - plano de ação
    - revisão crítica

    Retorna o texto final para o consumidor + os dados estruturados de triagem.
    """
    resposta_final, triagem_raw = processar_queixa(queixa)
    return ResultadoFluxo(
        resposta_final=resposta_final,
        triagem=Triagem(**triagem_raw),
    )


# -----------------------------
#  Tools de baixo nível (opcionais)
# -----------------------------


@mcp.tool()
def triagem_queixa(queixa: str) -> Triagem:
    """
    Classifica a queixa do consumidor (categoria, subcategoria, urgência e resumo).
    """
    triagem_raw = triage(queixa)
    return Triagem(**triagem_raw)


@mcp.tool()
def analisar_caso(queixa: str, triagem: Triagem) -> str:
    """
    Gera a análise jurídica detalhada com base na triagem.
    """
    return analyze_case(queixa, triagem.model_dump())


@mcp.tool()
def plano_de_acao(queixa: str, analise_juridica: str, triagem: Triagem) -> str:
    """
    Transforma a análise jurídica em um plano de ação prático para o consumidor.
    """
    return build_guidance(queixa, analise_juridica, triagem.model_dump())


@mcp.tool()
def revisar_resposta(resposta_bruta: str) -> str:
    """
    Faz a revisão crítica da resposta antes de enviar ao consumidor final.
    """
    return review_answer(resposta_bruta)


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
    # transport="stdio" facilita integração com ChatGPT/Claude/Cursor/Copilot
    mcp.run(transport="stdio")
