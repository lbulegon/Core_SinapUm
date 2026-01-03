FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Definir PYTHONPATH para garantir imports absolutos
ENV PYTHONPATH=/app

# Expor porta
EXPOSE 7020

# Comando padrão
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7020"]

