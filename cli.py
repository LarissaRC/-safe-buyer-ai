import asyncio
from pathlib import Path

from app.workflow.e_consumidor import processar_queixa
from openai import OpenAI
from agents import Agent, Runner
from agents.model_settings import ModelSettings
from agents.mcp import MCPServerStreamableHttp

client = OpenAI()

SERVER_NAME = "e-consumidor"
SERVER_SCRIPT = Path(__file__).resolve().parent / "mcp_server.py"


async def main() -> None:
    # 1) Criar o MCP server client (HTTP)
    mcp_server = MCPServerStreamableHttp(
        name="e-consumidor",
        params={
            "url": "http://127.0.0.1:8000/mcp",
            # timeout do HTTP para o streamable-http (request inicial / chamadas)
            "timeout": 60,           # pode ajustar pra 30, 60, 120...
            # quanto tempo o client aceita ficar sem receber mensagens do servidor
            "sse_read_timeout": 60*5 # opcional, mas bom deixar maiorzinho
        },
        cache_tools_list=True,
        # tempo de leitura da sessão MCP (é isso que vira aquele "Waited 5.0 seconds")
        client_session_timeout_seconds=60,
    )

    # 2) Conectar explícita­mente ao servidor MCP
    await mcp_server.connect()

    # 3) Criar o agente que usa esse MCP server
    JudgeAgent = Agent(
        name="Consultor automatico",
        instructions=(
            "Você é o agente julgador de casos. "
            "Quando receber uma queixa de consumidor, primeiro verifique se é realmente "
            "uma queixa relacionada ao Código de Defesa do Consumidor. "
            "Se for uma queixa válida, use a tool `processar_queixa` passando a queixa completa, "
            "e devolva ao usuário exatamente oque foi recebido como retorno"
        ),
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(
            tool_choice="auto",
        ),
    )

    try:
        print("=== e-Consumidor - Assistente Jurídico para Consumidores (via MCP) ===")
        print("Digite seu problema como consumidor. Linha em branco para sair.\n")

        while True:
            queixa = input("Relate o problema (ou ENTER para sair):\n> ")
            if not queixa.strip():
                break

            print("\nProcessando sua queixa via MCP...\n")

            # 4) Rodar o agente normalmente
            result = await Runner.run(JudgeAgent, queixa)

            # `final_output` é a resposta do agente
            print(result.final_output)
            print("\n" + "=" * 70 + "\n")

    finally:
        # 5) Limpar a conexão com o MCP server
        await mcp_server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())