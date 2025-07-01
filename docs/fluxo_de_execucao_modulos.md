# Fluxo de Execução Detalhado dos Módulos

Este documento descreve o caminho completo da execução do projeto, explicando a ordem de execução dos módulos, como as funções se encadeiam e quais dados são passados entre elas, dependendo do ponto de entrada.

---

## 2.1. Ponto de Entrada: `main.py`

O `main.py` atua como a interface de linha de comando (CLI) para o projeto, orquestrando as principais ações: executar o pipeline de ETL, iniciar o chat interativo ou servir a API.

### 2.1.1. Fluxo: Execução do Pipeline ETL (`python main.py pipeline`)

Este fluxo é responsável pela extração, transformação, análise e carregamento de dados de Pokémon, além de preparar o índice para o sistema RAG.

1.  **`main.py` (função `main`)**
    *   **Ação**: Carrega variáveis de ambiente do arquivo `.env` via `dotenv.load_dotenv()`.
    *   **Chamada**: Invoca `src.etl.pipeline.executar_pipeline()`.
    *   **Dados Passados**: Nenhum (a função `executar_pipeline` orquestra as dependências internamente).

2.  **`src/etl/pipeline.py` (função `executar_pipeline`)**
    *   **Ação**: Orquestra todas as fases do ETL e a indexação para o RAG.
    *   **Chamadas**:
        *   `src.utils.logger.configurar_logs()`: Inicializa o sistema de logs.
        *   `src.etl.extractor.buscar_dados_pokemon()`:
            *   **Dados Passados**: `quantidade` (do `settings.py`), `usar_cache`, `usar_dados_exemplo`.
            *   **Recebe**: Uma `List[Dict[str, Any]]` com os dados brutos dos Pokémon.
        *   `src.etl.transformer.transformar_dados_pokemon(dados_brutos)`:
            *   **Dados Passados**: Os `dados_brutos` recebidos do extrator.
            *   **Recebe**: Um `pd.DataFrame` estruturado (`tabela`).
        *   `src.etl.transformer.contar_pokemon_por_tipo(tabela)`:
            *   **Dados Passados**: O `tabela` DataFrame.
            *   **Recebe**: Um `Dict[str, int]` com a contagem de tipos.
        *   `src.etl.transformer.calcular_media_stats_por_tipo(tabela)`:
            *   **Dados Passados**: O `tabela` DataFrame.
            *   **Recebe**: Um `pd.DataFrame` com as médias de stats por tipo.
        *   `src.etl.transformer.encontrar_top_5_experiencia(tabela)`:
            *   **Dados Passados**: O `tabela` DataFrame.
            *   **Recebe**: Um `pd.DataFrame` com os top 5 Pokémon por experiência.
        *   `src.etl.reporter.exportar_relatorio_csv(tabela)`:
            *   **Dados Passados**: O `tabela` DataFrame.
        *   `src.etl.reporter.gerar_grafico_tipos(contagem_tipos)`:
            *   **Dados Passados**: O dicionário `contagem_tipos`.
        *   `src.etl.reporter.gerar_relatorio_consolidado(top_5_exp, media_stats_tipo)`:
            *   **Dados Passados**: Os DataFrames `top_5_exp` e `media_stats_tipo`.
        *   `src.etl.reporter.gerar_resumo_relatorio(tabela, analise_completa)`:
            *   **Dados Passados**: O `tabela` DataFrame e um dicionário de `analise_completa` (contagem de tipos).
        *   `src.rag.rag_data_loader.gerar_documentos_para_rag()`:
            *   **Dados Passados**: Nenhum (lê diretamente de `data/relatorio.csv`).
            *   **Recebe**: Uma `list[Document]` com documentos para o RAG.
        *   `src.rag.rag_data_loader.indexar_dados(documentos)`:
            *   **Dados Passados**: A `list[Document]` de documentos.
    *   **Saídas**: Arquivos de log (`logs/pipeline.log`), CSV (`data/relatorio.csv`), imagem do gráfico (`data/grafico_tipos.png`), relatório consolidado (`data/relatorio_consolidado.txt`), e o índice FAISS (`data/indice_faiss/`).

### 2.1.2. Fluxo: Chat Interativo (`python main.py chat`)

Este fluxo permite ao usuário interagir com o chatbot RAG diretamente no terminal.

1.  **`main.py` (função `main`)**
    *   **Ação**: Carrega variáveis de ambiente.
    *   **Chamada**: Invoca `main.py:chat_interativo()`.
    *   **Dados Passados**: Nenhum.

2.  **`main.py` (função `chat_interativo`)**
    *   **Ação**: Gerencia o loop de interação com o usuário, comandos especiais e a chamada principal ao RAG.
    *   **Chamadas**:
        *   `src.rag_builder.inicializar_rag()`:
            *   **Ação**: Tenta carregar o vector store FAISS existente. Se não existe, gera documentos do CSV e o indexa.
            *   **Recebe**: O `vetorstore` (instância FAISS).
        *   Loop de input do usuário (`input("Você: ")`).
        *   Comandos Especiais:
            *   `if comando == "/limpar"`: Chama `src.rag.chat_history.limpar_contexto()`.
            *   `if comando.startswith("/plot")`: Chama `main.py:handle_plot_command(pergunta)`.
                *   `main.py:handle_plot_command(command)`:
                    *   **Ação**: Parseia o comando `/plot`, lê o arquivo (CSV/JSON).
                    *   **Chamada**: `src.etl.reporter.gerar_grafico_automatico(dados, especificacao_plot=o_que_plotar)`.
                        *   **Dados Passados**: Dados do arquivo e a especificação de plotagem.
        *   `else` (pergunta normal para o RAG): Chama `src.rag.rag_core.responder_pergunta_rag(pergunta, vetorstore)`.
            *   **Dados Passados**: A `pergunta` do usuário e o `vetorstore` carregado.
            *   **Recebe**: A `resposta_texto` do LLM.

### 2.1.3. Fluxo: Servir API FastAPI (`python main.py serve_api` ou `python api.py`)

Este fluxo inicia o servidor web FastAPI que expõe as funcionalidades do projeto via HTTP.

1.  **`main.py` (função `main`)**
    *   **Ação**: Carrega variáveis de ambiente.
    *   **Chamada**: Invoca `uvicorn.run(fastapi_app, host="0.0.0.0", port=8001)` para iniciar o servidor Uvicorn com a aplicação FastAPI definida em `api.py`.
    *   **Dados Passados**: A instância do aplicativo FastAPI.

2.  **`api.py`**
    *   **Ação**: Define os endpoints da API e gerencia as requisições HTTP.
    *   **Eventos de Startup (`@app.on_event("startup")`)**:
        *   **Chamada**: `src.rag_builder.inicializar_rag()`:
            *   **Ação**: Carrega ou cria o `vetorstore` FAISS e o armazena na variável global `vetorstore_rag`.
            *   **Recebe**: O `vetorstore` (instância FAISS).
    *   **Endpoints e suas chamadas internas**:
        *   **`GET /status`**: Retorna um status simples.
        *   **`POST /run_pipeline`**: Chama `src.etl.pipeline.executar_pipeline()`.
        *   **`POST /chat`**:
            *   **Chamada**: `src.rag.rag_core.responder_pergunta_rag(user_pergunta, vetorstore_rag)`.
            *   **Dados Passados**: A pergunta do usuário e o `vetorstore_rag`.
            *   **Recebe**: A resposta do LLM.
        *   **`POST /clear_context`**: Chama `src.rag.chat_history.limpar_contexto(confirmar=False)`.
        *   **`GET /get_pipeline_report`**: Lê `data/relatorio.csv` usando `pandas`.
        *   **`GET /get_pipeline_chart`**: Retorna o arquivo `data/grafico_tipos.png` como `FileResponse`.
        *   **`GET /get_chat_history`**: Lê `chat_outputs/historico.txt`.
        *   **`GET /get_chat_data`**: Lista e lê arquivos de `chat_outputs/dados/` (CSV e JSON).

---

## 2.2. Fluxo Detalhado das Funções Principais (Interconexões)

Esta seção aprofunda como as funções se encadeiam entre os módulos para realizar as tarefas principais.

### 2.2.1. Fluxo de Extração (`src/etl/extractor.py`)

*   **`buscar_dados_pokemon()`** é a função orquestradora aqui.
    1.  Tenta `src.utils.cache.carregar_cache_json(CAMINHO_CACHE)`.
    2.  Se o cache não existir ou estiver vazio, chama `_criar_sessao_com_retentativas()` para configurar a sessão HTTP.
    3.  Chama `testar_conexao_api()` para verificar a disponibilidade da PokeAPI.
    4.  Se a API estiver inacessível e `USAR_DADOS_EXEMPLO` for `True`, chama `gerar_dados_exemplo()`.
    5.  Caso contrário, usa `ThreadPoolExecutor` para chamar `_buscar_pokemon_individual()` em paralelo para cada ID de Pokémon.
    6.  Após coletar todos os dados, se `USAR_CACHE` for `True`, chama `src.utils.cache.salvar_cache_json(resultado, CAMINHO_CACHE)`.
    7.  Retorna os dados brutos.

