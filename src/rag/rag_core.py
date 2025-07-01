import os
import re
import json
import pandas as pd
from datetime import datetime
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from src.rag.chat_history import carregar_contexto_anterior, salvar_historico

def get_llm():
    """Retorna o LLM a ser usado, priorizando Groq."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if groq_api_key:
        print("Usando Groq LLM.")
        return ChatGroq(api_key=groq_api_key, model="llama3-8b-8192")
    elif openai_api_key:
        print("Groq API Key não encontrada. Usando OpenAI LLM como fallback.")
        return ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")
    else:
        print("Nenhuma API Key encontrada.")
        return None

def construir_grafo_rag(retriever, llm):
    """Constrói o grafo LangGraph para o pipeline RAG."""
    def recuperar_docs(state):
        docs = retriever.invoke(state["pergunta"])
        return {"docs": docs, **state}

    def gerar_resposta(state):
        context = "\n".join([doc.page_content for doc in state["docs"]])
        contexto_anterior = carregar_contexto_anterior()
        
        prompt_template = (
            "Responda sempre em português. Use o contexto de conversas anteriores e dados para dar respostas precisas. "
            "Se a pergunta se referir a análises anteriores, mencione isso. "
            "Para listas, contagens ou análises, retorne os dados em formato estruturado (tabelas markdown ou JSON). "
            "Se não houver dados, diga explicitamente.\n\n"
            "{contexto_anterior_str}"
            "=== DADOS ATUAIS ===\n{context}\n\n"
            "Pergunta: {pergunta}\nResposta:"
        )
        
        contexto_anterior_str = f"=== CONTEXTO ANTERIOR ===\n{contexto_anterior}\n\n" if contexto_anterior else ""
        
        prompt = prompt_template.format(
            contexto_anterior_str=contexto_anterior_str,
            context=context, 
            pergunta=state['pergunta']
        )
        
        resposta = llm.invoke(prompt)
        return {"resposta": resposta, **state}

    graph = StateGraph(dict)
    graph.add_node("input", lambda x: {"pergunta": x["pergunta"]})
    graph.add_node("retriever", recuperar_docs)
    graph.add_node("gerador", gerar_resposta)
    
    graph.set_entry_point("input")
    graph.add_edge("input", "retriever")
    graph.add_edge("retriever", "gerador")
    graph.set_finish_point("gerador")
    
    return graph.compile()

def tentar_extrair_dados(resposta_texto: str):
    # Extrai tabelas markdown
    try:
        padrao_tabela = r"((?:^\|.*\|$\n)+)"
        blocos_tabela = re.findall(padrao_tabela, resposta_texto, re.MULTILINE)
        dataframes = []
        if blocos_tabela:
            for bloco in blocos_tabela:
                linhas = [ln.strip() for ln in bloco.strip().split('\n')]
                if len(linhas) < 2: continue
                cabecalho = [h.strip() for h in linhas[0].split('|') if h.strip()]
                dados_tabela = [[d.strip() for d in ln.split('|') if d.strip()] for ln in linhas[2:]]
                df = pd.DataFrame(dados_tabela, columns=cabecalho)
                dataframes.append(df)
            if dataframes:
                return dataframes[0] if len(dataframes) == 1 else dataframes
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair tabelas: {e}")

    # Extrai JSON
    try:
        match = re.search(r'```json\n(.*?)```', resposta_texto, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass

    return None

def salvar_dados_estruturados(dados):
    DADOS_DIR = "chat_outputs/dados"
    os.makedirs(DADOS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if isinstance(dados, list) and all(isinstance(d, pd.DataFrame) for d in dados):
        caminhos = []
        for i, df in enumerate(dados):
            caminho = os.path.join(DADOS_DIR, f"dados_{timestamp}_part{i+1}.csv")
            df.to_csv(caminho, index=False, sep=';', encoding='utf-8')
            caminhos.append(caminho)
        return caminhos

    caminho = None
    if isinstance(dados, pd.DataFrame):
        caminho = os.path.join(DADOS_DIR, f"dados_{timestamp}.csv")
        dados.to_csv(caminho, index=False, sep=';', encoding='utf-8')
    elif isinstance(dados, (list, dict)):
        caminho = os.path.join(DADOS_DIR, f"dados_{timestamp}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            
    return caminho

def responder_pergunta_rag(pergunta: str, vetorstore):
    llm = get_llm()
    if not llm or not vetorstore:
        print("Erro: LLM ou Vector Store não inicializado.")
        return None # Retorna None em caso de erro

    retriever = vetorstore.as_retriever(search_kwargs={"k": 25})
    grafo = construir_grafo_rag(retriever, llm)
    resultado = grafo.invoke({"pergunta": pergunta})
    
    if "resposta" in resultado and hasattr(resultado["resposta"], 'content'):
        resposta_texto = resultado["resposta"].content
        print("\nResposta:\n") # Manter o print para logs, se necessário
        print(resposta_texto) # Manter o print para logs, se necessário
        salvar_historico(pergunta, resposta_texto)
        dados_estruturados = tentar_extrair_dados(resposta_texto)
        if dados_estruturados is not None:
            caminho_dados = salvar_dados_estruturados(dados_estruturados)
            if caminho_dados:
                print(f"\n[INFO] Dados estruturados extraídos e salvos em: {caminho_dados}")
        return resposta_texto # Retorna a resposta
    else:
        print("Não foi possível gerar uma resposta.")
        return None # Retorna None se não houver resposta
