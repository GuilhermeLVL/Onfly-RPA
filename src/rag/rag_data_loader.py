import os
import pandas as pd
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_model():
    """Retorna o modelo de embedding da Hugging Face."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def verificar_csv_existe(caminho_csv: str = "data/relatorio.csv") -> bool:
    """Verifica se o arquivo CSV existe e não está vazio."""
    if not os.path.exists(caminho_csv):
        return False
    try:
        return os.path.getsize(caminho_csv) > 0
    except OSError:
        return False

def gerar_documentos_para_rag(caminho_csv: str = "data/relatorio.csv") -> list[Document]:
    """Gera documentos LangChain a partir do arquivo CSV estruturado."""
    if not verificar_csv_existe(caminho_csv):
        print(f"Arquivo CSV não encontrado ou vazio: {caminho_csv}")
        print("Execute o pipeline primeiro: python main.py pipeline")
        return []
    
    try:
        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8')
        documentos = []
        
        for _, row in df.iterrows():
            conteudo = (
                f"Nome: {row['Nome']}, Tipos: {row['Tipos']}, Experiencia: {row['Experiencia_Base']}, HP: {row['HP']}, "
                f"Ataque: {row['Ataque']}, Defesa: {row['Defesa']}, Categoria: {row['Categoria']}"
            )
            documentos.append(Document(page_content=conteudo))
        
        print(f"Documentos gerados a partir do CSV: {len(documentos)} Pokémon")
        return documentos
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return []

def indexar_dados(documentos: list[Document]):
    """Cria e salva um vector store FAISS com os documentos."""
    if not documentos:
        print("Nenhum documento para indexar.")
        return None
    embeddings = get_embedding_model()
    vetorstore = FAISS.from_documents(documentos, embeddings)
    vetorstore.save_local("data/indice_faiss")
    print("Vector store FAISS criado e salvo em data/indice_faiss")
    return vetorstore

def carregar_vetorstore():
    """Carrega o vector store FAISS local."""
    if not os.path.exists("data/indice_faiss"):
        return None
    embeddings = get_embedding_model()
    return FAISS.load_local("data/indice_faiss", embeddings, allow_dangerous_deserialization=True)
