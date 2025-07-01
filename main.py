import argparse
import os
import pandas as pd
from dotenv import load_dotenv
import uvicorn
from api import app as fastapi_app # Importa a instância do FastAPI

from src.etl.pipeline import executar_pipeline
from src.rag_builder import inicializar_rag
from src.rag.rag_core import responder_pergunta_rag
from src.rag.chat_history import limpar_contexto
from src.etl.reporter import gerar_grafico_automatico

def handle_plot_command(command: str):
    partes = command.split(maxsplit=2) # Divide em no máximo 3 partes: /plot, caminho, o_que_plotar
    if len(partes) < 2:
        print("Uso incorreto. Forneça o caminho do arquivo e o que deve ser plotado. Ex: /plot chat_outputs/dados/arquivo.csv diferenca do hp")
        return

    caminho_arquivo = partes[1]
    o_que_plotar = partes[2] if len(partes) > 2 else None # Pega o que deve ser plotado, se existir

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo não encontrado em '{caminho_arquivo}'")
        return

    try:
        if caminho_arquivo.endswith('.csv'):
            dados = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
        elif caminho_arquivo.endswith('.json'):
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                import json
                dados = json.load(f)
        else:
            print("Erro: Formato de arquivo não suportado. Use .csv ou .json")
            return
        
        # Passa o_que_plotar para a função de geração de gráfico
        caminho_grafico = gerar_grafico_automatico(dados, especificacao_plot=o_que_plotar)
        if caminho_grafico:
            print(f"[SUCESSO] Gráfico gerado e salvo em: {caminho_grafico}")
        else:
            print("[INFO] Não foi possível gerar o gráfico. Verifique a especificação ou o arquivo.")
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")

def chat_interativo():
    """Inicia um chat interativo com a IA no terminal."""
    print("Bem-vindo ao chat interativo com a IA Pokémon! Digite 'sair' para encerrar.")
    print("Comandos especiais:")
    print("  /limpar - Limpa o histórico de conversas e dados estruturados")
    print("  /plot <caminho_do_arquivo> - Gera um gráfico a partir de um arquivo CSV ou JSON")
    print("  sair - Encerra o chat\n")
    
    vetorstore = inicializar_rag()
    if not vetorstore:
        print("Não foi possível iniciar o chat. Encerrando.")
        return

    while True:
        pergunta = input("Você: ")
        comando = pergunta.strip().lower()

        if comando in ["sair", "exit"]:
            print("Encerrando o chat. Até logo!")
            break
        elif comando == "/limpar":
            limpar_contexto()
            print("[INFO] Contexto limpo! Histórico de conversas e dados estruturados foram removidos.")
        elif comando.startswith("/plot"):
            handle_plot_command(pergunta)
        elif comando.startswith("/"):
            print(f"Comando não reconhecido: {pergunta}")
            print("Comandos disponíveis: /limpar, /plot, sair")
        else:
            responder_pergunta_rag(pergunta, vetorstore)

def main():
    """Função principal para executar o CLI."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Executa o pipeline de ETL de Pokémon ou inicia um chat interativo com a IA."
    )
    parser.add_argument(
        "acao",
        choices=["pipeline", "chat", "serve_api"],
        help="A ação a ser executada: 'pipeline' para processar os dados, 'chat' para conversar com a IA, 'serve_api' para iniciar o servidor FastAPI."
    )

    args = parser.parse_args()

    if args.acao == "pipeline":
        print("Executando o pipeline de ETL...")
        executar_pipeline()
        print("Pipeline de ETL concluído.")
    elif args.acao == "chat":
        chat_interativo()
    elif args.acao == "serve_api":
        print("Iniciando servidor FastAPI...")
        uvicorn.run(fastapi_app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()