### 2.2.2. Fluxo de Transformação (`src/etl/transformer.py`)

*   **`transformar_dados_pokemon(dados_brutos)`** é a função principal que recebe os dados brutos.
    1.  Itera sobre `dados_brutos`, extraindo e reestruturando campos.
    2.  Calcula a 'Categoria' com base na 'Experiencia_Base'.
    3.  Retorna um `pd.DataFrame`.
*   As funções de análise (`contar_pokemon_por_tipo`, `calcular_media_stats_por_tipo`, `encontrar_top_5_experiencia`) operam diretamente no `pd.DataFrame` gerado por `transformar_dados_pokemon`.

### 2.2.3. Fluxo de Relatórios (`src/etl/reporter.py`)

*   As funções de relatório (`gerar_grafico_tipos`, `exportar_relatorio_csv`, `gerar_relatorio_consolidado`, `gerar_resumo_relatorio`) recebem os DataFrames e dicionários resultantes das fases de transformação e análise (`tabela`, `contagem_tipos`, `top_5_exp`, `media_stats_tipo`) e produzem os artefatos de saída (arquivos PNG, CSV, TXT).
*   **`gerar_grafico_automatico(dados, especificacao_plot=...)`** (chamado via `/plot` no `main.py` ou futuramente via API):
    1.  Recebe dados (DataFrame, dict ou list) e uma especificação.
    2.  Chama `_processar_especificacao_plot()` se uma `especificacao_plot` for fornecida para tentar criar um gráfico contextualizado.
    3.  Se a especificação não for clara ou não gerar um plot, tenta `_plot_from_dataframe()` ou `_plot_from_dict()` com base no `tipo` de gráfico.
    4.  Salva o gráfico em um caminho gerado ou especificado.

### 2.2.4. Fluxo de Geração/Indexação RAG (`src/rag/rag_data_loader.py` e `src/rag_builder.py`)

*   **`src.rag_builder.inicializar_rag()`** é o ponto de entrada para preparar o RAG.
    1.  Tenta `src.rag.rag_data_loader.carregar_vetorstore()`.
    2.  Se falhar, chama `src.rag.rag_data_loader.gerar_documentos_para_rag()`:
        *   **Ação**: Lê `data/relatorio.csv`.
        *   **Recebe**: Uma `list[Document]`.
    3.  Em seguida, chama `src.rag.rag_data_loader.indexar_dados(documentos)`:
        *   **Ação**: Obtém `get_embedding_model()` (`HuggingFaceEmbeddings`).
        *   Cria e salva o `FAISS` vector store em `data/indice_faiss`.
    4.  Retorna o `vetorstore` FAISS.

### 2.2.5. Fluxo de Resposta RAG (`src/rag/rag_core.py`)

*   **`responder_pergunta_rag(pergunta, vetorstore)`** é a função central para o chat.
    1.  Chama `get_llm()` para obter a instância do LLM (Groq ou OpenAI).
    2.  Cria um `retriever` a partir do `vetorstore`.
    3.  Chama `construir_grafo_rag(retriever, llm)` para criar o pipeline LangGraph.
    4.  Invoca o grafo com a pergunta. Dentro do grafo:
        *   `recuperar_docs` (node): Usa o `retriever` para buscar documentos relevantes do `vetorstore` com base na `pergunta`.
        *   `gerar_resposta` (node):
            *   Chama `src.rag.chat_history.carregar_contexto_anterior()` para obter o histórico e dados estruturados.
            *   Cria um prompt com a `pergunta`, o `context` dos documentos recuperados e o `contexto_anterior`.
            *   Invoca o `llm` com o prompt.
    5.  Após receber a `resposta` do grafo:
        *   Chama `src.rag.chat_history.salvar_historico(pergunta, resposta_texto)`.
        *   Chama `tentar_extrair_dados(resposta_texto)` para buscar tabelas ou JSON.
        *   Se dados estruturados forem encontrados, chama `salvar_dados_estruturados(dados_estruturados)`.
    6.  Retorna a `resposta_texto` do LLM.

### 2.2.6. Fluxo de Histórico de Chat (`src/rag/chat_history.py`)

*   **`salvar_historico(pergunta, resposta)`**: Anexa a interação ao `historico.txt`.
*   **`carregar_contexto_anterior()`**:
    1.  Lê o `historico.txt`.
    2.  Lista e lê todos os arquivos `.csv` e `.json` em `chat_outputs/dados/`.
    3.  Combina tudo em uma única string de contexto para o LLM.
*   **`limpar_contexto()`**: Remove `historico.txt` e todos os arquivos/diretórios em `chat_outputs/dados/` e `chat_outputs/graficos/`.

---

Esta seção pode ser usada como base para as próximas seções de detalhamento de cada módulo e documentação dos componentes principais, já que ela estabelece a ordem e as interconexões. 

## 3. Detalhamento de Cada Módulo

Esta seção fornece uma descrição detalhada de cada módulo do projeto, incluindo suas funções, classes, parâmetros, retornos, dependências internas e como são utilizados no fluxo geral.

### 3.1. Módulos ETL

#### 3.1.1. `src/etl/extractor.py`

**Descrição Geral:** Este módulo é encarregado de extrair os dados brutos de Pokémon da PokeAPI. Ele implementa estratégias para garantir a robustez da extração, como retentativas automáticas em caso de falha de conexão e o uso de paralelismo para acelerar a busca de múltiplos Pokémon. Além disso, oferece suporte a cache para evitar requisições desnecessárias e um modo de dados de exemplo para desenvolvimento ou em situações de API indisponível.

**Dependências Internas:**
*   `src.utils.cache`: Para salvar e carregar dados em cache.
*   `src.config.settings`: Para configurações como URLs da API, caminhos de cache, quantidade de Pokémon, etc.

**Funções:**

*   `_criar_sessao_com_retentativas() -> requests.Session`
    *   **Descrição**: Função interna auxiliar que cria e configura uma sessão `requests` com uma política de retentativas. Isso ajuda a lidar com instabilidades temporárias da rede ou da API.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: Uma instância de `requests.Session` configurada com `HTTPAdapter` e `Retry`.
    *   **Chamado por**: `testar_conexao_api()` e `buscar_dados_pokemon()`.

*   `testar_conexao_api() -> bool`
    *   **Descrição**: Testa a conectividade com a PokeAPI realizando uma requisição simples ao endpoint de um Pokémon específico.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: `True` se a conexão for bem-sucedida (status 2xx), `False` caso contrário. Logs de erro são gerados em caso de falha.
    *   **Chamado por**: `buscar_dados_pokemon()` para verificar a disponibilidade da API antes de iniciar a extração em massa.

*   `gerar_dados_exemplo(quantidade: int = QUANTIDADE_POKEMON) -> List[Dict[str, Any]]`
    *   **Descrição**: Gera uma lista de dicionários com dados de Pokémon de exemplo. Útil para testes, desenvolvimento offline ou como fallback quando a API está indisponível.
    *   **Parâmetros**:
        *   `quantidade` (int): O número de Pokémon de exemplo a serem gerados. O valor padrão é `QUANTIDADE_POKEMON` definido em `src/config/settings.py`.
    *   **Retornos**: Uma `List` de `Dict`s, onde cada dicionário representa um Pokémon com uma estrutura simplificada (id, name, types, stats).
    *   **Chamado por**: `buscar_dados_pokemon()` quando a API está indisponível e `USAR_DADOS_EXEMPLO` é `True`.

*   `_buscar_pokemon_individual(pokemon_id: int, sessao: requests.Session) -> Optional[Dict[str, Any]]`
    *   **Descrição**: Função interna que busca os dados de um único Pokémon pela sua ID. Utiliza a sessão com retentativas fornecida.
    *   **Parâmetros**:
        *   `pokemon_id` (int): A ID numérica do Pokémon a ser buscado.
        *   `sessao` (requests.Session): A sessão HTTP pré-configurada para a requisição.
    *   **Retornos**: Um `Dict` contendo os dados JSON do Pokémon se a requisição for bem-sucedida, ou `None` em caso de erro na requisição (logado).
    *   **Chamado por**: `buscar_dados_pokemon()` em um contexto de paralelismo (`ThreadPoolExecutor`).

*   `buscar_dados_pokemon(quantidade: int = QUANTIDADE_POKEMON, usar_cache: bool = USAR_CACHE, usar_dados_exemplo: bool = USAR_DADOS_EXEMPLO) -> List[Dict[str, Any]]`
    *   **Descrição**: A função principal deste módulo. Orquestra a busca de dados de Pokémon, priorizando o cache, testando a conexão com a API e usando paralelismo para buscar múltiplos Pokémon simultaneamente. Em caso de falha da API, pode retornar dados de exemplo.
    *   **Parâmetros**:
        *   `quantidade` (int): O número total de Pokémon a serem buscados. Padrão: `QUANTIDADE_POKEMON`.
        *   `usar_cache` (bool): Se `True`, tenta carregar dados do cache antes de buscar na API e salva no cache após uma busca bem-sucedida. Padrão: `USAR_CACHE`.
        *   `usar_dados_exemplo` (bool): Se `True`, usa dados de exemplo como fallback caso a API esteja inacessível ou falhe completamente. Padrão: `USAR_DADOS_EXEMPLO`.
    *   **Retornos**: Uma `List` de `Dict`s, contendo os dados brutos de todos os Pokémon extraídos. Retorna uma lista vazia ou dados de exemplo se nenhuma extração for bem-sucedida.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

