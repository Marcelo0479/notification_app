import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
import time
import requests
import pandas as pd
import re
from twocaptcha import TwoCaptcha

api_key_twoCaptcha = os.environ.get('api_key_twoCaptcha')

def get_cells(df):
    df.drop_duplicates(subset='Nome', inplace=True, ignore_index=True)
    df['OAB'] = df['OAB'].astype(str)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path='/usr/bin/chromedriver')

    # chrome_options.binary_location = '/usr/bin/google-chrome'  # Insira o caminho correto para o executável do Chrome

    navegador = webdriver.Chrome(service=service, options=chrome_options)
    navegador.get('https://cna.oab.org.br/')
    

    for i in range(len(df)):
        time.sleep(6)
        
        n_oab = df['OAB'][i]
        uf = df['UF'][i]
        
        campo_oab = navegador.find_element(By.ID, 'txtInsc')
        campo_oab.clear()
        campo_oab.send_keys(n_oab)
        
        select_uf = navegador.find_element(By.ID, 'cmbSeccional')
        select = Select(select_uf)
        select.select_by_value(f'{uf.upper()}')
        
        select_ins = navegador.find_element(By.ID, 'cmbTipoInsc')
        select = Select(select_ins)
        select.select_by_value('1')
        
        solver = TwoCaptcha(api_key_twoCaptcha)

        element = navegador.find_element(By.CLASS_NAME, 'g-recaptcha')
        sitekey = element.get_attribute('data-sitekey')
        
        #Tratamento erro 2captcha
        try:
            result = solver.recaptcha(
                    sitekey=sitekey,
                    url='https://cna.oab.org.br/',
                    invisible=1)
            solved_code = result['code']
        except:
            time.sleep(3)
            result = solver.recaptcha(
                    sitekey=sitekey,
                    url='https://cna.oab.org.br/',
                    invisible=1)
            solved_code = result['code']

        script = f'document.getElementById("g-recaptcha-response").innerHTML = "{solved_code}";'
        navegador.execute_script(script)

        navegador.execute_script('captchaCallback();')
        
        time.sleep(2)
        
        if not navegador.find_element(By.ID, 'textResult').text:
            time.sleep(3)
            
            navegador.find_element(By.CLASS_NAME, 'row').click()
            
            time.sleep(3)

            image = navegador.find_element(By.ID, 'imgDetail').get_attribute('src')
            response = requests.get(image)
            nome_arquivo = 'imagem.jpg'
            with open(nome_arquivo, 'wb') as arquivo:
                arquivo.write(response.content)

            imagem = cv2.imread('imagem.jpg')
            texto = pytesseract.image_to_string(imagem, lang='por')

            texto = texto.splitlines()
            telefone = []
            for l in texto:
                if l.startswith('('):
                    telefone.append(l)

            df['telefone'][i] = telefone
            navegador.find_element(By.CLASS_NAME, 'close').click()

    navegador.quit()

    return df

def clean_data_cell(df):
    for i in df.index:
        aux_4 = []
        aux_1 = df['telefone'][i].split(',')
        if aux_1 != [' '] and aux_1 != ['[]']:
            for e in aux_1:
                aux_2 = ''
                aux_3 = re.findall(r'\d+', e)
                for n in aux_3:
                    aux_2 += n
            if len(aux_2) > 8:                    
                if aux_2[2] == '9' or aux_2[2] == '8':
                    aux_4.append(aux_2)
        if aux_4:
            if len(aux_4[0]) == 11:
                aux_4[0] = aux_4[0][:2] + aux_4[0][-8:]
                df['telefone'][i] = aux_4[0]
            else:
                df['telefone'][i] = aux_4[0]
        else:
            df['telefone'][i] = 'Não encontrado'
