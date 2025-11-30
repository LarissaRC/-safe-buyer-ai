"""
Agente crítico: revisa e melhora a resposta consolidada antes de devolver ao usuário.
Última etapa antes de retornar o texto final ao consumidor.
"""

from app.config import BASE_MODEL_ID, client

CRITIC_SYSTEM_PROMPT = """
Você é um revisor crítico.

Recebe uma resposta completa de um assistente jurídico (com análise + plano de ação)
e deve:

- Corrigir inconsistências.
- Melhorar a clareza e a organização.
- Manter as referências ao CDC e o conteúdo jurídico coerente.
- Manter o aviso de que não substitui advogado humano.
- Remover repetições desnecessárias.

Retorne SOMENTE o texto final revisado, pronto para ser mostrado ao consumidor.
"""


def review_answer(resposta_bruta: str) -> str:
    completion = client.chat.completions.create(
        model=BASE_MODEL_ID,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
            {"role": "user", "content": resposta_bruta},
        ],
    )
    return completion.choices[0].message.content
