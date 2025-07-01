import os
import json
import pandas as pd
from datetime import datetime

CHAT_OUTPUTS_DIR = "chat_outputs"
DADOS_DIR = os.path.join(CHAT_OUTPUTS_DIR, "dados")
HISTORICO_PATH = os.path.join(CHAT_OUTPUTS_DIR, "historico.txt")

def salvar_historico(pergunta: str, resposta: str):
    os.makedirs(CHAT_OUTPUTS_DIR, exist_ok=True)
    with open(HISTORICO_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}]\nPergunta: {pergunta}\nResposta: {resposta}\n{'--'*20}\n")

def carregar_contexto_anterior() -> str:
    contexto_partes = []
    if os.path.exists(HISTORICO_PATH):
        try:
            with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
                historico = f.read()
                if historico.strip():
                    contexto_partes.append(f"=== HISTÓRICO DE CONVERSAS ===\n{historico}")
        except Exception as e:
            print(f"Erro ao ler histórico: {e}")
    
    if os.path.exists(DADOS_DIR):
        try:
            dados_estruturados = []
            for arquivo in os.listdir(DADOS_DIR):
                caminho_arquivo = os.path.join(DADOS_DIR, arquivo)
                if arquivo.endswith('.csv'):
                    df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
                    dados_estruturados.append(f"CSV ({arquivo}):\n{df.to_string()}")
                elif arquivo.endswith('.json'):
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados_json = json.load(f)
                        dados_estruturados.append(f"JSON ({arquivo}):\n{json.dumps(dados_json, indent=2, ensure_ascii=False)}")
            
            if dados_estruturados:
                contexto_partes.append(f"=== DADOS ESTRUTURADOS ANTERIORES ===\n" + "\n\n".join(dados_estruturados))
        except Exception as e:
            print(f"Erro ao ler dados estruturados: {e}")
    
    return "\n\n".join(contexto_partes) if contexto_partes else ""

def limpar_contexto(confirmar: bool = True):
    if confirmar:
        resposta = input("Tem certeza que deseja limpar todo o contexto? (sim/não): ")
        if resposta.lower() not in ['sim', 's', 'yes', 'y']:
            print("Operação cancelada.")
            return
    
    try:
        if os.path.exists(HISTORICO_PATH):
            os.remove(HISTORICO_PATH)
            print(f"[INFO] Histórico removido: {HISTORICO_PATH}")
        
        if os.path.exists(DADOS_DIR):
            for arquivo in os.listdir(DADOS_DIR):
                os.remove(os.path.join(DADOS_DIR, arquivo))
            print(f"[INFO] Arquivos de dados removidos de {DADOS_DIR}")
            os.rmdir(DADOS_DIR)

        graficos_dir = os.path.join(CHAT_OUTPUTS_DIR, "graficos")
        if os.path.exists(graficos_dir):
            for arquivo in os.listdir(graficos_dir):
                os.remove(os.path.join(graficos_dir, arquivo))
            print(f"[INFO] Gráficos removidos de {graficos_dir}")
            os.rmdir(graficos_dir)

        if os.path.exists(CHAT_OUTPUTS_DIR) and not os.listdir(CHAT_OUTPUTS_DIR):
             os.rmdir(CHAT_OUTPUTS_DIR)

        print("[SUCESSO] Contexto limpo com sucesso!")
        
    except Exception as e:
        print(f"[ERRO] Erro ao limpar contexto: {e}")