#### 3.1.2. `src/etl/transformer.py`

**Descrição Geral:** Este módulo foca na fase de transformação do pipeline ETL. Ele pega os dados brutos de Pokémon (geralmente uma lista de dicionários) e os converte em um `pandas.DataFrame` limpo e estruturado. Além da estruturação básica, ele adiciona uma categorização de Pokémon e oferece funções para análises sumárias, como contagem por tipo, média de atributos por tipo e identificação dos Pokémon com maior experiência base.

**Dependências Internas:** Nenhuma específica dentro do projeto, apenas bibliotecas padrão como `pandas` e `logging`.

**Funções:**

*   `transformar_dados_pokemon(dados_brutos: List[Dict[str, Any]]) -> pd.DataFrame`
    *   **Descrição**: Esta é a função central do módulo. Ela itera sobre a lista de dicionários de dados brutos de Pokémon e extrai informações relevantes (`id`, `name`, `types`, `base_experience`, `stats`). As estatísticas são achatadas em colunas separadas (HP, Ataque, Defesa) e é adicionada uma coluna 'Categoria' baseada na 'Experiencia_Base' (Forte, Médio, Fraco). O resultado é um `pd.DataFrame` bem formatado.
    *   **Parâmetros**:
        *   `dados_brutos` (`List[Dict[str, Any]]`): Uma lista de dicionários, onde cada dicionário contém os dados JSON brutos de um Pokémon, conforme extraído da PokeAPI.
    *   **Retornos**: Um `pd.DataFrame` com as colunas 'ID', 'Nome', 'Tipos', 'Experiencia_Base', 'HP', 'Ataque', 'Defesa' e 'Categoria'.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

*   `contar_pokemon_por_tipo(tabela: pd.DataFrame) -> Dict[str, int]`
    *   **Descrição**: Analisa a coluna 'Tipos' do DataFrame de Pokémon e conta a ocorrência de cada tipo. Lida com Pokémon que possuem múltiplos tipos, garantindo que cada tipo seja contado individualmente.
    *   **Parâmetros**:
        *   `tabela` (`pd.DataFrame`): O DataFrame de Pokémon com a coluna 'Tipos'.
    *   **Retornos**: Um `Dict` onde as chaves são os nomes dos tipos de Pokémon (string) e os valores são suas respectivas contagens (inteiro).
    *   **Chamado por**: Pode ser usado por `src.etl.reporter.py` para gerar relatórios ou gráficos.

*   `calcular_media_stats_por_tipo(tabela: pd.DataFrame) -> pd.DataFrame`
    *   **Descrição**: Calcula a média das estatísticas (HP, Ataque, Defesa) para cada tipo de Pokémon. Se um Pokémon tem múltiplos tipos, ele contribui para a média de cada um desses tipos.
    *   **Parâmetros**:
        *   `tabela` (`pd.DataFrame`): O DataFrame de Pokémon, esperado que contenha as colunas 'Tipos', 'HP', 'Ataque' e 'Defesa'.
    *   **Retornos**: Um `pd.DataFrame` indexado por 'Tipos' com colunas 'HP', 'Ataque' e 'Defesa', contendo as médias arredondadas para uma casa decimal.
    *   **Chamado por**: Pode ser usado por `src.etl.reporter.py` para gerar relatórios ou gráficos.

*   `encontrar_top_5_experiencia(tabela: pd.DataFrame) -> pd.DataFrame`
    *   **Descrição**: Identifica e retorna os 5 Pokémon com os maiores valores na coluna 'Experiencia_Base'.
    *   **Parâmetros**:
        *   `tabela` (`pd.DataFrame`): O DataFrame de Pokémon, esperado que contenha a coluna 'Experiencia_Base'.
    *   **Retornos**: Um `pd.DataFrame` contendo as linhas correspondentes aos 5 Pokémon de maior experiência base.
    *   **Chamado por**: Pode ser usado por `src.etl.reporter.py` para gerar relatórios ou gráficos.

#### 3.1.3. `src/etl/reporter.py`

**Descrição Geral:** Este módulo é o responsável pela "carga" e "relatório" no contexto do ETL. Ele pega os dados transformados e os apresenta de maneiras significativas: salvando-os como arquivos CSV, gerando relatórios textuais consolidados e criando visualizações gráficas usando `matplotlib` e `seaborn`. Inclui uma funcionalidade de `gerar_grafico_automatico` que tenta interpretar solicitações de plotagem a partir de texto.

**Dependências Internas:**
*   `src.config.settings`: Para caminhos de saída de arquivos de gráficos e CSV.
*   `main.py`: `gerar_grafico_automatico` é chamado diretamente pelo `main.py` para o comando `/plot`.

**Funções:**

*   `gerar_grafico_tipos(contagem_tipos: Dict[str, int], caminho_saida: str = CAMINHO_GRAFICO_TIPOS)`
    *   **Descrição**: Cria um gráfico de barras visualizando a distribuição de Pokémon por tipo. Salva o gráfico como um arquivo de imagem.
    *   **Parâmetros**:
        *   `contagem_tipos` (`Dict[str, int]`): Um dicionário resultante da função `contar_pokemon_por_tipo` em `transformer.py`, mapeando tipos de Pokémon para suas contagens.
        *   `caminho_saida` (str): O caminho completo onde a imagem do gráfico será salva. O padrão é `CAMINHO_GRAFICO_TIPOS` de `settings.py`.
    *   **Retornos**: Nenhum. O gráfico é salvo diretamente no caminho especificado.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

*   `exportar_relatorio_csv(tabela: pd.DataFrame, caminho_saida: str = CAMINHO_RELATORIO_CSV)`
    *   **Descrição**: Salva um `pd.DataFrame` fornecido em um arquivo CSV. É útil para persistir os dados transformados em um formato tabular que pode ser facilmente inspecionado ou utilizado por outras ferramentas.
    *   **Parâmetros**:
        *   `tabela` (`pd.DataFrame`): O DataFrame de Pokémon a ser exportado.
        *   `caminho_saida` (str): O caminho completo onde o arquivo CSV será salvo. O padrão é `CAMINHO_RELATORIO_CSV` de `settings.py`.
    *   **Retornos**: Nenhum. O DataFrame é salvo como um arquivo CSV.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

*   `gerar_relatorio_consolidado(top_5: pd.DataFrame, media_por_tipo: pd.DataFrame, caminho_saida: str = "data/relatorio_consolidado.txt")`
    *   **Descrição**: Compila um relatório em formato de texto (`.txt`) que resume as principais análises geradas. Inclui os 5 Pokémon com maior experiência base e as médias de atributos por tipo.
    *   **Parâmetros**:
        *   `top_5` (`pd.DataFrame`): DataFrame contendo os 5 Pokémon com maior experiência, geralmente resultado de `encontrar_top_5_experiencia` de `transformer.py`.
        *   `media_por_tipo` (`pd.DataFrame`): DataFrame com as médias de HP, Ataque e Defesa por tipo, geralmente resultado de `calcular_media_stats_por_tipo` de `transformer.py`.
        *   `caminho_saida` (str): O caminho completo onde o arquivo de texto será salvo. O padrão é `"data/relatorio_consolidado.txt"`.
    *   **Retornos**: Nenhum. O relatório é salvo como um arquivo de texto.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

*   `gerar_resumo_relatorio(tabela: pd.DataFrame, analise_tipos: Dict[str, Any]) -> Dict[str, Any]`
    *   **Descrição**: Calcula e loga um resumo estatístico das informações dos Pokémon. Inclui o total de Pokémon, tipos únicos, contagem por categoria (Forte, Médio, Fraco) e médias gerais de HP, Ataque e Defesa.
    *   **Parâmetros**:
        *   `tabela` (`pd.DataFrame`): O DataFrame principal com os dados de Pokémon.
        *   `analise_tipos` (`Dict[str, Any]`): Um dicionário contendo informações de análise de tipos, especialmente a contagem de tipos.
    *   **Retornos**: Um dicionário com as estatísticas resumidas.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

*   `_plot_from_dataframe(ax, dados: pd.DataFrame, tipo: Optional[str])`
    *   **Descrição**: Função auxiliar interna para gerar gráficos a partir de um DataFrame. Suporta gráficos de pizza, linha e barra.
    *   **Parâmetros**:
        *   `ax`: Objeto `Axes` do Matplotlib para plotagem.
        *   `dados` (`pd.DataFrame`): DataFrame a ser plotado.
        *   `tipo` (Optional[str]): Tipo de gráfico ('pizza', 'linha', 'barras').
    *   **Retornos**: Nenhum. A plotagem é feita no objeto `ax`.
    *   **Chamado por**: `gerar_grafico_automatico()`.

