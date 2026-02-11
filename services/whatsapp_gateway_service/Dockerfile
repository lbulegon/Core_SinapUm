FROM node:20-alpine

WORKDIR /app

# Instala git (necessário para algumas dependências npm)
RUN apk add --no-cache git

# Copia arquivos de dependências
COPY package.json ./

# Instala dependências
RUN npm install --only=production

# Copia código fonte
COPY src/ ./src/

# Cria diretório de autenticação
RUN mkdir -p /data/auth

# Expõe porta
EXPOSE 8007

# Comando de inicialização
CMD ["node", "src/index.js"]
