# transformer.py
# Funções para limpeza, categorização e análise dos dados extraídos 

import pandas as pd
import logging
from typing import List, Dict, Any

def transformar_dados_pokemon(dados_brutos: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transforma a lista de dados brutos da PokeAPI em um DataFrame estruturado e limpo.

    Args:
        dados_brutos (List[Dict[str, Any]]): A lista de dicionários com dados de Pokémon.

    Returns:
        pd.DataFrame: Uma tabela com colunas: ID, Nome, Tipos, Experiencia_Base, HP, Ataque, Defesa, Categoria.
    """
    dados_transformados = []
    
    for pokemon in dados_brutos:
        stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon.get('stats', [])}
        experiencia_base = pokemon.get('base_experience', 0)

        dados_transformados.append({
            'ID': pokemon.get('id'),
            'Nome': pokemon.get('name', 'N/A').capitalize(),
            'Tipos': ", ".join([t['type']['name'] for t in pokemon.get('types', [])]),
            'Experiencia_Base': experiencia_base,
            'HP': stats.get('hp', 0),
            'Ataque': stats.get('attack', 0),
            'Defesa': stats.get('defense', 0),
            'Categoria': "Forte" if experiencia_base > 100 else "Médio" if experiencia_base >= 50 else "Fraco"
        })
    
    tabela = pd.DataFrame(dados_transformados)
    logging.info(f"Transformação concluída. Tabela criada com {len(tabela)} Pokémon.")
    return tabela

def contar_pokemon_por_tipo(tabela: pd.DataFrame) -> Dict[str, int]:
    """
    Conta a ocorrência de cada tipo de Pokémon na tabela de dados.

    Args:
        tabela (pd.DataFrame): O DataFrame de Pokémon com a coluna 'Tipos'.

    Returns:
        Dict[str, int]: Um dicionário com a contagem de cada tipo.
    """
    contagem = tabela['Tipos'].str.split(', ', expand=True).stack().value_counts().to_dict()
    logging.info(f"Contagem de tipos concluída. {len(contagem)} tipos únicos encontrados.")
    return contagem

def calcular_media_stats_por_tipo(tabela: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a média de HP, Ataque e Defesa para cada tipo de Pokémon.

    Args:
        tabela (pd.DataFrame): O DataFrame de Pokémon.

    Returns:
        pd.DataFrame: Uma tabela com a média de stats para cada tipo.
    """
    tabela_tipos = tabela.assign(Tipos=tabela['Tipos'].str.split(', ')).explode('Tipos')
    media_por_tipo = tabela_tipos.groupby('Tipos')[['HP', 'Ataque', 'Defesa']].mean().round(1)
    logging.info(f"Média de stats por tipo calculada.")
    return media_por_tipo

def encontrar_top_5_experiencia(tabela: pd.DataFrame) -> pd.DataFrame:
    """
    Encontra os 5 Pokémon com a maior experiência base.

    Args:
        tabela (pd.DataFrame): O DataFrame de Pokémon.

    Returns:
        pd.DataFrame: Uma tabela com os 5 Pokémon de maior experiência.
    """
    top_5 = tabela.nlargest(5, 'Experiencia_Base')
    logging.info(f"Top 5 Pokémon por experiência definidos.")
    return top_5