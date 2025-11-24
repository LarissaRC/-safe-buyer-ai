from app.workflow.e_consumidor import processar_queixa


def main():
    print("=== e-Consumidor – Assistente Jurídico para Consumidores ===")
    print("Digite seu problema como consumidor. Linha em branco para sair.\n")

    while True:
        queixa = input("Relate o problema (ou ENTER para sair):\n> ")
        if not queixa.strip():
            break

        print("\nProcessando sua queixa...\n")

        resposta_final, triagem = processar_queixa(queixa)

        print("=== Classificação da Triagem ===")
        print(f"Categoria:    {triagem.get('categoria')}")
        print(f"Subcategoria: {triagem.get('subcategoria')}")
        print(f"Urgência:     {triagem.get('urgencia')}")
        print(f"Resumo:       {triagem.get('resumo')}\n")

        print("=== Resposta do Assistente Jurídico ===")
        print(resposta_final)
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
