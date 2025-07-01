# cache.py
# Funções para manipulação de cache

import logging
import os
import json
from typing import Any, Optional, List, Dict, Union

def salvar_cache_json(dados: Union[List[Any], Dict[str, Any]], caminho: str) -> None:
    """
    Salva uma estrutura de dados (lista ou dicionário) em um arquivo JSON.

    Args:
        dados (Union[List[Any], Dict[str, Any]]): Os dados a serem salvos.
        caminho (str): O caminho do arquivo JSON de destino.
    """
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        logging.info(f"Cache salvo com sucesso em: {caminho}")
    except TypeError as e:
        logging.error(f"Erro de serialização ao salvar cache JSON: {e}")
    except IOError as e:
        logging.error(f"Erro de I/O ao salvar cache JSON em {caminho}: {e}")

def carregar_cache_json(caminho: str) -> Optional[Union[List[Any], Dict[str, Any]]]:
    """
    Carrega dados de um arquivo JSON de cache, se ele existir e for válido.

    Args:
        caminho (str): O caminho do arquivo JSON a ser carregado.

    Returns:
        Optional[Union[List[Any], Dict[str, Any]]]: Os dados carregados ou None se o arquivo não existir ou ocorrer um erro.
    """
    if not os.path.exists(caminho):
        return None
    
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except json.JSONDecodeError as e:
        logging.warning(f"Erro ao decodificar JSON do cache {caminho}: {e}. O cache será ignorado.")
        return None
    except IOError as e:
        logging.error(f"Erro de I/O ao carregar cache JSON de {caminho}: {e}")
        return None
