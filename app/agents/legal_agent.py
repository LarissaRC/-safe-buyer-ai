"""
Agente jurídico: gera análise textual baseada na triagem e no relato.
Executado após triagem no fluxo principal.
"""

from app.config import LEGAL_MODEL_ID, client

LEGAL_SYSTEM_PROMPT = """
Você é um advogado virtual especializado em Direito do Consumidor (CDC brasileiro).

Sua resposta SEMPRE deve conter:
1) Um resumo claro do caso.
2) Os artigos do Código de Defesa do Consumidor (CDC) aplicáveis (cite o número e um resumo).
3) Explicação dos direitos do consumidor em linguagem simples, para leigo.
4) Observação de que sua resposta é informativa e não substitui um advogado humano.

Quando não tiver certeza absoluta, deixe isso claro ("em tese", "em geral", "normalmente").
Sempre responda em português do Brasil.
"""


def analyze_case(queixa: str, triagem: dict) -> str:
    content_user = f"""
Relato do consumidor:
{queixa}

Classificação da triagem:
- categoria: {triagem.get('categoria')}
- subcategoria: {triagem.get('subcategoria')}
- urgencia: {triagem.get('urgencia')}
- resumo: {triagem.get('resumo')}
"""
    completion = client.chat.completions.create(
        model=LEGAL_MODEL_ID,
        messages=[
            {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
            {"role": "user", "content": content_user},
        ],
    )
    return completion.choices[0].message.content
