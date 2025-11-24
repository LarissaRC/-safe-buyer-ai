import os
import time
from openai import OpenAI

client = OpenAI(api_key="SUA-CHAVE-AQUI")
MODELO_TESTADO = "ft:gpt-4o-mini-2024-07-18:personal::CfNSu6qd"

print("Fazendo upload do arquivo de teste...")
file_response = client.files.create(
    file=open("teste_data.jsonl", "rb"),
    purpose="evals"
)
FILE_ID = file_response.id
print(f"Arquivo de teste carregado: {FILE_ID}")

print("Criando a definição da avaliação...")
eval_def = client.evals.create(
    name="CDC Legal Accuracy Check",
    data_source_config={
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "pergunta": {"type": "string"},
                "resposta_ideal": {"type": "string"}
            },
            "required": ["pergunta", "resposta_ideal"]
        },
        "include_sample_schema": True
    },
    testing_criteria=[
        {
            "type": "string_check", 
            "name": "Checar se a resposta contem termos chave",
            "input": "{{ sample }}",
            "operation": "ilike",
            "reference": "%{{ item.resposta_ideal }}%" 
        }
    ]
)
EVAL_ID = eval_def.id
print(f"Eval criado com ID: {EVAL_ID}")

print(f"Iniciando rodada de avaliação no modelo {MODELO_TESTADO}...")
run = client.evals.runs.create(
    eval_id=EVAL_ID,
    name="Teste CDC Fine-Tuning V1",
    data_source={
        "type": "responses",
        "model": MODELO_TESTADO,
        "input_messages": {
            "type": "template",
            "template": [
                {"role": "system", "content": "Você é um especialista em Direito do Consumidor brasileiro."},
                {"role": "user", "content": "{{ item.pergunta }}"}
            ]
        },
        "source": {
            "type": "file_id",
            "id": FILE_ID
        }
    }
)

print("-" * 30)
print(f"Run de Avaliação iniciada: {run.id}")
print(f"Status: {run.status}")
print("-" * 30)

# Monitoramento
print("Aguardando resultados...")
while True:
    run_status = client.evals.runs.retrieve(
        eval_id=EVAL_ID,
        run_id=run.id
    )
    print(f"Status atual: {run_status.status}")
    
    if run_status.status in ["completed", "failed", "cancelled"]:
        if run_status.status == "completed":
            print("\nRESULTADOS:")
            print(run_status) 
            print(f"\nVeja o relatório completo na URL: {run_status.report_url}")
        else:
            print("A avaliação falhou ou foi cancelada.")
        break
    time.sleep(5)