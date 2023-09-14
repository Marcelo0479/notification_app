from get_cellphone import Options, Service, webdriver, time, By

def get_url_TJDF():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path='/usr/bin/chromedriver')

    navegador = webdriver.Chrome(service=service, options=chrome_options)
    navegador.get('https://pesquisadje.tjdft.jus.br/')
    time.sleep(5)
    elemento = navegador.find_element(By.CSS_SELECTOR, 'a.jss68.jss282.jss285.jss286.jss290.jss291')
    url = elemento.get_attribute('href')
    navegador.close()
    return url

def get_url_TRT18():
    url = 'https://diario.jt.jus.br/cadernos/Diario_J_18.pdf'
    return url

def get_url_TJSP():
    url = 'https://dje.tjsp.jus.br/cdje/index.do;jsessionid=904E03097EDCF133765EE6CB860DFD6B.cdje2'
    return url