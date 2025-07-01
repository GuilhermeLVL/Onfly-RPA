# extractor.py
# Funções para consumir a PokeAPI com retentativas e paralelismo.

import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from src.utils.cache import salvar_cache_json, carregar_cache_json
from src.config.settings import (
    URL_API,
    CAMINHO_CACHE,
    QUANTIDADE_POKEMON,
    USAR_CACHE,
    USAR_DADOS_EXEMPLO,
    TIMEOUT_REQUEST,
    RETENTATIVAS_CONEXAO,
    FATOR_BACKOFF
)

def _criar_sessao_com_retentativas() -> requests.Session:
    """
    Cria uma sessão de requests com uma estratégia de retentativas.
    Isso ajuda a lidar com instabilidades temporárias da rede ou da API.

    Returns:
        requests.Session: Uma sessão configurada com retentativas.
    """
    sessao = requests.Session()
    retries = Retry(
        total=RETENTATIVAS_CONEXAO,
        backoff_factor=FATOR_BACKOFF,
        status_forcelist=[500, 502, 503, 504],  # Erros de servidor
        allowed_methods=frozenset(['GET'])
    )
    adaptador = HTTPAdapter(max_retries=retries)
    sessao.mount("https://", adaptador)
    sessao.mount("http://", adaptador)
    return sessao

def testar_conexao_api() -> bool:
    """
    Testa a conexão com a PokeAPI usando a sessão com retentativas.

    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário.
    """
    try:
        sessao = _criar_sessao_com_retentativas()
        resposta = sessao.get(f"{URL_API}1", timeout=TIMEOUT_REQUEST)
        resposta.raise_for_status()
        logging.info("Conexão com PokeAPI testada com sucesso.")
        return True
    except requests.exceptions.RequestException as erro:
        logging.error(f"Erro ao conectar com PokeAPI após {RETENTATIVAS_CONEXAO} tentativas: {erro}")
        return False

def gerar_dados_exemplo(quantidade: int = QUANTIDADE_POKEMON) -> List[Dict[str, Any]]:
    """
    Gera dados de exemplo para desenvolvimento ou quando a API está indisponível.

    Args:
        quantidade (int): O número de Pokémon de exemplo a serem gerados.

    Returns:
        List[Dict[str, Any]]: Uma lista de dicionários, cada um representando um Pokémon.
    """
    pokemon_exemplo = [
        {
            'id': 1, 'name': 'bulbasaur', 'types': [{'type': {'name': 'grass'}}, {'type': {'name': 'poison'}}],
            'stats': [
                {'stat': {'name': 'hp'}, 'base_stat': 45},
                {'stat': {'name': 'attack'}, 'base_stat': 49},
                {'stat': {'name': 'defense'}, 'base_stat': 49}
            ]
        }
    ]
    resultado = [pokemon_exemplo[0].copy() for _ in range(quantidade)]
    for i, pokemon in enumerate(resultado):
        pokemon['id'] = i + 1
        pokemon['name'] = f"pokemon_{i+1}"
    logging.info(f"Dados de exemplo gerados: {len(resultado)} Pokémon")
    return resultado

def _buscar_pokemon_individual(pokemon_id: int, sessao: requests.Session) -> Optional[Dict[str, Any]]:
    """
    Busca os dados de um único Pokémon pela sua ID.

    Args:
        pokemon_id (int): A ID do Pokémon a ser buscado.
        sessao (requests.Session): A sessão de requests a ser usada.

    Returns:
        Optional[Dict[str, Any]]: Um dicionário com os dados do Pokémon ou None se falhar.
    """
    try:
        url = f"{URL_API}{pokemon_id}"
        resposta = sessao.get(url, timeout=TIMEOUT_REQUEST)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        logging.error(f"Erro ao baixar Pokémon {pokemon_id}: {erro}")
        return None

def buscar_dados_pokemon(
    quantidade: int = QUANTIDADE_POKEMON,
    usar_cache: bool = USAR_CACHE,
    usar_dados_exemplo: bool = USAR_DADOS_EXEMPLO
) -> List[Dict[str, Any]]:
    """
    Busca dados dos Pokémon da PokeAPI em paralelo, com suporte a cache e dados de exemplo.

    Args:
        quantidade (int): O número de Pokémon a serem buscados.
        usar_cache (bool): Se deve usar o cache para carregar/salvar os dados.
        usar_dados_exemplo (bool): Se deve usar dados de exemplo em caso de falha na API.

    Returns:
        List[Dict[str, Any]]: Uma lista de dicionários com os dados brutos dos Pokémon.
    """
    if usar_cache:
        dados_cache = carregar_cache_json(CAMINHO_CACHE)
        if dados_cache:
            logging.info(f"Dados de {len(dados_cache)} Pokémon carregados do cache.")
            return dados_cache

    if not testar_conexao_api():
        if usar_dados_exemplo:
            logging.warning("API indisponível. Usando dados de exemplo.")
            return gerar_dados_exemplo(quantidade)
        else:
            logging.error("Falha na conexão com a API. Nenhum dado foi obtido.")
            return []

    resultado: List[Dict[str, Any]] = []
    sessao = _criar_sessao_com_retentativas()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futuros = {executor.submit(_buscar_pokemon_individual, i, sessao): i for i in range(1, quantidade + 1)}
        
        for futuro in as_completed(futuros):
            dados = futuro.result()
            if dados:
                resultado.append(dados)

    resultado.sort(key=lambda p: p['id'])  # Ordenar para consistência

    if resultado:
        if usar_cache:
            salvar_cache_json(resultado, CAMINHO_CACHE)
        logging.info(f"{len(resultado)} Pokémon baixados e processados com sucesso.")
    else:
        logging.error("Nenhum Pokémon foi baixado com sucesso.")
        if usar_dados_exemplo:
            logging.warning("Usando dados de exemplo como fallback.")
            return gerar_dados_exemplo(quantidade)
    
    return resultado
