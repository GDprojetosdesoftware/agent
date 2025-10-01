# 1. Use uma imagem base oficial do Python.
FROM python:3.10-slim

# 2. Defina o diretório de trabalho dentro do contêiner.
WORKDIR /app

# NOVO PASSO: Instalar o 'curl', uma ferramenta que usaremos para o Health Check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 3. Copie o arquivo de dependências primeiro.
COPY requirements.txt .

# 4. Instale as dependências.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie todo o seu código para o contêiner.
COPY . .

# 6. Exponha a porta padrão que o Streamlit usa.
EXPOSE 8501

# NOVO PASSO: Configuração do Health Check
# Esta seção diz ao Docker como verificar se a aplicação está saudável.
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 7. Defina o comando para iniciar a aplicação Streamlit.
CMD ["streamlit", "run", "stocks.py", "--server.port=8501", "--server.address=0.0.0.0"]