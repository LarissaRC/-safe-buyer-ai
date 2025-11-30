"""
Compat layer: mantém o nome antigo `cli_mcp.py`, mas delega para a CLI oficial em
`cli.py`. Preferir rodar `python cli.py`.
"""

from cli import main


if __name__ == "__main__":
    main()
