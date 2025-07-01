# reporter.py
# Funções para geração de gráficos e exportação de relatórios 

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

from src.config.settings import CAMINHO_GRAFICO_TIPOS, CAMINHO_RELATORIO_CSV

def gerar_grafico_tipos(contagem_tipos: Dict[str, int], caminho_saida: str = CAMINHO_GRAFICO_TIPOS):
    """
    Cria e salva um gráfico de barras com a contagem de Pokémon por tipo.

    Args:
        contagem_tipos (Dict[str, int]): Dicionário com tipos como chaves e contagens como valores.
        caminho_saida (str): Caminho para salvar o arquivo de imagem do gráfico.
    """
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    tipos = list(contagem_tipos.keys())
    quantidades = list(contagem_tipos.values())
    
    barras = plt.bar(tipos, quantidades, color='skyblue', edgecolor='navy', alpha=0.7)
    
    plt.title('Quantidade de Pokémon por Tipo', fontsize=16, fontweight='bold')
    plt.xlabel('Tipos de Pokémon', fontsize=12)
    plt.ylabel('Quantidade', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    for barra in barras:
        yval = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2.0, yval + 0.5, int(yval), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=300)
    plt.close()
    logging.info(f"Gráfico de tipos salvo em: {caminho_saida}")

def exportar_relatorio_csv(tabela: pd.DataFrame, caminho_saida: str = CAMINHO_RELATORIO_CSV):
    """
    Exporta um DataFrame para um arquivo CSV.

    Args:
        tabela (pd.DataFrame): DataFrame a ser salvo.
        caminho_saida (str): Caminho para salvar o arquivo CSV.
    """
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    tabela.to_csv(caminho_saida, index=False, encoding='utf-8', sep=';')
    logging.info(f"Relatório CSV salvo em: {caminho_saida}")

def gerar_relatorio_consolidado(top_5: pd.DataFrame, media_por_tipo: pd.DataFrame, caminho_saida: str = "data/relatorio_consolidado.txt"):
    """
    Gera um relatório de texto consolidado com as principais análises.

    Args:
        top_5 (pd.DataFrame): DataFrame com os 5 Pokémon de maior experiência.
        media_por_tipo (pd.DataFrame): DataFrame com a média de stats por tipo.
        caminho_saida (str): Caminho para salvar o arquivo de texto do relatório.
    """
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("========================================\n")
        f.write("    RELATÓRIO DE ANÁLISE POKÉMON      \n")
        f.write("========================================\n\n")
        f.write("--- Top 5 Pokémon com Maior Experiência Base ---\n")
        f.write(top_5.to_string(index=False))
        f.write("\n\n")
        f.write("--- Média de Atributos por Tipo ---\n")
        f.write(media_por_tipo.to_string())
        f.write("\n\n")
        f.write(f"Gráfico de distribuição por tipo salvo em: {CAMINHO_GRAFICO_TIPOS}\n")
        f.write(f"Dados completos salvos em: {CAMINHO_RELATORIO_CSV}\n")
    logging.info(f"Relatório consolidado salvo em: {caminho_saida}")

