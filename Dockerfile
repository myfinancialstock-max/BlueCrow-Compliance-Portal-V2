FROM python:3.12-slim

WORKDIR /app

# Instalar dependências primeiro (camada cacheada — só reconstruída se requirements.txt mudar)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

EXPOSE 8000
