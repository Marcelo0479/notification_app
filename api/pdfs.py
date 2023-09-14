import requests
import hashlib
import os

def obter_hash_do_pdf(url):
    resposta = requests.get(url)
    conteudo_pdf = resposta.content
    return hashlib.md5(conteudo_pdf).hexdigest()

def obter_hash_do_arquivo_local(nome_arquivo):
    caminho = os.path.join('/app/data/pdf_diarios', nome_arquivo)
    print(caminho)
    if not os.path.exists(caminho):
        return None
    with open(caminho, 'rb') as f:
        conteudo = f.read()
    return hashlib.md5(conteudo).hexdigest()

def baixar_pdf(url, nome_arquivo, tribunal):
    resposta = requests.get(url)
    caminho = os.path.join('/app/data/pdf_diarios', nome_arquivo)  # ajuste aqui
    with open(caminho, 'wb') as f:
        f.write(resposta.content)
    print(f"PDF de {tribunal} salvo.")
