# 1. Use uma imagem base oficial do Python.
FROM python:3.10-slim

# 2. Defina o diretório de trabalho dentro do contêiner.
WORKDIR /app

# 3. Copie o arquivo de dependências primeiro para otimizar o build.
COPY requirements.txt .

# 4. Instale as dependências.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie todo o seu código (arquivos .py, pastas, etc.) para o contêiner.
COPY . .

# 6. Exponha a porta padrão que o Streamlit usa.
EXPOSE 8501

# 7. Defina o comando para iniciar a aplicação Streamlit.
CMD ["streamlit", "run", "stocks.py", "--server.port=8501", "--server.address=0.0.0.0"]