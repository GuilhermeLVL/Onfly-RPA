# Poke RPA Pipeline & AI Chat

Este projeto é uma solução completa para extração, transformação e análise de dados de Pokémon, combinada com uma interface de chat interativa baseada em IA para consultar os dados em linguagem natural.

O sistema utiliza um pipeline de ETL para buscar dados da PokeAPI, processá-los e gerar relatórios. Em seguida, indexa essas informações para que um modelo de linguagem (LLM) possa responder a perguntas complexas, funcionando como um assistente de análise de dados.

---

## ✨ Funcionalidades Principais

- **Pipeline de ETL Automatizado**: Extrai, transforma e carrega dados de Pokémon de forma eficiente.
- **Geração de Relatórios**: Cria automaticamente relatórios em formato CSV e visualizações gráficas.
- **Cache Inteligente**: Armazena dados já buscados para acelerar execuções futuras.
- **Chat Interativo com IA (RAG)**: Converse com seus dados! Faça perguntas como "quantos pokémon do tipo fogo existem?" ou "liste os 5 pokémon com maior ataque".
- **Suporte a Múltiplos LLMs**: Compatível com Groq (Llama 3) e OpenAI (GPT), com fallback automático.
- **Containerização com Docker**: Ambiente de execução padronizado, leve e fácil de implantar.

---

## 🚀 Tecnologias Utilizadas

- **Backend**: Python 3.12
- **Bibliotecas Principais**:
  - `pandas`: Manipulação e análise de dados.
  - `requests`: Requisições HTTP para a PokeAPI.
  - `matplotlib` & `seaborn`: Geração de gráficos.
  - `langchain` & `langgraph`: Orquestração do pipeline de IA (RAG).
  - `faiss-cpu`: Armazenamento e busca de vetores para o RAG.
  - `python-dotenv`: Gerenciamento de variáveis de ambiente.
- **Containerização**: Docker

---

## 📋 Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

