from mcp_server import mcp


def main():
    """
    Entry point principal do projeto.

    Quando você roda `python main.py`, sobe o servidor MCP `e-consumidor`
    usando transporte stdio, pronto para ser conectado por ChatGPT/Claude/Copilot.
    """
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
