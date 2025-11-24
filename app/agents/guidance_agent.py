from app.config import BASE_MODEL_ID, client
from app.tools.modelos_documentos import sugerir_modelos

GUIDANCE_SYSTEM_PROMPT = """
Você é um assistente que transforma a análise jurídica em um passo a passo prático
para o consumidor.

Sua resposta deve ter:

1) "Plano de ação" em formato de lista numerada.
2) "Documentos importantes" (lista com o que o consumidor deve juntar).
3) "Sugestão de modelos de documentos", com nome e finalidade (ex: "Carta de Reclamação ao Fornecedor").

Fale de forma empática, clara e organizada.
Nunca prometa resultado garantido, apenas oriente possíveis caminhos.
"""


def build_guidance(queixa: str, triagem: dict, analise_juridica: str) -> str:
    modelos = sugerir_modelos(triagem.get("categoria", "outros"))

    modelos_texto = "\n".join(f"- {m['id']}: {m['descricao']}" for m in modelos) or (
        "Nenhum modelo específico sugerido para este caso."
    )

    user_content = f"""
Relato do consumidor:
{queixa}

Classificação:
{triagem}

Análise jurídica:
{analise_juridica}

Modelos de documentos disponíveis para este tipo de caso:
{modelos_texto}
"""

    completion = client.chat.completions.create(
        model=BASE_MODEL_ID,
        messages=[
            {"role": "system", "content": GUIDANCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return completion.choices[0].message.content
