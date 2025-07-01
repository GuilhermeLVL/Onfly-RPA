"""
Arquivo de configuração para centralizar constantes e parâmetros.
"""

# Configurações da API
URL_API = "https://pokeapi.co/api/v2/pokemon/"
QUANTIDADE_POKEMON = 100  # Número de Pokémon a serem buscados
TIMEOUT_REQUEST = 30  # Tempo máximo de espera para uma requisição

# Configurações de Cache
USAR_CACHE = True
CAMINHO_CACHE = "data/pokemon_cache.json"

# Configurações de Dados de Exemplo
USAR_DADOS_EXEMPLO = True

# Configurações de Caminhos de Saída
CAMINHO_LOG = "logs/pipeline.log"
CAMINHO_GRAFICO_TIPOS = "data/grafico_tipos.png"
CAMINHO_RELATORIO_CSV = "data/relatorio.csv"

# Configurações de Retentativas (Retry)
RETENTATIVAS_CONEXAO = 3  # Número máximo de retentativas
FATOR_BACKOFF = 0.5  # Espera entre retentativas (ex: 0.5s, 1s, 2s)


