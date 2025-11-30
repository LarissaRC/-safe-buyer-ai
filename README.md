# e-consumidor (safe-buyer-ai)

Assistente jurídico acadêmico focado em Direito do Consumidor brasileiro. Expõe um servidor MCP com tools para rodar o fluxo completo (triagem → análise → orientação → revisão) e uma CLI simples para testar localmente.

## Arquitetura em alto nível
- **Servidor MCP**: `main.py` inicia o servidor definido em `mcp_server.py`, que registra tools e modelos Pydantic.
- **Agentes (`app/agents/`)**: `triage_agent.py`, `legal_agent.py`, `guidance_agent.py`, `critic_agent.py`.
- **Tools (`app/tools/`)**: `jurisprudencia.py` (casos exemplo) e `modelos_documentos.py` (sugestão de modelos).
- **Workflow (`app/workflow/e_consumidor.py`)**: função `processar_queixa` encadeia triagem → análise jurídica → busca de casos → plano de ação → revisão.
- **Config (`app/config.py`)**: cliente OpenAI e seleção de modelos (usa `OPENAI_API_KEY` de ambiente).
- **Fine-tuning (`fine_tuning/`)**: scripts auxiliares/experimentais para gerar dados, subir jobs e avaliar modelos; não fazem parte do fluxo de produção.

## Como rodar o servidor MCP
1) Configure a variável de ambiente `OPENAI_API_KEY` (placeholder no código é só para desenvolvimento local).
2) Rode:
```
python main.py
```
Isso sobe o servidor `e-consumidor` via transporte `stdio`. Para depurar diretamente o arquivo do servidor, você também pode usar `python mcp_server.py`.

## Como rodar a CLI local
Com o servidor acessível (ele será iniciado automaticamente pela própria CLI quando necessário):
```
python cli.py
```
Digite sua queixa; o fluxo MCP retorna a classificação da triagem e a resposta final revisada para exibir no terminal.

## Notas sobre fine_tuning/
- Scripts `start_finetuning.py`, `check_status.py` e `eval.py` são para experimentos de ajuste fino e avaliação.
- Exigem configuração manual de chave e IDs; não são usados no fluxo MCP/CLI de produção.
