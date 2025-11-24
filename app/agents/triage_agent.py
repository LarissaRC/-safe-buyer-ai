import json

from app.config import BASE_MODEL_ID, client

TRIAGE_SYSTEM_PROMPT = """
Você é um agente de triagem especializado em Direito do Consumidor (CDC brasileiro).

Sua tarefa: receber o relato do consumidor em linguagem natural e classificá-lo.

Categorias possíveis:
- produto_defeituoso
- serviço_não_prestado
- publicidade_enganosa
- cobrança_indevida
- atraso_entrega
- cancelamento_unilateral
- mau_atendimento
- outros

Responda SOMENTE em JSON, no formato:

{
  "categoria": "...",
  "subcategoria": "...",
  "urgencia": "baixa|media|alta",
  "resumo": "resumo curto do problema em 1 ou 2 frases"
}
"""


def triage(queixa: str) -> dict:
    completion = client.chat.completions.create(
        model=BASE_MODEL_ID,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": queixa},
        ],
    )
    return json.loads(completion.choices[0].message.content)