- [Python 3.12+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [Git](https://git-scm.com/downloads)

---

## ⚙️ Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd poke_rpa_pipeline
    ```

2.  **Crie o arquivo de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto. Ele será usado para armazenar suas chaves de API.

3.  **Adicione as chaves de API ao arquivo `.env`:**
    Você precisa de pelo menos uma das chaves abaixo. O sistema priorizará a chave do Groq se ambas estiverem presentes.

    https://console.groq.com/keys
    https://platform.openai.com/account/api-keys

    ```env
    # Chave da API do Groq (recomendado, mais rápido e gratuito)
    GROQ_API_KEY="sua_chave_aqui"

    # Ou a chave da API da OpenAI
    OPENAI_API_KEY="sua_chave_aqui"
    ```

---

## ⚡ Como Executar

Existem duas maneiras de executar o projeto: via Docker (recomendado) ou localmente.

### 🐳 Via Docker (Recomendado)

Esta é a forma mais simples e segura de executar a aplicação, pois todo o ambiente já está configurado dentro do contêiner, utilizando o `docker-compose` para orquestração.

1.  **Garanta que o `.env` esteja na raiz do projeto:**
    Certifique-se de que o arquivo `.env` com suas chaves de API (conforme a seção "Configuração") esteja na raiz do diretório do projeto.

2.  **Construa e inicie os serviços com Docker Compose:**
    No terminal, na raiz do projeto, execute o comando para construir a imagem e iniciar o contêiner:
    ```bash
    docker compose up --build -d
    ```
    Este comando:
    - `up`: Inicia os serviços definidos no `docker-compose.yml`.
    - `--build`: Constrói a imagem se ela ainda não existir ou se houver alterações no `Dockerfile`.
    - `-d`: Executa o contêiner em segundo plano (detached mode).

3.  **Execute o Pipeline de ETL (dentro do contêiner):
**Uma vez que o contêiner esteja rodando, você pode executar o pipeline de ETL ou interagir com o chat. Os dados, logs e gráficos gerados serão salvos diretamente nas pastas `data`, `logs` e `chat_outputs` no seu computador, devido aos volumes configurados no `docker-compose.yml`.
    ```bash
    docker compose exec poke-rpa-pipeline python main.py pipeline
    ```

4.  **Inicie o Chat Interativo (dentro do contêiner):
**Para iniciar o chat, use:
    ```bash
    docker compose exec -it poke-rpa-pipeline python main.py chat
    ```
    Para sair do chat, digite `exit` ou `quit`.

5.  **Parar e remover os serviços (opcional):
**Quando terminar de usar, você pode parar e remover os contêineres, redes e volumes criados pelo `docker-compose` (exceto os volumes persistentes `data`, `logs` e `chat_outputs` que você criou manualmente para a persistência):
    ```bash
    docker compose down
    ```

6.  **Inicie o Frontend (Chat Interativo via Web) via Docker:**
    Se você configurou o serviço de frontend no `docker-compose.yml`, o frontend será iniciado automaticamente junto com o backend quando você executar `docker compose up --build -d`. Você pode então acessar o chat interativo no seu navegador através do endereço `http://localhost:5173`.

### 🐍 Localmente (Sem Docker)

1.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux / macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o Pipeline de ETL:**
    ```bash
    python main.py pipeline
    ```

4.  **Inicie o Chat Interativo:**
    ```bash
    python main.py chat
    ```

5.  **Inicie o Frontend (Chat Interativo via Web):**
    Para interagir com o chat através da interface web, navegue até o diretório `frontend`, instale as dependências e inicie o servidor de desenvolvimento:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    Após executar o comando `npm run dev`, o frontend estará acessível no seu navegador, geralmente em `http://localhost:5173` (ou uma porta similar, indicada no terminal).

---

## 📂 Estrutura do Projeto

```
.
├── api.py             # API RESTful para interação com o ETL e RAG.
├── chat_outputs/      # Saídas geradas pelo chat (histórico, dados, gráficos).
│   ├── dados/         # Dados extraídos e transformados (e.g., CSV).
│   └── historico.txt  # Histórico das interações do chat.
├── data/              # Dados brutos, processados e índices do FAISS.
│   └── indice_faiss/  # Índice FAISS para o sistema RAG.
│       ├── index.faiss
│       └── index.pkl
├── docs/              # Documentação do projeto.
│   └── fluxo_de_execucao_modulos.md
├── Dockerfile         # Definições para a imagem Docker da aplicação.
├── docker-compose.yml # Definições para orquestração de serviços Docker.
├── erro.txt           # Arquivo para logs de erros.
├── frontend/          # Aplicação frontend (React/TypeScript).
│   ├── public/        # Ativos públicos (e.g., vite.svg).
│   ├── src/           # Código-fonte do frontend.
│   │   ├── assets/    # Ativos como imagens.
│   │   ├── App.css
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── README.md
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── logs/              # Arquivos de log da aplicação Python.
├── main.py            # Ponto de entrada da aplicação (CLI).
├── planejamento.txt   # Arquivo de planejamento ou notas.
├── README.md          # Documentação principal do projeto.
├── requirements.txt   # Dependências Python do projeto.
└── src/               # Código-fonte principal da aplicação Python.
    ├── config/        # Configurações globais.
    │   └── settings.py
    ├── etl/           # Módulos para Extração, Transformação e Carga de dados.
    │   ├── extractor.py
    │   ├── pipeline.py
    │   ├── reporter.py
    │   └── transformer.py
    ├── rag/           # Módulos do sistema RAG (Retrieval Augmented Generation).
    │   ├── chat_history.py
    │   ├── rag_core.py
    │   └── rag_data_loader.py
    ├── utils/         # Utilitários diversos.
    │   ├── cache.py
    │   └── logger.py
    ├── rag.py         # Lógica principal do RAG (pode ser refatorado em rag_core.py).
    └── rag_builder.py # Construtor/inicializador do sistema RAG.
```


### Fluxo de Execução dos Módulos
![Fluxo de Execução dos Módulos](docs/Editor _ Mermaid Chart-2025-07-01-023651.png)

https://www.mermaidchart.com/app/projects/c34e6cdc-58d1-4fb7-9a9d-907fdbc382e7/diagrams/f1a30f46-5e6b-4afd-9918-2663ff8f3bec/version/v0.1/edit