*   `_plot_from_dict(ax, dados: Dict[str, Any], tipo: Optional[str])`
    *   **Descrição**: Função auxiliar interna para gerar gráficos a partir de um dicionário. Suporta gráficos de pizza, linha e barra.
    *   **Parâmetros**:
        *   `ax`: Objeto `Axes` do Matplotlib para plotagem.
        *   `dados` (`Dict[str, Any]`): Dicionário a ser plotado.
        *   `tipo` (Optional[str]): Tipo de gráfico ('pizza', 'linha', 'barras').
    *   **Retornos**: Nenhum. A plotagem é feita no objeto `ax`.
    *   **Chamado por**: `gerar_grafico_automatico()`.

*   `_processar_especificacao_plot(ax, dados: pd.DataFrame, especificacao: str) -> bool`
    *   **Descrição**: Função auxiliar interna que tenta interpretar uma `especificacao_plot` em texto livre e gerar um gráfico específico com base nela. Por exemplo, pode plotar a distribuição de HP, ataque, defesa, diferença de HP ou todos os stats.
    *   **Parâmetros**:
        *   `ax`: Objeto `Axes` do Matplotlib para plotagem.
        *   `dados` (`pd.DataFrame`): DataFrame a ser analisado e plotado.
        *   `especificacao` (str): String com a solicitação de plotagem.
    *   **Retornos**: `True` se um gráfico foi gerado com sucesso com base na especificação, `False` caso contrário (especificação ambígua ou dados ausentes).
    *   **Chamado por**: `gerar_grafico_automatico()`.

*   `gerar_grafico_automatico(dados: Union[pd.DataFrame, Dict, List], caminho_saida: Optional[str] = None, tipo: Optional[str] = None, titulo: str = "Gráfico Gerado Automaticamente", especificacao_plot: Optional[str] = None) -> Optional[str]`
    *   **Descrição**: A função mais flexível para geração de gráficos. Pode receber dados em diferentes formatos (DataFrame, dicionário, lista) e tenta criar um gráfico. Se `especificacao_plot` for fornecida, ela tenta criar um gráfico contextualizado; caso contrário, usa o `tipo` de gráfico padrão. Gera um nome de arquivo de saída automático se `caminho_saida` não for fornecido.
    *   **Parâmetros**:
        *   `dados` (`Union[pd.DataFrame, Dict, List]`): Os dados a serem plotados.
        *   `caminho_saida` (Optional[str]): O caminho para salvar o gráfico. Se `None`, um caminho padrão com timestamp é gerado.
        *   `tipo` (Optional[str]): O tipo de gráfico ('barras', 'pizza', 'linha'). Usado como fallback se `especificacao_plot` não for clara.
        *   `titulo` (str): O título do gráfico.
        *   `especificacao_plot` (Optional[str]): Uma string descrevendo o que plotar (ex: "diferenca do hp", "apenas hp").
    *   **Retornos**: O caminho completo do arquivo de imagem salvo se o gráfico for gerado com sucesso, ou `None` em caso de falha.
    *   **Chamado por**: `main.py` (para o comando `/plot`), e potencialmente por funções RAG para gerar visualizações dinâmicas.

#### 3.1.4. `src/etl/pipeline.py`

**Descrição Geral:** Este módulo atua como o orquestrador principal do pipeline de Extração, Transformação e Carregamento (ETL). Ele define a sequência de operações, chamando as funções apropriadas dos módulos `extractor.py`, `transformer.py` e `reporter.py` para processar os dados de Pokémon de ponta a ponta. Além das fases tradicionais de ETL, ele também integra a etapa de preparação e indexação de dados para o sistema RAG (Retrieval Augmented Generation).

**Dependências Internas:**
*   `src.utils.logger`: Para configurar o sistema de log da aplicação.
*   `src.etl.extractor`: Para a função `buscar_dados_pokemon`.
*   `src.etl.transformer`: Para as funções `transformar_dados_pokemon`, `contar_pokemon_por_tipo`, `calcular_media_stats_por_tipo` e `encontrar_top_5_experiencia`.
*   `src.etl.reporter`: Para as funções `gerar_grafico_tipos`, `exportar_relatorio_csv`, `gerar_resumo_relatorio` e `gerar_relatorio_consolidado`.
*   `src.rag.rag_data_loader`: Para as funções `gerar_documentos_para_rag` e `indexar_dados`.

**Funções:**

*   `executar_pipeline()`
    *   **Descrição**: Esta é a função principal do módulo e o ponto de entrada para a execução do pipeline ETL completo. Ela coordena todas as fases:
        1.  **Configuração de Logs**: Inicializa o sistema de logs.
        2.  **Extração**: Chama `buscar_dados_pokemon()` para obter os dados brutos da PokeAPI (ou cache/exemplos).
        3.  **Verificação de Dados**: Se nenhum dado for obtido, o pipeline é encerrado.
        4.  **Transformação**: Chama `transformar_dados_pokemon()` para converter os dados brutos em um `pd.DataFrame` estruturado.
        5.  **Análise**: Realiza análises chamando `contar_pokemon_por_tipo`, `calcular_media_stats_por_tipo` e `encontrar_top_5_experiencia` do módulo `transformer`.
        6.  **Geração de Relatórios**: Invoca `exportar_relatorio_csv`, `gerar_grafico_tipos` e `gerar_relatorio_consolidado` do módulo `reporter` para persistir e visualizar os resultados.
        7.  **Resumo de Relatório**: Gera um resumo das estatísticas via `gerar_resumo_relatorio` para fins de log.
        8.  **Indexação para RAG**: Prepara os dados para o sistema de IA chamando `gerar_documentos_para_rag` e `indexar_dados` do módulo `rag_data_loader`.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: Nenhum. A função executa as operações e loga o progresso e quaisquer erros. Levanta exceções em caso de erro fatal.
    *   **Chamado por**: `main.py`, quando o argumento `acao` é "pipeline".

### 3.2. Módulos RAG (Retrieval Augmented Generation)

#### 3.2.1. `src/rag/rag_core.py`

**Descrição Geral:** Este módulo implementa a lógica central do sistema RAG. Ele lida com a seleção do LLM, a construção do grafo de execução (`LangGraph`) que gerencia o fluxo de recuperação de documentos e geração de respostas, a extração de dados estruturados das respostas do LLM e o salvamento desses dados. É a ponte entre a pergunta do usuário e a resposta enriquecida com o contexto dos dados de Pokémon.

**Dependências Internas:**
*   `src.rag.chat_history`: Para carregar o histórico de conversas anterior e salvar o novo histórico.
*   Bibliotecas externas: `os`, `re`, `json`, `pandas`, `datetime`, `langgraph`, `langchain_openai`, `langchain_groq`.

**Funções:**

*   `get_llm()`
    *   **Descrição**: Função utilitária que seleciona e retorna uma instância do Large Language Model (LLM) a ser utilizado. Prioriza o uso da API do Groq (Llama 3) se a chave `GROQ_API_KEY` estiver disponível no ambiente; caso contrário, tenta usar a API da OpenAI (GPT-3.5-turbo) com a `OPENAI_API_KEY`.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: Uma instância de `ChatGroq` ou `ChatOpenAI`, ou `None` se nenhuma chave de API for encontrada.
    *   **Chamado por**: `responder_pergunta_rag()`.

*   `construir_grafo_rag(retriever, llm)`
    *   **Descrição**: Constrói e compila um grafo de execução usando `LangGraph`. Este grafo define o pipeline RAG de dois estágios:
        1.  **`recuperar_docs`**: Utiliza o `retriever` fornecido para buscar documentos relevantes no vetorstore com base na pergunta do usuário.
        2.  **`gerar_resposta`**: Combina o contexto dos documentos recuperados e o histórico de conversas anterior em um prompt, que é então enviado ao LLM para gerar a resposta final. Inclui instruções para o LLM responder em português, usar o contexto e retornar dados estruturados (tabelas/JSON) quando aplicável.
    *   **Parâmetros**:
        *   `retriever`: Um objeto `Retriever` (geralmente do `FAISS` ou similar) configurado para buscar documentos.
        *   `llm`: A instância do LLM (obtida via `get_llm()`).
    *   **Retornos**: Um objeto de grafo `LangGraph` compilado, pronto para ser invocado com perguntas.
    *   **Chamado por**: `responder_pergunta_rag()`.

*   `tentar_extrair_dados(resposta_texto: str)`
    *   **Descrição**: Tenta extrair dados estruturados (tabelas formatadas em Markdown ou blocos JSON) do texto de resposta gerado pelo LLM. Utiliza expressões regulares para identificar e parsear esses formatos.
    *   **Parâmetros**:
        *   `resposta_texto` (str): A string de texto da resposta do LLM.
    *   **Retornos**: Um `pd.DataFrame` (para tabelas Markdown), um `dict` ou `list` (para JSON), ou `None` se nenhum dado estruturado puder ser extraído.
    *   **Chamado por**: `responder_pergunta_rag()` para processar a saída do LLM.

*   `salvar_dados_estruturados(dados)`
    *   **Descrição**: Salva os dados estruturados extraídos (DataFrame, lista ou dicionário) em um arquivo no diretório `chat_outputs/dados`. Salva DataFrames como CSV e listas/dicionários como JSON, utilizando um timestamp no nome do arquivo para garantir unicidade.
    *   **Parâmetros**:
        *   `dados`: Os dados estruturados a serem salvos (pode ser `pd.DataFrame`, `list` ou `dict`).
    *   **Retornos**: O caminho completo do arquivo onde os dados foram salvos, ou `None` se o formato dos dados não for suportado.
    *   **Chamado por**: `responder_pergunta_rag()` se dados estruturados forem extraídos com sucesso.

