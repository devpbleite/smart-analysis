"""
Interface de chat no terminal.

Separada do agente para permitir no futuro trocar
o canal de comunicação (ex: API web, Telegram, Slack)
sem alterar a lógica do agente.
"""


def run_chat(agent) -> None:

    print("\n" + "=" * 50)
    print("  🤖 Agente de Auditoria de Estoque")
    print("=" * 50)
    print("  Pergunte sobre validade, giro, receita, alertas.")
    print("  Digite 'sair' ou 'exit' para encerrar.\n")

    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando...")
            break

        if not pergunta:
            continue

        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("\n👋 Até logo!")
            break

        try:
            print("\n⏳ Processando...\n")
            resposta = agent.invoke({"input": pergunta})
            print(f"\n🤖 Agente:\n{resposta['output']}\n")
        except Exception as e:

            print(f"\n⚠️ Erro ao processar sua pergunta: {e}\n")