def gerar_resumo_relatorio(tabela: pd.DataFrame, analise_tipos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria e loga um resumo com as principais estatísticas do relatório.

    Args:
        tabela (pd.DataFrame): DataFrame principal com dados dos Pokémon.
        analise_tipos (Dict[str, Any]): Dicionário contendo a contagem de tipos.

    Returns:
        Dict[str, Any]: Dicionário com o resumo das estatísticas.
    """
    resumo = {
        'total_pokemon': len(tabela),
        'tipos_unicos': len(analise_tipos['contagem_tipos']),
        'fortes': (tabela['Categoria'] == 'Forte').sum(),
        'medios': (tabela['Categoria'] == 'Médio').sum(),
        'fracos': (tabela['Categoria'] == 'Fraco').sum(),
        'hp_medio': tabela['HP'].mean(),
        'ataque_medio': tabela['Ataque'].mean(),
        'defesa_media': tabela['Defesa'].mean()
    }
    
    logging.info("=== RESUMO DO RELATÓRIO ===")
    for chave, valor in resumo.items():
        if isinstance(valor, float):
            logging.info(f"{chave.replace('_', ' ').capitalize()}: {valor:.1f}")
        else:
            logging.info(f"{chave.replace('_', ' ').capitalize()}: {valor}")
    
    return resumo

# --- Funções para Gráficos Automáticos ---

def _plot_from_dataframe(ax, dados: pd.DataFrame, tipo: Optional[str]):
    if dados.shape[1] < 2:
        ax.text(0.5, 0.5, "Dados insuficientes para gráfico", ha='center')
        return
    x, y = dados.columns[0], dados.columns[1]
    dados[y] = pd.to_numeric(dados[y], errors='coerce').fillna(0)

    if tipo == "pizza":
        dados.set_index(x)[y].plot.pie(autopct='%1.1f%%', ax=ax)
    elif tipo == "linha":
        dados.plot(x=x, y=y, ax=ax, marker='o')
    else:  # Barra como padrão
        dados.plot.bar(x=x, y=y, ax=ax)
        ax.tick_params(axis='x', rotation=45)

def _plot_from_dict(ax, dados: Dict[str, Any], tipo: Optional[str]):
    chaves, valores = list(dados.keys()), list(dados.values())
    valores_num = [pd.to_numeric(v, errors='coerce') for v in valores]

    if tipo == "pizza":
        ax.pie(valores_num, labels=chaves, autopct='%1.1f%%')
    elif tipo == "linha":
        ax.plot(chaves, valores_num, marker='o')
    else: # Barra como padrão
        ax.bar(chaves, valores_num, color='skyblue')
        ax.tick_params(axis='x', rotation=45)

def _processar_especificacao_plot(ax, dados: pd.DataFrame, especificacao: str) -> bool:
    """
    Processa a especificação de plotagem e tenta gerar o gráfico.
    Retorna True se o gráfico foi gerado, False caso contrário (ex: especificação ambígua).
    """
    especificacao_lower = especificacao.lower()

    if "diferenca do hp" in especificacao_lower:
        if 'HP' in dados.columns and 'HP_anterior' in dados.columns: # Assumindo 'HP_anterior' existe para cálculo de diferença
            dados['Diferenca_HP'] = dados['HP'] - dados['HP_anterior']
            dados.plot(x=dados.index, y='Diferenca_HP', kind='bar', ax=ax, title='Diferença de HP')
            ax.set_ylabel('Diferença de HP')
            return True
        else:
            ax.text(0.5, 0.5, "Colunas 'HP' ou 'HP_anterior' não encontradas para calcular diferença de HP.", ha='center')
            return False
    elif "apenas hp" in especificacao_lower or "hp" == especificacao_lower.strip():
        if 'HP' in dados.columns:
            dados['HP'].plot(kind='hist', ax=ax, title='Distribuição de HP')
            ax.set_xlabel('HP')
            ax.set_ylabel('Frequência')
            return True
        else:
            ax.text(0.5, 0.5, "Coluna 'HP' não encontrada.", ha='center')
            return False
    elif "apenas ataque" in especificacao_lower or "ataque" == especificacao_lower.strip():
        if 'Ataque' in dados.columns:
            dados['Ataque'].plot(kind='hist', ax=ax, title='Distribuição de Ataque')
            ax.set_xlabel('Ataque')
            ax.set_ylabel('Frequência')
            return True
        else:
            ax.text(0.5, 0.5, "Coluna 'Ataque' não encontrada.", ha='center')
            return False
    elif "apenas defesa" in especificacao_lower or "defesa" == especificacao_lower.strip():
        if 'Defesa' in dados.columns:
            dados['Defesa'].plot(kind='hist', ax=ax, title='Distribuição de Defesa')
            ax.set_xlabel('Defesa')
            ax.set_ylabel('Frequência')
            return True
        else:
            ax.text(0.5, 0.5, "Coluna 'Defesa' não encontrada.", ha='center')
            return False
    elif "todos os stats" in especificacao_lower or "todos os atributos" in especificacao_lower:
        stats_columns = ['HP', 'Ataque', 'Defesa', 'Ataque_Especial', 'Defesa_Especial', 'Velocidade']
        found_stats = [col for col in stats_columns if col in dados.columns]
        if found_stats:
            dados[found_stats].plot(kind='box', ax=ax, title='Distribuição de Todos os Atributos')
            ax.set_ylabel('Valor do Atributo')
            return True
        else:
            ax.text(0.5, 0.5, "Nenhuma coluna de atributo comum encontrada (HP, Ataque, Defesa, etc.).", ha='center')
            return False
    
    # Se a especificação não for clara, retornar False
    ax.text(0.5, 0.5, "Especificação de plotagem ambígua ou não suportada. Por favor, detalhe melhor (ex: 'apenas hp', 'diferenca do hp').", ha='center')
    return False


def gerar_grafico_automatico(
    dados: Union[pd.DataFrame, Dict, List],
    caminho_saida: Optional[str] = None,
    tipo: Optional[str] = None,  # 'barras', 'pizza', 'linha'
    titulo: str = "Gráfico Gerado Automaticamente",
    especificacao_plot: Optional[str] = None # Novo parâmetro
) -> Optional[str]:
    """
    Gera um gráfico automaticamente a partir de diferentes tipos de dados.

    Args:
        dados: Um DataFrame, dicionário ou lista para plotar.
        caminho_saida: Onde salvar o gráfico. Se None, um caminho é gerado.
        tipo: O tipo de gráfico a ser gerado ('barras', 'pizza', 'linha').
        titulo: Título do gráfico.
        especificacao_plot: String descrevendo o que deve ser plotado (ex: "diferenca do hp", "apenas hp").

    Returns:
        O caminho onde o gráfico foi salvo, ou None se falhar.
    """
    if not caminho_saida:
        GRAFICOS_DIR = "chat_outputs/graficos"
        os.makedirs(GRAFICOS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_saida = os.path.join(GRAFICOS_DIR, f"grafico_{timestamp}.png")

    fig, ax = plt.subplots(figsize=(12, 8))
    
    try:
        if isinstance(dados, pd.DataFrame):
            if especificacao_plot:
                plot_gerado = _processar_especificacao_plot(ax, dados, especificacao_plot)
                if not plot_gerado:
                    # Se a especificação não gerou um plot, tentar o comportamento padrão
                    _plot_from_dataframe(ax, dados, tipo)
            else:
                _plot_from_dataframe(ax, dados, tipo)
        elif isinstance(dados, dict):
            _plot_from_dict(ax, dados, tipo)
        else:
            ax.text(0.5, 0.5, "Formato de dados não suportado para gráfico.", ha='center')

        ax.set_title(titulo, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(caminho_saida, dpi=300)
        plt.close(fig)
        logging.info(f"Gráfico automático salvo em: {caminho_saida}")
        return caminho_saida
    except Exception as e:
        logging.error(f"Falha ao gerar gráfico automático: {e}")
        plt.close(fig)
        return None
