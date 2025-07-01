# logger.py
# Funções para configuração de logging 

import logging
import os
from typing import Any, Optional, List, Dict, Union

from src.config.settings import CAMINHO_LOG

def configurar_logs(caminho_log: str = CAMINHO_LOG) -> None:
    """
    Configura o sistema de logs para salvar em arquivo e mostrar no console.

    Args:
        caminho_log (str): O caminho para o arquivo de log.
    """
    os.makedirs(os.path.dirname(caminho_log), exist_ok=True)
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(caminho_log, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
