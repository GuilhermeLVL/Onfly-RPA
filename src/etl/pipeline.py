# pipeline.py
# Execução geral do pipeline de ETL 

from src.utils.logger import configurar_logs
from src.etl.extractor import buscar_dados_pokemon
from src.etl.transformer import (
    transformar_dados_pokemon, 
    contar_pokemon_por_tipo,
    calcular_media_stats_por_tipo,
    encontrar_top_5_experiencia
)
from src.etl.reporter import (
    gerar_grafico_tipos, 
    exportar_relatorio_csv, 
    gerar_resumo_relatorio,
    gerar_relatorio_consolidado
)
import logging
from src.rag.rag_data_loader import gerar_documentos_para_rag, indexar_dados

def executar_pipeline():
    """
    Executa todo o processo de ETL:
    1. Busca dados da PokeAPI
    2. Transforma e analisa os dados
    3. Gera relatórios e gráficos
    """
    # Configurar logs
    configurar_logs()
    logging.info("Iniciando pipeline de ETL.")
    
    try:
        # 1. Extração
        dados_brutos = buscar_dados_pokemon()
        logging.info(f"Busca concluída. {len(dados_brutos)} Pokémon obtidos.")
        
        if not dados_brutos:
            logging.warning("Nenhum dado foi obtido. Encerrando o pipeline.")
            return

        # 2. Transformação
        tabela = transformar_dados_pokemon(dados_brutos)
        logging.info("Transformação de dados concluída.")

        # 3. Análise
        contagem_tipos = contar_pokemon_por_tipo(tabela)
        media_stats_tipo = calcular_media_stats_por_tipo(tabela)
        top_5_exp = encontrar_top_5_experiencia(tabela)
        logging.info("Análises estatísticas concluídas.")
        
        # 4. Geração de Relatórios
        exportar_relatorio_csv(tabela)
        gerar_grafico_tipos(contagem_tipos)
        gerar_relatorio_consolidado(top_5_exp, media_stats_tipo)
        
        # Gerar resumo para o log
        analise_completa = {
            'contagem_tipos': contagem_tipos
        }
        gerar_resumo_relatorio(tabela, analise_completa)
        
        # 5. Indexação para RAG
        documentos = gerar_documentos_para_rag()
        if documentos:
            indexar_dados(documentos)
            logging.info("Indexação de dados para o RAG concluída.")
        else:
            logging.warning("Não foi possível gerar documentos para o RAG.")

        logging.info("Pipeline concluído com sucesso!")
        
    except Exception as erro:
        logging.error(f"Erro fatal no pipeline: {erro}", exc_info=True)
        raise