*   `responder_pergunta_rag(pergunta: str, vetorstore)`
    *   **Descrição**: A função principal para interagir com o sistema RAG. Ela obtém o LLM, configura o `retriever` a partir do `vetorstore`, constrói e invoca o grafo RAG com a pergunta do usuário. Após obter a resposta do LLM, imprime-a, salva no histórico de chat e tenta extrair e salvar quaisquer dados estruturados presentes na resposta.
    *   **Parâmetros**:
        *   `pergunta` (str): A pergunta do usuário.
        *   `vetorstore`: O objeto do banco de vetores (`FAISS` ou similar) que contém os documentos indexados.
    *   **Retornos**: A string da resposta do LLM, ou `None` se houver falha na inicialização do LLM/vetorstore ou na geração da resposta.
    *   **Chamado por**: `main.py` (dentro da função `chat_interativo`) e `api.py` (endpoint `/chat`).

#### 3.2.2. `src/rag/chat_history.py`

**Descrição Geral:** Este módulo é responsável por gerenciar o histórico de interações do chat e os dados estruturados (CSV/JSON) que foram extraídos e salvos durante sessões anteriores. Ele garante que o LLM possa ter um "contexto" das conversas passadas e dos resultados de análises prévias, enriquecendo as respostas e permitindo interações mais coerentes e informadas.

**Dependências Internas:** Nenhuma específica dentro do projeto, apenas bibliotecas padrão como `os`, `json`, `pandas` e `datetime`.

**Variáveis Globais:**
*   `CHAT_OUTPUTS_DIR` (`"chat_outputs"`): O diretório base para todas as saídas do chat.
*   `DADOS_DIR` (`os.path.join(CHAT_OUTPUTS_DIR, "dados")`): Subdiretório onde os dados estruturados (CSV/JSON) são salvos.
*   `HISTORICO_PATH` (`os.path.join(CHAT_OUTPUTS_DIR, "historico.txt")`): Caminho do arquivo de texto onde o histórico de perguntas e respostas é armazenado.

**Funções:**

*   `salvar_historico(pergunta: str, resposta: str)`
    *   **Descrição**: Persiste uma nova interação de pergunta e resposta no arquivo `historico.txt`. Cada entrada inclui um timestamp para rastreamento.
    *   **Parâmetros**:
        *   `pergunta` (str): A pergunta feita pelo usuário.
        *   `resposta` (str): A resposta gerada pelo sistema (LLM).
    *   **Retornos**: Nenhum. O histórico é anexado ao arquivo.
    *   **Chamado por**: `src.rag.rag_core.responder_pergunta_rag()` após gerar uma resposta.

*   `carregar_contexto_anterior() -> str`
    *   **Descrição**: Agrega todo o histórico de conversas e os conteúdos dos arquivos de dados estruturados previamente salvos (`.csv` e `.json`) em uma única string. Esta string é formatada para ser injetada no prompt do LLM, fornecendo o "contexto anterior" para a geração de respostas.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: Uma string contendo o histórico textual e os dados estruturados anteriores, formatados. Retorna uma string vazia se não houver histórico ou dados.
    *   **Chamado por**: `src.rag.rag_core.construir_grafo_rag()` (especificamente pela função `gerar_resposta` dentro do grafo) para enriquecer o prompt do LLM.

*   `limpar_contexto(confirmar: bool = True)`
    *   **Descrição**: Exclui todos os arquivos de histórico (`historico.txt`), dados estruturados (do diretório `chat_outputs/dados`) e gráficos (do diretório `chat_outputs/graficos`), efetivamente resetando a memória do chat. Inclui uma confirmação para evitar exclusões acidentais, se `confirmar` for `True`.
    *   **Parâmetros**:
        *   `confirmar` (bool): Se `True`, o usuário é solicitado a confirmar a ação de limpeza. Padrão: `True`.
    *   **Retornos**: Nenhum. Realiza a exclusão dos arquivos e diretórios e imprime mensagens de status.
    *   **Chamado por**: `main.py` (dentro da função `chat_interativo`) e `api.py` (endpoint `/clear_context`).

#### 3.2.3. `src/rag/rag_data_loader.py`

**Descrição Geral:** Este módulo é essencial para a criação e gestão do banco de vetores (vector store) que o sistema RAG utiliza para recuperar informações relevantes. Ele lida com a criação de embeddings (representações numéricas do texto), a construção do `VectorStore` (utilizando FAISS) e o carregamento desse `VectorStore` para uso no chat RAG.

**Dependências Internas:** Nenhuma específica dentro do projeto, apenas bibliotecas externas como `os`, `pandas`, `langchain_core.documents.Document`, `langchain_community.vectorstores.FAISS` e `langchain_huggingface.HuggingFaceEmbeddings`.

**Funções:**

*   `get_embedding_model()`
    *   **Descrição**: Inicializa e retorna o modelo de embedding da Hugging Face (`all-MiniLM-L6-v2`). Modelos de embedding são cruciais para converter texto em vetores numéricos que podem ser comparados para encontrar similaridades semânticas.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: Uma instância de `HuggingFaceEmbeddings`.
    *   **Chamado por**: `indexar_dados()` e `carregar_vetorstore()`.

*   `verificar_csv_existe(caminho_csv: str = "data/relatorio.csv") -> bool`
    *   **Descrição**: Verifica se o arquivo CSV especificado (que contém os dados de Pokémon transformados) existe no sistema de arquivos e se não está vazio. É uma pré-condição para a geração de documentos para o RAG.
    *   **Parâmetros**:
        *   `caminho_csv` (str): O caminho para o arquivo CSV a ser verificado. O padrão é `"data/relatorio.csv"`.
    *   **Retornos**: `True` se o arquivo existe e não está vazio, `False` caso contrário.
    *   **Chamado por**: `gerar_documentos_para_rag()`.

*   `gerar_documentos_para_rag(caminho_csv: str = "data/relatorio.csv") -> list[Document]`
    *   **Descrição**: Lê o arquivo CSV de dados de Pokémon transformados e converte cada linha em um objeto `LangChain Document`. Cada `Document` terá o conteúdo da linha formatado como uma string legível, que é o texto que será indexado.
    *   **Parâmetros**:
        *   `caminho_csv` (str): O caminho para o arquivo CSV de onde os documentos serão gerados. O padrão é `"data/relatorio.csv"`.
    *   **Retornos**: Uma `list` de objetos `Document`, onde cada `Document` representa um Pokémon. Retorna uma lista vazia se o CSV não for encontrado, estiver vazio ou ocorrer um erro de leitura.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

*   `indexar_dados(documentos: list[Document])`
    *   **Descrição**: Pega uma lista de `Document`s, gera os embeddings para cada um usando o modelo de embedding e, em seguida, constrói um banco de vetores FAISS (Facebook AI Similarity Search) a partir desses embeddings. O FAISS é então salvo localmente para persistência, permitindo que seja carregado rapidamente em sessões futuras.
    *   **Parâmetros**:
        *   `documentos` (`list[Document]`): A lista de documentos LangChain a serem indexados.
    *   **Retornos**: A instância do `FAISS` VectorStore criada, ou `None` se não houver documentos para indexar.
    *   **Chamado por**: `src.etl.pipeline.executar_pipeline()`.

*   `carregar_vetorstore()`
    *   **Descrição**: Tenta carregar um banco de vetores FAISS previamente salvo do disco. Isso evita a necessidade de reindexar os dados a cada inicialização do sistema, acelerando o tempo de carregamento do chat.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: Uma instância do `FAISS` VectorStore carregada, ou `None` se o índice não for encontrado no caminho especificado.
    *   **Chamado por**: `src.rag_builder.inicializar_rag()`.

#### 3.2.4. `src/rag_builder.py`

**Descrição Geral:** Este módulo atua como um construtor ou inicializador para o sistema RAG. Sua principal responsabilidade é garantir que um `VectorStore` (índice FAISS) esteja disponível. Ele tenta carregar um índice existente; se não encontrar, ele orquestra a geração de documentos a partir dos dados e a subsequente indexação para criar um novo `VectorStore`.

**Dependências Internas:**
*   `src.rag.rag_data_loader`: Para as funções `carregar_vetorstore`, `gerar_documentos_para_rag` e `indexar_dados`.

**Funções:**

*   `inicializar_rag()`
    *   **Descrição**: Esta é a função principal do módulo. Ela primeiro tenta carregar um `VectorStore` FAISS salvo localmente usando `carregar_vetorstore()`. Se um `VectorStore` não for encontrado (ou seja, é a primeira execução ou o índice foi limpo/removido), ela prossegue para gerar os documentos para o RAG usando `gerar_documentos_para_rag()` e, em seguida, os indexa para criar um novo `VectorStore` usando `indexar_dados()`.
    *   **Parâmetros**: Nenhum.
    *   **Retornos**: A instância do `VectorStore` (FAISS) pronta para uso. Retorna `None` se o índice não puder ser carregado ou criado com sucesso.
    *   **Chamado por**: `main.py` (dentro da função `chat_interativo`) e `api.py` (evento de startup).

