# Utiliza a versão "bookworm" (Debian 12), que é a mais recente e segura
FROM python:3.12-slim-bookworm

WORKDIR /app

# Atualiza todos os pacotes críticos do SO e limpa o cache para não pesar a imagem
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Atualiza o pip por segurança e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Principal.py", "--server.port=8501", "--server.address=0.0.0.0"]