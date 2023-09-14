# Define a imagem base
FROM python:3.9

# Instale as dependências do Chrome e do ChromeDriver
RUN apt-get update && apt-get install -y wget gnupg unzip

# Adicione o repositório do Chrome e instale o Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb

# Instala o Chrome a partir do pacote .deb que foi baixado
RUN apt-get install -y ./google-chrome-stable_114.0.5735.90-1_amd64.deb

# Faça o download do ChromeDriver e coloque-o no diretório /usr/local/bin
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip

RUN unzip /tmp/chromedriver.zip -d /usr/bin/

# Defina as permissões corretas para o ChromeDriver
RUN chmod +x /usr/bin/chromedriver

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos necessários para o contêiner
COPY . /app

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Instala as dependências do Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr

# Instala os pacotes de idioma do Tesseract OCR (exemplo para inglês)
RUN apt-get install -y tesseract-ocr-por

RUN apt update

RUN apt install -y libgl1-mesa-glx

RUN which google-chrome

# Comando padrão a ser executado quando o contêiner for iniciado
CMD ["python", "app.py"]