### 3.3. Módulo API

#### 3.3.1. `api.py`

**Descrição Geral:** Este arquivo define a API RESTful do projeto usando FastAPI, permitindo que as funcionalidades de ETL e RAG sejam acessadas via requisições HTTP, ideal para integração com um frontend.

**Dependências Internas:**
*   `src.etl.pipeline`: Para a função `executar_pipeline`.
*   `src.rag_builder`: Para a função `inicializar_rag`.
*   `src.rag.rag_core`: Para a função `responder_pergunta_rag`.
*   `src.rag.chat_history`: Para a função `limpar_contexto`.
*   `src.etl.reporter`: Para a função `gerar_grafico_automatico` (embora não diretamente exposta como endpoint para uso genérico, a funcionalidade de plotagem é acessível).

**Dependências Externas:**
*   `fastapi`: O framework web principal.
*   `fastapi.responses.FileResponse`: Para retornar arquivos (gráficos).
*   `fastapi.middleware.cors.CORSMiddleware`: Para lidar com políticas de Cross-Origin Resource Sharing.
*   `uvicorn`: Servidor ASGI para rodar a aplicação FastAPI.
*   `os`: Para operações de sistema de arquivos.
*   `pandas`: Para leitura e manipulação de arquivos CSV.
*   `json`: Para leitura e manipulação de arquivos JSON.

**Variáveis Globais:**
*   `vetorstore_rag`: Uma variável global que armazena a instância do `VectorStore` (FAISS) carregada na inicialização do aplicativo. É crucial para o funcionamento do endpoint `/chat`.

**Event Handlers:**

*   `@app.on_event("startup") async def startup_event():`
    *   **Descrição**: Esta função assíncrona é executada uma única vez quando o servidor FastAPI é iniciado. Ela é responsável por inicializar o sistema RAG, carregando ou criando o `VectorStore`. Isso garante que o chatbot esteja pronto para responder às perguntas assim que a API estiver online.
    *   **Fluxo**: Chama `src.rag_builder.inicializar_rag()` e armazena o resultado em `vetorstore_rag`. Loga mensagens de sucesso ou erro na inicialização.

**Endpoints da API:**

1.  **`GET /status`**
    *   **Descrição**: Um endpoint simples para verificar se a API está online e respondendo.
    *   **Parâmetros**: Nenhum.
    *   **Respostas**:
        *   `200 OK`: `{"status": "API está online!"}`

2.  **`POST /run_pipeline`**
    *   **Descrição**: Aciona a execução completa do pipeline ETL (Extração, Transformação, Carregamento de dados de Pokémon).
    *   **Parâmetros**: Nenhum (requisição POST vazia).
    *   **Respostas**:
        *   `200 OK`: `{"message": "Pipeline de ETL executado com sucesso!"}`
        *   `500 Internal Server Error`: `{"detail": "Erro ao executar o pipeline: <mensagem de erro>"}` (se ocorrer uma exceção durante a execução do pipeline).
    *   **Dependências**: `src.etl.pipeline.executar_pipeline()`.

3.  **`POST /chat`**
    *   **Descrição**: Permite interagir com o chatbot RAG, enviando uma pergunta e recebendo uma resposta gerada pelo LLM com base nos dados indexados.
    *   **Parâmetros**:
        *   Corpo da requisição (JSON): `{"pergunta": "Sua pergunta aqui"}`
    *   **Respostas**:
        *   `200 OK`: `{"pergunta": "Sua pergunta aqui", "resposta": "Resposta gerada pelo chatbot"}`
        *   `400 Bad Request`: `{"detail": "Pergunta não fornecida."}` (se a pergunta estiver ausente no corpo da requisição).
        *   `503 Service Unavailable`: `{"detail": "Chatbot não inicializado. Execute o pipeline primeiro."}` (se o `vetorstore_rag` não foi inicializado com sucesso).
        *   `500 Internal Server Error`: `{"detail": "Não foi possível obter uma resposta do chatbot."}` (se `responder_pergunta_rag` retornar `None`).
    *   **Dependências**: `vetorstore_rag` (variável global), `src.rag.rag_core.responder_pergunta_rag()`.

4.  **`POST /clear_context`**
    *   **Descrição**: Limpa o histórico de conversas do chatbot e os arquivos de dados estruturados e gráficos salvos (`chat_outputs/`).
    *   **Parâmetros**: Nenhum (requisição POST vazia).
    *   **Respostas**:
        *   `200 OK`: `{"message": "Contexto do chatbot limpo com sucesso!}"`
        *   `500 Internal Server Error`: `{"detail": "Erro ao limpar o contexto: <mensagem de erro>"}`.
    *   **Dependências**: `src.rag.chat_history.limpar_contexto(confirmar=False)`.

5.  **`GET /get_pipeline_report`**
    *   **Descrição**: Retorna o relatório principal do pipeline ETL (`data/relatorio.csv`) em formato JSON (lista de dicionários).
    *   **Parâmetros**: Nenhum.
    *   **Respostas**:
        *   `200 OK`: `[{"ID": 1, "Nome": "Bulbasaur", ...}]` (JSON array de objetos).
        *   `404 Not Found`: `{"detail": "Relatório do pipeline não encontrado. Execute o pipeline primeiro."}`.
        *   `500 Internal Server Error`: `{"detail": "Erro ao ler o relatório CSV: <mensagem de erro>"}`.
    *   **Dependências**: Leitura de `data/relatorio.csv` usando `pandas`.

6.  **`GET /get_pipeline_chart`**
    *   **Descrição**: Retorna a imagem do gráfico de tipos gerado pelo pipeline (`data/grafico_tipos.png`).
    *   **Parâmetros**: Nenhum.
    *   **Respostas**:
        *   `200 OK`: Retorna o conteúdo da imagem PNG.
        *   `404 Not Found`: `{"detail": "Gráfico do pipeline não encontrado. Execute o pipeline primeiro."}`.
    *   **Dependências**: Leitura de `data/grafico_tipos.png` e `FileResponse`.

7.  **`GET /get_chat_history`**
    *   **Descrição**: Retorna o conteúdo completo do arquivo de histórico de chat (`chat_outputs/historico.txt`).
    *   **Parâmetros**: Nenhum.
    *   **Respostas**:
        *   `200 OK`: `{"history": "Conteúdo do histórico de chat"}`. Retorna `{"history": ""}` se o arquivo não existir.
    *   **Dependências**: Leitura de `chat_outputs/historico.txt`.

8.  **`GET /get_chat_data`**
    *   **Descrição**: Retorna uma lista de todos os arquivos de dados estruturados (CSV e JSON) salvos pelo chatbot (`chat_outputs/dados/`), incluindo seus conteúdos.
    *   **Parâmetros**: Nenhum.
    *   **Respostas**:
        *   `200 OK`: `{"data": [{"filename": "dados_timestamp.csv", "type": "csv", "content": [...]}, {"filename": "dados_timestamp.json", "type": "json", "content": {...}}]}`. Retorna `{"data": []}` se o diretório não existir.
    *   **Dependências**: Listagem e leitura de arquivos em `chat_outputs/dados/` usando `os`, `pandas` e `json`.

---

## 4. Documentação dos Componentes Principais

Esta seção foca nos principais subsistemas do projeto, detalhando sua lógica e como eles interagem.

### 4.1. Sistema RAG (Retrieval Augmented Generation)

O sistema RAG é o cérebro por trás da capacidade do chatbot de responder perguntas complexas sobre os dados de Pokémon. Ele combina a capacidade de recuperar informações relevantes de uma base de conhecimento (neste caso, dados de Pokémon) com a capacidade de um Large Language Model (LLM) de gerar respostas coerentes e contextuais.

**Componentes Principais do RAG:**

1.  **Modelo de Embedding (`src/rag/rag_data_loader.py:get_embedding_model`)**:
    *   **Função**: Converte texto (como os documentos de Pokémon ou as perguntas do usuário) em vetores numéricos (embeddings). Vetores semanticamente semelhantes ficam próximos no espaço vetorial.
    *   **Implementação**: Utiliza o modelo `all-MiniLM-L6-v2` da Hugging Face.
    *   **Quando é chamado**: Durante a criação e carregamento do `VectorStore`.

2.  **Geração de Documentos (`src/rag/rag_data_loader.py:gerar_documentos_para_rag`)**:
    *   **Função**: Transforma os dados estruturados do CSV (`data/relatorio.csv`) em um formato que o sistema RAG pode entender e indexar. Cada linha do CSV se torna um `Document` da LangChain.
    *   **Lógica**: Formata as informações de cada Pokémon (Nome, Tipos, Experiência, Stats) em uma única string de texto para cada documento.
    *   **Quando é chamado**: Durante a execução do pipeline ETL (`src/etl/pipeline.py`) e durante a inicialização do RAG se o índice não existir (`src/rag_builder.py`).

