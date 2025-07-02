# Estágio de build
FROM python:3.12-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN pip install --upgrade pip

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# Estágio final
FROM python:3.12-slim

WORKDIR /app

# Copiar dependências pré-compiladas do estágio de build
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copiar o restante da aplicação
COPY . .

# Definir o comando padrão para executar a API
CMD ["python", "main.py", "serve_api"]
