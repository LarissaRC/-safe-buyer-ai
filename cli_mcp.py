import asyncio
import json
from pathlib import Path

from mcp import MCPClient


async def processar_queixa_via_mcp(queixa: str):
    server_script = Path(__file__).resolve().parent / "mcp_server.py"
    config = {
        "mcpServers": {
            "e-consumidor": {
                "command": "python",
                "args": [str(server_script)],
            }
        }
    }

    client = MCPClient.from_dict(config)
    await client.create_all_sessions()

    try:
        session = client.get_session("e-consumidor")
        result = await session.call_tool(
            "fluxo_e_consumidor",
            {"queixa": queixa},
        )

        raw_text = result.content[0].text
        data = json.loads(raw_text)

        resposta_final = data["resposta_final"]
        triagem = data["triagem"]

        return resposta_final, triagem
    finally:
        await client.close_all_sessions()


def main():
    print("=== e-Consumidor - Assistente Juridico para Consumidores (via MCP) ===")
    print("Digite seu problema como consumidor. Linha em branco para sair.\n")

    while True:
        queixa = input("Relate o problema (ou ENTER para sair):\n> ")
        if not queixa.strip():
            break

        print("\nProcessando sua queixa via MCP...\n")

        resposta_final, triagem = asyncio.run(processar_queixa_via_mcp(queixa))

        print("=== Classificacao da Triagem ===")
        print(f"Categoria:    {triagem.get('categoria')}")
        print(f"Subcategoria: {triagem.get('subcategoria')}")
        print(f"Urgencia:     {triagem.get('urgencia')}")
        print(f"Resumo:       {triagem.get('resumo')}\n")

        print("=== Resposta do Assistente Juridico ===")
        print(resposta_final)
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