3.  **Vector Store (FAISS) (`src/rag/rag_data_loader.py:indexar_dados` e `carregar_vetorstore`)**:
    *   **Função**: Armazena os embeddings dos documentos de Pokémon. É otimizado para buscas de similaridade, permitindo encontrar rapidamente os documentos mais relevantes para uma dada consulta.
    *   **Implementação**: Usa a biblioteca FAISS (Facebook AI Similarity Search) para criar e gerenciar o índice de vetores. O índice é salvo e carregado do diretório `data/indice_faiss`.
    *   **Quando é chamado**:
        *   `indexar_dados()`: Após a geração de documentos, cria o índice FAISS (chamado pelo pipeline ETL).
        *   `carregar_vetorstore()`: Tenta carregar um índice existente na inicialização do chatbot (chamado por `src/rag_builder.py`).

4.  **LLM (Large Language Model) (`src/rag/rag_core.py:get_llm`)**:
    *   **Função**: É o modelo de linguagem que gera as respostas textuais.
    *   **Implementação**: Prioriza `ChatGroq` (modelo `llama3-8b-8192`) se `GROQ_API_KEY` estiver disponível, caso contrário, usa `ChatOpenAI` (modelo `gpt-3.5-turbo`) com `OPENAI_API_KEY`.
    *   **Quando é chamado**: Pelo `src/rag/rag_core.py:responder_pergunta_rag` para obter a instância do modelo.

5.  **Histórico de Chat e Contexto (`src/rag/chat_history.py`)**:
    *   **Função**: Mantém a "memória" do chatbot, persistindo as conversas anteriores e os dados estruturados extraídos. Isso permite que o LLM tenha um contexto mais amplo nas interações subsequentes.
    *   **Lógica**: Salva perguntas e respostas em `chat_outputs/historico.txt`. Carrega também os arquivos CSV e JSON do diretório `chat_outputs/dados` para incluir no contexto do prompt do LLM.
    *   **Funções Principais**: `salvar_historico()`, `carregar_contexto_anterior()`, `limpar_contexto()`.
    *   **Quando é chamado**:
        *   `salvar_historico()`: Após cada resposta do LLM em `src/rag/rag_core.py`.
        *   `carregar_contexto_anterior()`: Antes de cada geração de resposta pelo LLM em `src/rag/rag_core.py`.
        *   `limpar_contexto()`: Acionado pelo comando `/limpar` no CLI ou pelo endpoint `/clear_context` da API.

6.  **Grafo RAG (LangGraph) (`src/rag/rag_core.py:construir_grafo_rag`)**:
    *   **Função**: Orquestra o fluxo de recuperação de informações e geração de respostas. Define os passos lógicos que a pergunta do usuário percorre.
    *   **Lógica**:
        1.  **Input Node**: Recebe a pergunta do usuário.
        2.  **Retriever Node (`recuperar_docs`)**: Usa o `retriever` (configurado com o `VectorStore`) para buscar documentos relevantes no índice FAISS com base na pergunta.
        3.  **Generator Node (`gerar_resposta`)**:
            *   Pega o conteúdo dos documentos recuperados.
            *   Adiciona o `contexto_anterior` (histórico de chat e dados estruturados).
            *   Monta um prompt detalhado para o LLM.
            *   Invoca o LLM para gerar a resposta final.
    *   **Quando é chamado**: Toda vez que uma pergunta é feita ao chatbot (`src/rag/rag_core.py:responder_pergunta_rag`).

**Fluxo Completo do RAG (Exemplo de uma pergunta):**

1.  Usuário envia uma `pergunta` (via CLI ou API).
2.  `src.rag_builder.inicializar_rag()` garante que o `VectorStore` (FAISS) esteja carregado.
3.  `src.rag.rag_core.responder_pergunta_rag()` é chamado com a `pergunta` e o `vetorstore`.
4.  Dentro de `responder_pergunta_rag`:
    *   Um `retriever` é criado a partir do `vetorstore`.
    *   O `grafo` LangGraph é construído.
    *   O `grafo.invoke()` é chamado com a `pergunta`.
    *   O `retriever` busca documentos relevantes do `VectorStore`.
    *   A função `gerar_resposta` no grafo chama `src.rag.chat_history.carregar_contexto_anterior()` para obter o histórico e dados salvos.
    *   Um prompt é criado combinando a pergunta, os documentos recuperados e o contexto anterior.
    *   O LLM (`get_llm()`) gera uma `resposta`.
5.  De volta a `responder_pergunta_rag`, a `resposta` é exibida, salva via `src.rag.chat_history.salvar_historico()`.
6.  `src.rag.rag_core.tentar_extrair_dados()` tenta encontrar tabelas/JSON na resposta e, se encontrar, `src.rag.rag_core.salvar_dados_estruturados()` as persiste em `chat_outputs/dados`.

### 4.2. Fluxo ETL (Extração, Transformação e Carga)

O pipeline ETL é responsável por coletar, processar e disponibilizar os dados de Pokémon. Ele é um processo sequencial e robusto.

**Estágios do ETL:**

1.  **Extração (`src/etl/extractor.py`)**:
    *   **Função**: Obter os dados brutos de Pokémon.
    *   **Lógica**:
        *   Verifica primeiro o cache local (`data/pokemon_cache.json`) usando `src.utils.cache.carregar_cache_json()`. Se disponível e válido, carrega de lá.
        *   Caso contrário, testa a conectividade com a PokeAPI (`testar_conexao_api()`).
        *   Se a API estiver inacessível e `USAR_DADOS_EXEMPLO` for `True`, gera dados de exemplo (`gerar_dados_exemplo()`).
        *   Se a API estiver disponível, utiliza `ThreadPoolExecutor` para buscar dados de múltiplos Pokémon em paralelo (`_buscar_pokemon_individual()`).
        *   Após a extração, se `USAR_CACHE` for `True`, os dados são salvos no cache via `src.utils.cache.salvar_cache_json()`.
    *   **Saída**: Uma lista de dicionários com os dados brutos dos Pokémon.

2.  **Transformação (`src/etl/transformer.py`)**:
    *   **Função**: Processar e estruturar os dados brutos, adicionando informações derivadas.
    *   **Lógica**:
        *   `transformar_dados_pokemon()`: Converte a lista de dicionários brutos em um `pandas.DataFrame`. Extrai e normaliza campos, calcula estatísticas e adiciona uma `Categoria` (Forte, Médio, Fraco) baseada na experiência base.
        *   Funções de Análise Auxiliares: `contar_pokemon_por_tipo()`, `calcular_media_stats_por_tipo()`, `encontrar_top_5_experiencia()` realizam análises sumárias no DataFrame transformado.
    *   **Saída**: Um `pandas.DataFrame` limpo e estruturado, além de resultados de análises intermediárias.

3.  **Carga e Relatório (`src/etl/reporter.py`)**:
    *   **Função**: Persistir os dados processados e gerar relatórios/visualizações.
    *   **Lógica**:
        *   `exportar_relatorio_csv()`: Salva o DataFrame transformado em `data/relatorio.csv`.
        *   `gerar_grafico_tipos()`: Cria e salva um gráfico de barras da contagem de Pokémon por tipo em `data/grafico_tipos.png`.
        *   `gerar_relatorio_consolidado()`: Cria um arquivo de texto resumindo as principais análises (`data/relatorio_consolidado.txt`).
        *   `gerar_resumo_relatorio()`: Calcula e loga um resumo das principais estatísticas.
        *   `gerar_grafico_automatico()`: Função flexível para gerar gráficos sob demanda a partir de dados (utilizada no CLI `/plot`).
    *   **Saída**: Arquivos CSV, PNG e TXT no diretório `data/` e `chat_outputs/`.

**Orquestração do ETL (`src/etl/pipeline.py:executar_pipeline`)**:

A função `executar_pipeline()` em `src/etl/pipeline.py` é a orquestradora central do fluxo ETL. Ela invoca as funções dos módulos `extractor`, `transformer` e `reporter` na ordem correta, garantindo que os dados sejam processados de ponta a ponta. Além disso, ela também chama `src.rag.rag_data_loader.gerar_documentos_para_rag()` e `src.rag.rag_data_loader.indexar_dados()` para garantir que os dados transformados sejam indexados e estejam disponíveis para o sistema RAG.

### 4.3. API RESTful (`api.py`)

A `api.py` utiliza o framework FastAPI para fornecer uma interface HTTP para as funcionalidades do projeto, permitindo que o sistema seja acessado programaticamente ou via um frontend web (como o `frontend/` presente no projeto).

**Inicialização da API:**

*   Quando o `api.py` é iniciado (e.g., `uvicorn.run(app, ...)`, que é chamado por `main.py serve_api`), o evento `@app.on_event("startup")` é acionado.
*   Neste evento, `src.rag_builder.inicializar_rag()` é chamado para garantir que o `VectorStore` do RAG esteja carregado e pronto para ser usado pelos endpoints do chat.

**Endpoints Chave:**

