"""
Orquestração do fluxo e-consumidor: triagem -> análise jurídica -> casos -> guia -> revisão.
Chamado pelo tool principal `fluxo_e_consumidor` definido em mcp_server.py.
"""

from app.agents.critic_agent import review_answer
from app.agents.guidance_agent import build_guidance
from app.agents.legal_agent import analyze_case
from app.agents.triage_agent import triage
from app.tools.jurisprudencia import buscar_casos_parecidos


def processar_queixa(queixa: str) -> tuple[str, dict]:
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

    return resposta_final, triagem
