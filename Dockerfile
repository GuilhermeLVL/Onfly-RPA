# Estágio 1: Build
# Use uma imagem base oficial do Python
FROM python:3.12-slim as builder

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema, se houver
# Exemplo: RUN apt-get update && apt-get install -y gcc

# Instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Estágio 2: Final
# Use uma imagem base leve
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Cria diretórios necessários para a aplicação
RUN mkdir -p /app/data/indice_faiss /app/logs /app/chat_outputs/dados /app/chat_outputs/graficos

# Copia as dependências instaladas do estágio de build
COPY --from=builder /root/.local /root/.local

# Adiciona o diretório de binários do usuário ao PATH
ENV PATH=/root/.local/bin:$PATH

# Copia o código da aplicação
COPY src/ ./src/
COPY main.py .

# Define o ponto de entrada para a aplicação
ENTRYPOINT ["python", "main.py"]

# O comando padrão pode ser "chat" ou "pipeline"
CMD ["chat"]
