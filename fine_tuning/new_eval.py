import os
import json
from openai import OpenAI
from tqdm import tqdm

# --- CONFIGURAÇÃO ---
client = OpenAI(api_key="SUA-CHAVE-AQUI")

# Seus Modelos
MODELO_FINE_TUNED = "ft:gpt-4o-mini-2024-07-18:personal::CikOLzaf"
MODELO_BASE = "gpt-4o-mini"
MODELO_JUIZ = "gpt-4o"

# Prompt do Sistema (igual para ambos os competidores)
SYSTEM_PROMPT = """
Você é um advogado virtual especializado em Direito do Consumidor (CDC brasileiro).

Sua resposta SEMPRE deve conter:
1) Um resumo claro do caso.
2) Os artigos do Código de Defesa do Consumidor (CDC) aplicáveis (cite o número e um resumo).
3) Explicação dos direitos do consumidor em linguagem simples, para leigo.

Quando não tiver certeza absoluta, deixe isso claro ("em tese", "em geral", "normalmente").
Sempre responda em português do Brasil.
"""
# Dados de Teste (Pergunta + Gabarito)
dados_teste = [
    {
        "pergunta": "Qual o prazo para reclamar de vício oculto?",
        "gabarito": "Segundo o § 3º do Art. 26, tratando-se de vício oculto, o prazo decadencial inicia-se no momento em que ficar evidenciado o defeito."
    },
    {
        "pergunta": "O fornecedor pode vender produto que sabe ser perigoso?",
        "gabarito": "Não. O Art. 10 proíbe colocar no mercado de consumo produto ou serviço que sabe ou deveria saber apresentar alto grau de nocividade ou periculosidade à saúde ou segurança."
    },
    {
        "pergunta": "O comerciante responde pelo defeito do produto?",
        "gabarito": "Conforme o Art. 13, o comerciante é responsável quando: I - o fabricante/importador não puderem ser identificados; II - o produto não tiver identificação clara; ou III - não conservar adequadamente produtos perecíveis."
    },
    {
        "pergunta": "O que é publicidade enganosa?",
        "gabarito": "Segundo o § 1° do Art. 37, é qualquer modalidade de informação ou comunicação de caráter publicitário, inteira ou parcialmente falsa, ou que por omissão seja capaz de induzir em erro o consumidor."
    },
    {
        "pergunta": "Qual o prazo para o fornecedor sanar um vício no produto?",
        "gabarito": "O § 1º do Art. 18 estipula o prazo máximo de trinta dias para o vício ser sanado."
    },
    {
        "pergunta": "O desconhecimento do vício exime o fornecedor de responsabilidade?",
        "gabarito": "Não. O Art. 23 afirma que a ignorância do fornecedor sobre os vícios de qualidade por inadequação dos produtos e serviços não o exime de responsabilidade."
    },
    {
        "pergunta": "Os serviços públicos essenciais podem ser interrompidos?",
        "gabarito": "Não. O Art. 22 obriga os órgãos públicos e concessionárias a fornecer serviços adequados, eficientes, seguros e, quanto aos essenciais, contínuos."
    },
    {
        "pergunta": "Quem responde pelos danos causados por defeitos de fabricação?",
        "gabarito": "Segundo o Art. 12, o fabricante, o produtor, o construtor (nacional ou estrangeiro) e o importador respondem, independentemente da existência de culpa, pela reparação dos danos."
    },
    {
        "pergunta": "O que caracteriza um produto defeituoso?",
        "gabarito": "Conforme o § 1º do Art. 12, o produto é defeituoso quando não oferece a segurança que dele legitimamente se espera, considerando sua apresentação, uso e riscos esperados, e a época de circulação."
    },
    {
        "pergunta": "O que é publicidade abusiva?",
        "gabarito": "Conforme o § 2º do Art. 37, é abusiva a publicidade discriminatória, que incite à violência, explore o medo ou a superstição, se aproveite da deficiência de julgamento da criança, desrespeite valores ambientais ou induza a comportamento prejudicial."
    }
]

def gerar_resposta(modelo, pergunta):
    """Gera resposta de um modelo específico"""
    try:
        response = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": pergunta}
            ],
            temperature=0.1 
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"

def juiz_comparativo(pergunta, gabarito, resp_ft, resp_base):
    """GPT-4o decide qual resposta é melhor"""
    
    prompt_juiz = f"""
    Você é um Juiz Jurídico Sênior comparando dois assistentes de IA sobre o Código de Defesa do Consumidor (CDC).

    ### DADOS DO CASO
    Pergunta: "{pergunta}"
    Gabarito Oficial: "{gabarito}"

    ### RESPOSTAS DOS COMPETIDORES
    Modelo A (Fine-Tuned): "{resp_ft}"
    Modelo B (Base): "{resp_base}"

    ### TAREFA
    Avalie qual modelo foi melhor considerando:
    1. **Precisão Legal:** A resposta está correta segundo o CDC e o gabarito?
    2. **Citação:** O modelo citou corretamente o Artigo/Inciso (se o gabarito exigir)?
    3. **Concisão e Estilo:** O modelo foi direto e técnico (estilo jurídico) ou prolixo?

    Retorne um JSON com:
    - "vencedor": "A", "B" ou "Empate"
    - "melhor_citacao": "A", "B" ou "Nenhum" (quem citou a lei corretamente?)
    - "justificativa": "Explique brevemente por que um venceu o outro."
    """

    response = client.chat.completions.create(
        model=MODELO_JUIZ,
        messages=[{"role": "user", "content": prompt_juiz}],
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

# --- EXECUÇÃO ---
print(f"Iniciando Batalha: {MODELO_FINE_TUNED} vs {MODELO_BASE}\n")

placar = {"A": 0, "B": 0, "Empate": 0}
resultados_detalhados = []

for i, caso in enumerate(tqdm(dados_teste)):
    # 1. Gerar respostas
    resp_ft = gerar_resposta(MODELO_FINE_TUNED, caso["pergunta"])
    resp_base = gerar_resposta(MODELO_BASE, caso["pergunta"])
    
    # 2. Julgar
    veredicto = juiz_comparativo(caso["pergunta"], caso["gabarito"], resp_ft, resp_base)
    
    # 3. Computar placar
    vencedor = veredicto["vencedor"]
    placar[vencedor] += 1
    
    resultados_detalhados.append({
        "id": i+1,
        "pergunta": caso["pergunta"],
        "resp_ft": resp_ft,
        "resp_base": resp_base,
        "veredicto": veredicto
    })

# --- RELATÓRIO FINAL ---
print("\n" + "="*40)
print("PLACAR FINAL DA BATALHA")
print("="*40)
print(f"Modelo Fine-Tuned (A): {placar['A']} vitórias")
print(f"Modelo Base (B):       {placar['B']} vitórias")
print(f"Empates:               {placar['Empate']}")
print("-" * 40)

if placar['A'] > placar['B']:
    print("CONCLUSÃO: O Fine-Tuning melhorou o modelo!")
elif placar['B'] > placar['A']:
    print("CONCLUSÃO: O Modelo Base ainda é superior. O Fine-Tuning precisa de ajustes.")
else:
    print("CONCLUSÃO: Desempenho similar. Talvez precise de mais dados de treino.")

with open("batalha_modelos.json", "w", encoding="utf-8") as f:
    json.dump(resultados_detalhados, f, ensure_ascii=False, indent=2)
print("\nDetalhes salvos em 'batalha_modelos.json'")