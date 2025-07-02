from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import pandas as pd
import json

from src.etl.pipeline import executar_pipeline
from src.rag_builder import inicializar_rag
from src.rag.rag_core import responder_pergunta_rag
from src.rag.chat_history import limpar_contexto
from src.etl.reporter import gerar_grafico_automatico

app = FastAPI()

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "http://127.0.0.1", "http://127.0.0.1:80", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variável global para armazenar o vetorstore
vetorstore_rag = None

@app.on_event("startup")
async def startup_event():
    global vetorstore_rag
    print("Inicializando RAG...")
    vetorstore_rag = inicializar_rag()
    if not vetorstore_rag:
        print("Erro ao inicializar o RAG. O chatbot pode não funcionar corretamente.")

@app.get("/status")
async def get_status():
    return {"status": "API está online!"}

@app.post("/run_pipeline")
async def run_pipeline():
    try:
        executar_pipeline()
        return {"message": "Pipeline de ETL executado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar o pipeline: {e}")

@app.post("/chat")
async def chat_endpoint(pergunta: dict):
    global vetorstore_rag
    if not vetorstore_rag:
        raise HTTPException(status_code=503, detail="Chatbot não inicializado. Execute o pipeline primeiro.")
    
    user_pergunta = pergunta.get("pergunta")
    if not user_pergunta:
        raise HTTPException(status_code=400, detail="Pergunta não fornecida.")
    
    # A função responder_pergunta_rag já imprime a resposta e salva o histórico
    # Precisamos capturar a resposta para retornar ao frontend
    # Uma forma simples é modificar responder_pergunta_rag para retornar a resposta
    # Ou usar um StringIO para capturar a saída do print
    
    # Por simplicidade, vamos assumir que responder_pergunta_rag será modificada para retornar a resposta
    # ou que o frontend fará uma nova requisição para buscar o histórico/dados
    
    resposta_llm = responder_pergunta_rag(user_pergunta, vetorstore_rag)
    if resposta_llm:
        return {"pergunta": user_pergunta, "resposta": resposta_llm}
    else:
        raise HTTPException(status_code=500, detail="Não foi possível obter uma resposta do chatbot.")

@app.post("/clear_context")
async def clear_context_endpoint():
    try:
        limpar_contexto(confirmar=False) # Não pede confirmação no backend
        return {"message": "Contexto do chatbot limpo com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar o contexto: {e}")

@app.get("/get_pipeline_report")
async def get_pipeline_report():
    caminho_relatorio = "data/relatorio.csv"
    if not os.path.exists(caminho_relatorio):
        raise HTTPException(status_code=404, detail="Relatório do pipeline não encontrado. Execute o pipeline primeiro.")
    
    try:
        df = pd.read_csv(caminho_relatorio, sep=';', encoding='utf-8')
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o relatório CSV: {e}")

@app.get("/get_pipeline_chart")
async def get_pipeline_chart():
    caminho_grafico = "data/grafico_tipos.png"
    if not os.path.exists(caminho_grafico):
        raise HTTPException(status_code=404, detail="Gráfico do pipeline não encontrado. Execute o pipeline primeiro.")
    
    return FileResponse(caminho_grafico, media_type="image/png")

@app.get("/get_chat_history")
async def get_chat_history():
    historico_path = "chat_outputs/historico.txt"
    if not os.path.exists(historico_path):
        return {"history": ""}
    with open(historico_path, "r", encoding="utf-8") as f:
        return {"history": f.read()}

@app.get("/get_chat_data")
async def get_chat_data():
    dados_dir = "chat_outputs/dados"
    if not os.path.exists(dados_dir):
        return {"data": []}
    
    all_data = []
    for filename in os.listdir(dados_dir):
        filepath = os.path.join(dados_dir, filename)
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(filepath, sep=';', encoding='utf-8')
                all_data.append({"filename": filename, "type": "csv", "content": df.to_dict(orient="records")})
            elif filename.endswith(".json"):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_data.append({"filename": filename, "type": "json", "content": data})
        except Exception as e:
            print(f"Erro ao ler arquivo de dados do chat {filename}: {e}")
            continue
    return {"data": all_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
