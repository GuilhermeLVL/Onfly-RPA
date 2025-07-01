from src.rag.rag_data_loader import carregar_vetorstore, gerar_documentos_para_rag, indexar_dados

def inicializar_rag():
    """
    Inicializa o sistema RAG, garantindo que os dados estejam indexados.
    Retorna o vector store para ser usado nas perguntas.
    """
    vetorstore = carregar_vetorstore()
    if not vetorstore:
        print("Índice não encontrado. Gerando um novo...")
        documentos = gerar_documentos_para_rag()
        if documentos:
            vetorstore = indexar_dados(documentos)
        else:
            print("Não foi possível criar o índice. Verifique os dados de entrada.")
            return None
    else:
        print("Índice carregado com sucesso.")
    
    return vetorstore
