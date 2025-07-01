# Use uma imagem base Node.js
FROM node:20-alpine

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie package.json e package-lock.json para o diretório de trabalho
COPY package*.json ./

# Instale as dependências
RUN npm install

# Copie o restante do código da aplicação
COPY . .

# Exponha a porta que o Vite usa (padrão é 5173)
EXPOSE 5173

# Comando para iniciar a aplicação em modo de desenvolvimento
CMD ["npm", "run", "dev"] 