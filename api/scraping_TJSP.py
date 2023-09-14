from get_cellphone import webdriver, Service, Select, By
from urls import get_url_TJSP
import time
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def baixar_TJSP(cad_TJSP):
    prefs = {
        "download.default_directory": r"/app/data/pdf_diarios",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs", prefs)

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(executable_path='/usr/bin/chromedriver')

    navegador = webdriver.Chrome(service=service, options=chrome_options)
    navegador.get(get_url_TJSP())
    
    cadernos = navegador.find_element(By.ID, 'cadernosCad')
    navegador.execute_script("arguments[0].removeAttribute('disabled');", cadernos)

    download_button = navegador.find_element(By.ID, 'download')
    navegador.execute_script("arguments[0].removeAttribute('disabled');", download_button)

    caderno_selecionado = Select(cadernos)
    
    diretorio = '/app/data/pdf_diarios/'
    
    if cad_TJSP == 'TJSPC':
        cad_index = 2
    if cad_TJSP == 'TJSPI1':
        cad_index = 3
    if cad_TJSP == 'TJSPI2':
        cad_index = 4
    if cad_TJSP == 'TJSPI3':
        cad_index = 5
    
    caderno_selecionado.select_by_index(cad_index)
    download_button.click()
    # while True:
    #     if any(filename.endswith(".crdownload") for filename in os.listdir(diretorio)):
    #         time.sleep(1)
    #     else:
    #         break
    #     logger.info('Aguarndando download TJSPC')
    #     time.sleep(5)
    # logger.info("Arquivos no diretório: %s", os.listdir(diretorio))
    # time.sleep(10)
    # rename_cads_TJSP('TJSPC')

    time.sleep(120)
    rename_cads_TJSP(cad_TJSP)
    navegador.close()
    
def rename_cads_TJSP(cad_TJSP):
    pdf_file = f'/app/data/pdf_diarios/downloadCaderno.do'
    pdf_renamed = f'/app/data/pdf_diarios/diario_{cad_TJSP}_temp.pdf'
    os.rename(pdf_file, pdf_renamed)

def rename_cads_temps(cad_TJSP):
    pdf_file = f'/app/data/pdf_diarios/diario_{cad_TJSP}_temp.pdf'
    pdf_renamed = f'/app/data/pdf_diarios/diario_{cad_TJSP}.pdf'
    os.rename(pdf_file, pdf_renamed)