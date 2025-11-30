"""
Script auxiliar/experimental para monitorar o status de um job de fine-tuning.
Fora do fluxo de produção; exige configuração manual de JOB_ID e chave.
"""

from openai import OpenAI
import time
import os

client = OpenAI(api_key="SUA-CHAVE-AQUI")  # placeholder controlado, não committe chave real

# JOB_ID = "ftjob-XXXXXXXXXXXXXXXXXXXXXXXX"
JOB_ID = "ftjob-4YsS9JOpIwd5hak7A9NcYRkm"

def check_status(job_id):
    while True:
        try:
            job = client.fine_tuning.jobs.retrieve(job_id)
            status = job.status
            
            print(f"Status atual: {status.upper()}")
            
            if status == "succeeded":
                print("-" * 30)
                print(" Fine-tuning concluído com sucesso! ")
                print(f"Nome do modelo personalizado: {job.fine_tuned_model}")
                print("-" * 30)
                break
            
            elif status == "failed":
                print("-" * 30)
                print(" O fine-tuning falhou.")
                print(f"Erro: {job.error}")
                print("-" * 30)
                break
            
            elif status == "cancelled":
                print("Job cancelado.")
                break
                
            else:
                events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id, limit=1)
                if events.data:
                    print(f"Último evento: {events.data[0].message}")
                
                print("Aguardando 30 segundos para próxima verificação...")
                time.sleep(30)
                
        except Exception as e:
            print(f"Erro ao verificar status: {e}")
            break

if __name__ == "__main__":
    if JOB_ID == "ftjob-XXXXXXXXXXXXXXXXXXXXXXXX":
        print("Erro: Você precisa substituir a variável JOB_ID pelo ID real do seu fine-tuning.")
    else:
        print(f"Monitorando Job: {JOB_ID}")
        check_status(JOB_ID)
