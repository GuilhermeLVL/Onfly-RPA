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