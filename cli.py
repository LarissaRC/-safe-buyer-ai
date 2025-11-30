"""
CLI oficial para conversar com o servidor MCP e-consumidor via terminal.

Use `python cli.py` para iniciar o loop interativo que chama o tool
`fluxo_e_consumidor` exposto pelo servidor MCP em stdio.
"""

import asyncio
import json
from pathlib import Path
import asyncio
import os

from openai import OpenAI
from agents import Agent, Runner
from agents.model_settings import ModelSettings
from agents.mcp import MCPServerStreamableHttp

client = OpenAI()

async def main() -> None:
    #conectar o servidor local
    async with MCPServerStreamableHttp(
        name="MeuServidorDemo",
        params={
            "url": "http://127.0.0.1:8000/mcp",
        },
        cache_tools_list=True,
    ) as mcp_server:
        #criar um agent que usa esse MCP server
        agent = Agent(
            name="Assistente com MCP",
            instructions=(
                "Você é um asistente que usa as ferramentas do MCP "
                "para fazer contas sempre que isso ajuda."
            ),
            mcp_servers=[mcp_server],
            model_settings=ModelSettings(
                tool_choice="auto"
            ),
        )

        #Loop de chat no terminal
        print("Digite 'sair' para encerrar.\n")
        while True:
            user_input = input("Você: ")
            if user_input.lower() in ("sair", "exit", "quit"):
                break

            result = await Runner.run(agent, user_input)
            print("Agente:", result.final_output, "\n")


SERVER_NAME = "e-consumidor"
SERVER_SCRIPT = Path(__file__).resolve().parent / "mcp_server.py"


async def processar_queixa_via_mcp(queixa: str):
    """Envia a queixa para o servidor MCP local e retorna a resposta e a triagem."""
    config = {
        "mcpServers": {
            SERVER_NAME: {
                "command": "python",
                "args": [str(SERVER_SCRIPT)],
            }
        }
    }

    client = MCPClient.from_dict(config)
    await client.create_all_sessions()

    try:
        session = client.get_session(SERVER_NAME)
        result = await session.call_tool("fluxo_e_consumidor", {"queixa": queixa})

        raw_text = result.content[0].text
        data = json.loads(raw_text)

        resposta_final = data["resposta_final"]
        triagem = data["triagem"]

        return resposta_final, triagem
    finally:
        await client.close_all_sessions()


async def _run_cli() -> None:
    print("=== e-Consumidor - Assistente Jurídico para Consumidores (via MCP) ===")
    print("Digite seu problema como consumidor. Linha em branco para sair.\n")

    while True:
        queixa = input("Relate o problema (ou ENTER para sair):\n> ")
        if not queixa.strip():
            break

        print("\nProcessando sua queixa via MCP...\n")

        resposta_final, triagem = await processar_queixa_via_mcp(queixa)

        print("=== Classificação da Triagem ===")
        print(f"Categoria:    {triagem.get('categoria')}")
        print(f"Subcategoria: {triagem.get('subcategoria')}")
        print(f"Urgência:     {triagem.get('urgencia')}")
        print(f"Resumo:       {triagem.get('resumo')}\n")

        print("=== Resposta do Assistente Jurídico ===")
        print(resposta_final)
        print("\n" + "=" * 70 + "\n")


def main() -> None:
    asyncio.run(_run_cli())


if __name__ == "__main__":
    main()
