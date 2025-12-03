"""
Script auxiliar/experimental para preparar e disparar um job de fine-tuning.
Não faz parte do fluxo de produção; use apenas em contexto de laboratório.
"""

from openai import OpenAI
import json
import os

client = OpenAI(api_key="SUA-CHAVE-AQUI")  # placeholder para execução local controlada

input_json_file = "new_data.json"
output_jsonl_file = "data.jsonl"

def convert_to_jsonl(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in data:
                json.dump(entry, f, ensure_ascii=False)
                f.write('\n')
        print(f"Arquivo convertido com sucesso para {output_path}")
    except FileNotFoundError:
        print(f"Erro: Arquivo {input_path} não encontrado.")
        exit()

# Verifica se precisa converter
if os.path.exists(input_json_file) and not os.path.exists(output_jsonl_file):
    convert_to_jsonl(input_json_file, output_jsonl_file)
elif not os.path.exists(output_jsonl_file):
    print(f"Erro: Nem {input_json_file} nem {output_jsonl_file} encontrados.")
    exit()

# Upload do arquivo de treinamento
print("Fazendo upload do arquivo...")
try:
    with open(output_jsonl_file, "rb") as file:
        response = client.files.create(
            file=file,
            purpose="fine-tune"
        )
    file_id = response.id
    print(f"Arquivo carregado com sucesso! ID do arquivo: {file_id}")

    # Job de fine-tuning
    print("Iniciando o job de fine-tuning...")
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-4o-mini-2024-07-18",
        hyperparameters={
            "n_epochs": 3
        }
    )
    
    print("-" * 30)
    print(f"Job criado com sucesso!")
    print(f"ID do Job: {job.id}")
    print(f"Status inicial: {job.status}")
    print("-" * 30)
    print(f"Salve o ID do Job ({job.id}) para usar no script de monitoramento.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