| Método | Endpoint                | Descrição                                                                               | Entrada (Body JSON) | Saída (JSON) / Tipo de Arquivo       | Funções Internas Acionadas                                        |
| :----- | :---------------------- | :-------------------------------------------------------------------------------------- | :------------------ | :----------------------------------- | :---------------------------------------------------------------- |
| `GET`  | `/status`               | Verifica se a API está operacional.                                                     | N/A                 | `{"status": "API está online!"}` | N/A                                                               |
| `POST` | `/run_pipeline`         | Inicia a execução do pipeline completo de ETL.                                          | N/A                 | `{"message": "Pipeline de ETL executado com sucesso!"}` | `src.etl.pipeline.executar_pipeline()`                            |
| `POST` | `/chat`                 | Envia uma pergunta ao chatbot RAG e recebe uma resposta.                                | `{"pergunta": "texto"}` | `{"pergunta": "...", "resposta": "..."}` | `src.rag.rag_core.responder_pergunta_rag()`                       |
| `POST` | `/clear_context`        | Limpa o histórico de chat e os dados estruturados do chatbot.                           | N/A                 | `{"message": "Contexto do chatbot limpo com sucesso!"}` | `src.rag.chat_history.limpar_contexto(confirmar=False)`           |
| `GET`  | `/get_pipeline_report`  | Obtém o relatório ETL principal em formato CSV (retorna como JSON array de objetos).    | N/A                 | `[{"ID": 1, "Nome": "Bulbasaur", ...}]`  | Leitura de `data/relatorio.csv`                                   |
| `GET`  | `/get_pipeline_chart`   | Obtém o gráfico de tipos de Pokémon gerado pelo pipeline.                               | N/A                 | Imagem PNG                           | Retorna `data/grafico_tipos.png` como `FileResponse`              |
| `GET`  | `/get_chat_history`     | Obtém o histórico textual completo das interações do chat.                              | N/A                 | `{"history": "texto do histórico"}`     | Leitura de `chat_outputs/historico.txt`                           |
| `GET`  | `/get_chat_data`        | Obtém os dados estruturados (CSV/JSON) salvos pelo chatbot durante as interações.       | N/A                 | `{"data": [{"filename": "...", "type": "...", "content": "..."}]}` | Leitura de arquivos em `chat_outputs/dados/`                      |

---

## 5. Sugestões de Melhoria

Com base na análise aprofundada do código, as seguintes sugestões de melhoria são propostas para aumentar a escalabilidade, manutenibilidade e robustez do projeto:

### 5.1. Módulos ETL

*   **Refatoração da Lógica de Plotagem em `src/etl/reporter.py`:**
    *   **Problema**: A função `_processar_especificacao_plot` em `reporter.py` tenta inferir a intenção do gráfico a partir de strings literais (`"diferenca do hp"`, `"apenas hp"`). Isso é propenso a erros e difícil de estender. A assunção de uma coluna `HP_anterior` para cálculo de diferença de HP não é claramente definida ou gerada no fluxo ETL atual, o que pode causar falhas silenciosas ou gráficos incorretos.
    *   **Sugestão**: Refatorar para um mapeamento mais explícito de `comando -> função_de_plotagem`. Em vez de strings literais, considere usar um dicionário ou enum para mapear comandos a funções específicas de plotagem. Para `diferenca do hp`, garantir que a coluna `HP_anterior` seja consistentemente gerada na fase de transformação ou remover a funcionalidade se não for relevante.

*   **Consistência e Centralização de Caminhos de Arquivo:**
    *   **Problema**: Alguns caminhos de arquivo estão hardcoded em `api.py` (ex: `data/relatorio.csv`, `data/grafico_tipos.png`, `chat_outputs/historico.txt`). Embora `src/config/settings.py` já centralize muitos caminhos, há inconsistência.
    *   **Sugestão**: Mover todos os caminhos de arquivo fixos para `src/config/settings.py` e referenciá-los a partir de lá. Isso tornará a configuração mais flexível e a manutenção mais fácil.

*   **Modularidade e Parametrização do Pipeline ETL (`src/etl/pipeline.py`):**
    *   **Problema**: A função `executar_pipeline()` é monolítica, executando todas as fases. Para testes ou casos de uso específicos (ex: rodar apenas extração e transformação), não há granularidade.
    *   **Sugestão**: Parametrizar a função `executar_pipeline` para aceitar argumentos que permitam a execução de subconjuntos do pipeline (ex: `executar_pipeline(run_extraction=True, run_transformation=True, generate_reports=False)`). Isso melhora a flexibilidade e testabilidade.

### 5.2. Módulos RAG (Retrieval Augmented Generation)

*   **Gerenciamento de Tamanho do Contexto de Chat (`src/rag/chat_history.py`):**
    *   **Problema**: O `carregar_contexto_anterior()` injeta todo o histórico e conteúdo de arquivos de dados no prompt do LLM. Isso pode rapidamente exceder os limites de tokens do LLM para conversas longas ou com muitos dados, levando a erros ou respostas truncadas.
    *   **Sugestão**: Implementar uma estratégia de sumarização ou janela deslizante para o contexto. Por exemplo, resumir conversas antigas usando um LLM menor ou manter apenas as `N` últimas interações relevantes. Para dados estruturados, talvez enviar apenas metadados ou um resumo conciso, a menos que explicitamente solicitado.

*   **Robustez na Extração de Dados Estruturados (`src/rag/rag_core.py`):**
    *   **Problema**: A função `tentar_extrair_dados()` depende fortemente de padrões de texto exatos (regex) para tabelas Markdown e JSON. Variações mínimas na saída do LLM podem quebrar a extração.
    *   **Sugestão**: Explorar bibliotecas mais robustas para parsing de Markdown ou JSON que sejam mais tolerantes a pequenas variações. Considerar adicionar uma camada de validação de esquema aos dados extraídos antes de salvá-los.

*   **Tratamento de Erros e Logs Mais Granulares no Grafo (`src/rag/rag_core.py`):**
    *   **Problema**: Falhas dentro dos nós do `LangGraph` podem ser difíceis de depurar. A saída atual de erros pode ser genérica.
    *   **Sugestão**: Adicionar callbacks ou loggers específicos aos nós do LangGraph para capturar e registrar o estado e quaisquer exceções de forma mais detalhada, facilitando a depuração. Implementar estratégias de fallback dentro do grafo para lidar com falhas de um nó (ex: se a recuperação de documentos falhar, o gerador pode tentar responder com um prompt mais genérico).

*   **Controle de Versão do Índice FAISS (`src/rag/rag_data_loader.py`):**
    *   **Problema**: Se `data/relatorio.csv` for atualizado, o índice FAISS precisa ser recriado manualmente ou a cada inicialização se não encontrado. Não há um mecanismo para detectar automaticamente se o CSV mudou e forçar a reindexação.
    *   **Sugestão**: Adicionar um mecanismo de validação (ex: comparar um hash do CSV ou seu timestamp de modificação com um hash/timestamp salvo do índice) para acionar a reindexação somente quando os dados de origem realmente mudarem. Isso economizaria tempo de processamento.

### 5.3. Módulos de Utilitários

*   **Validação de Schema do Cache (`src/utils/cache.py`):**
    *   **Problema**: O `carregar_cache_json` apenas verifica a validade sintática do JSON. Um JSON válido, mas com estrutura de dados inesperada, pode causar erros downstream.
    *   **Sugestão**: Adicionar validação da estrutura dos dados carregados do cache. Por exemplo, usar `Pydantic` ou validação manual para garantir que o cache contém o tipo e o formato de dados esperado antes de retorná-lo.

*   **Rotatividade de Logs (`src/utils/logger.py`):**
    *   **Problema**: O `FileHandler` atual do logger não tem rotatividade, fazendo com que o arquivo de log (`pipeline.log`) cresça indefinidamente, o que pode consumir espaço em disco e dificultar a análise.
    *   **Sugestão**: Substituir `logging.FileHandler` por `logging.handlers.RotatingFileHandler` ou `TimedRotatingFileHandler` para gerenciar o tamanho dos arquivos de log, criando novos arquivos periodicamente ou após um tamanho limite.

*   **Configuração de Logs Dinâmica (`src/utils/logger.py`):**
    *   **Problema**: O nível de log (`INFO`) e o formato são fixos.
    *   **Sugestão**: Permitir que o nível de log e outros parâmetros de configuração de log sejam definidos via variáveis de ambiente ou por `src/config/settings.py`, facilitando a adaptação do log para diferentes ambientes (desenvolvimento, produção, depuração).

### 5.4. Módulos de Configuração

*   **Variáveis de Ambiente para Configurações Chave (`src/config/settings.py`):**
    *   **Problema**: Embora as chaves de API já usem `.env`, outras configurações como `QUANTIDADE_POKEMON`, `TIMEOUT_REQUEST` ou `CAMINHO_LOG` são constantes no código.
    *   **Sugestão**: Tornar essas configurações também passíveis de sobrescrição por variáveis de ambiente (lidas com `os.getenv`). Isso oferece maior flexibilidade para o deploy em diferentes ambientes sem modificar o código-fonte.

## 6. Exemplos de Código

Devido à extensão e complexidade dos módulos, exemplos de código relevantes já foram inseridos nas seções "2. Fluxo de Execução Detalhado" e "3. Detalhamento de Cada Módulo" para ilustrar as chamadas e a interconexão das funções. Por exemplo, trechos do `main.py` e das funções `responder_pergunta_rag` e `carregar_contexto_anterior` foram fornecidos. Para exemplos mais aprofundados, a leitura direta dos arquivos mencionados é recomendada.

