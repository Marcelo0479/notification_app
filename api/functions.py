import requests
import PyPDF2
import re
import logging
from pathlib import Path


# def baixar_diario(url, tribunal):
#     """
#     Baixar o diário a partir da URL e salva-lo no diretório pdf_diarios.
#     """
#     assert url, "A URL não pode estar vazia."
#     assert tribunal, "O nome do tribunal não pode estar vazio."
#     filename = Path(f'pdf_diarios/diario_{tribunal}.pdf')
#     response = requests.get(url, verify=False)
#     filename.write_bytes(response.content)


def pdf_string(nome_arquivo):
    """
    Lê o conteúdo do PDF e retorna como string.
    """
    assert nome_arquivo, "O nome do tribunal não pode estar vazia."
    pdf_file = f'/app/data/pdf_diarios/{nome_arquivo}'
    try:
        with open(pdf_file, 'rb') as file:
            pdfReader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() for page in pdfReader.pages])
            return text
    except FileNotFoundError:
        logging.error(f"Arquivo {pdf_file} não encontrado.")
        return ""
    except Exception as e:
        logging.error(f"Erro ao abrir o arquivo: {str(e)}")
        return ""


#Criando Lista com os processos
def lista_processo(string, re_processo):
    """
    Dividindo a string do pdf em processos e retorna uma lista de processos.
    """
    assert string, "A string não pode estar vazia."
    assert re_processo, "A expressão regular não pode estar vazia."
    string = string.lower()
    processos = re.split(re_processo, string)
    processos2 = [processos[i] + processos[i+1] for i in range(0, len(processos)-1, 2)]
    return processos2


#Limpando string
def limpando_lista (list, tribunal):
    list2=[]
    for string in list:
        string=string.lower()
        if tribunal.startswith('TJSP'):
            string=string.replace("\n","")
        else:
            string=string.replace("\n"," ")
        list2.append(string)
    return list2

#Criando lista com palavras 1 palavra positiva
def separando_nomeacao (string,lista):
    texto_nomeacao= []
    for nomeacao in lista:
        if nomeacao.find(string) != -1:
            texto_nomeacao.append(nomeacao)
    return texto_nomeacao

#Criando lista com palavras lista positiva
def separando_positivo (keywords_positivas,lista):
    texto_nomeacao_positivas= []
    for nomeacao in lista:
        if any(i in nomeacao for i in keywords_positivas):          
            texto_nomeacao_positivas.append(nomeacao)
    return texto_nomeacao_positivas

#Subtraindo listas
def removendo_lista (listaMaior, ListaMenor):
     lista= [x for x in listaMaior if x not in ListaMenor]
     return lista


#Removendo palavras negativas
def removendo_negativo (keyword_negativas,lista):
    texto_nomeacao_positiva_sobra=[]
    for nomeacao in lista:
        if any(i in nomeacao for i in keyword_negativas):
            pass
        else:
            texto_nomeacao_positiva_sobra.append(nomeacao)
            
    return texto_nomeacao_positiva_sobra


#Separando Processos
def separando_n_processos (lista):
    #pegando processos
    processos_final=[]
    for texto in lista:
        temp=re.findall(r'(\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4})', texto)
        texto=texto.replace("nomeio","-----------------NOMEIO-----------------")
        try:
            processos_final.append([temp[0],texto])
        except:
            continue
    return processos_final

#Ler lista
def lendo_lista (lista,n):
    if len(lista) > 0:
        print(lista[n])
    else:
        print ("Vazio")

# Obtendo o nº do processo e a lista de advogados
def obtendo_dados_processo_e_advogados(lista_total, re_trib):
    """
    Obtém o número do processo e a lista de advogados para cada processo na lista total.
    """
    assert lista_total, "A lista de processos não pode estar vazia."
    assert re_trib, "A expressão regular não pode estar vazia."

    advogados = []
    for i in range(2):  # estamos interessados apenas nas duas primeiras listas
        for p in lista_total[i]:
            n_processo = p[0]
            texto_processo = p[1]
            advogados_proc = [list(adv) + [n_processo, texto_processo] 
                              for adv in re.findall(re_trib, p[1], re.IGNORECASE)]
            advogados += advogados_proc
            
    return advogados



def codigo_padrao(tribunal, re_processo, peritos_positivas, peritos_negativos, keyword_positivas, keyword_negativas):
    """
    Realiza todas as operações necessárias para a extração de dados do pdf.
    """
    n_processos = n_nomeacoes = n_peritos = 0
    
    assert tribunal, "O nome do tribunal não pode estar vazio."
    assert re_processo, "A expressão regular não pode estar vazia."

    # Ler o PDF
    nome_arquivo = f'diario_{tribunal}.pdf'
    
    # Lendo PDF
    pdf = pdf_string(nome_arquivo)

    if pdf:
        #Listando Processos
        processos = lista_processo (pdf,re_processo)
        print("Processos: "+ str(len(processos)))
        n_processos = len(processos)

        #Criando lista com palavras positiva "Nomeio"
        nomeacao = separando_nomeacao ("nomeio",processos)
        print("Nomeação: "+str(len(nomeacao)))
        n_nomeacoes = len(nomeacao)

        #Limpando string Ex. tirando quebra de linha
        nomeacao = limpando_lista(nomeacao, tribunal)

        #lista com peritos positivos
        nomeacao_primeira_lista = separando_positivo (peritos_positivas,nomeacao)
        nomeacao_primeira_lista = removendo_negativo (keyword_negativas,nomeacao_primeira_lista)
        lista_sobra = removendo_lista(nomeacao,nomeacao_primeira_lista)
        print("Peritos: "+str(len(nomeacao_primeira_lista)))
        n_peritos = len(nomeacao_primeira_lista)

        #Lista com Palavras Positivas
        nomeacao_segunda_lista = separando_positivo (keyword_positivas,lista_sobra)
        nomeacao_segunda_lista = removendo_negativo (keyword_negativas,nomeacao_segunda_lista)
        lista_sobra2 = removendo_lista(lista_sobra,nomeacao_segunda_lista)
        print("Palavras: "+str(len(nomeacao_segunda_lista)))

        #Lista Outros
        keyword_negativas2=keyword_negativas+peritos_negativos
        nomeacao_terceira_lista = removendo_negativo (keyword_negativas2,lista_sobra2)
        print("Outros: "+str(len(nomeacao_terceira_lista)))

        #Juntando as listas
        list1=separando_n_processos(nomeacao_primeira_lista)
        list2=separando_n_processos(nomeacao_segunda_lista)
        list3=separando_n_processos(nomeacao_terceira_lista)
        lista_total = []
        lista_total.append (list1)
        lista_total.append (list2)
        lista_total.append (list3)

        return  lista_total, n_processos, n_nomeacoes, n_peritos
    
# def codigo_padrao_TJSP(tribunal, re_processo, peritos_negativos, keyword_positivas, keyword_negativas):
#     """
#     Realiza todas as operações necessárias para a extração de dados do pdf.
#     """
#     n_processos = n_nomeacoes = n_peritos = 0
    
#     assert tribunal, "O nome do tribunal não pode estar vazio."
#     assert re_processo, "A expressão regular não pode estar vazia."

#     # Ler o PDF
#     nome_arquivo = f'diario_{tribunal}.pdf'
    
#     # Lendo PDF
#     pdf = pdf_string(nome_arquivo)

#     if pdf:
#         #Listando Processos
#         processos = lista_processo (pdf,re_processo)
#         print("Processos: "+ str(len(processos)))
#         n_processos = len(processos)

#         #Criando lista com palavras positiva "Nomeio"
#         nomeacao = separando_nomeacao ("nomeio",processos)
#         print("Nomeação: "+str(len(nomeacao)))
#         n_nomeacoes = len(nomeacao)

#         #Limpando string Ex. tirando quebra de linha
#         nomeacao = limpando_lista(nomeacao, tribunal)

#         #lista com peritos positivos
#         nomeacao_primeira_lista = removendo_negativo (keyword_negativas,nomeacao)
#         lista_sobra = removendo_lista(nomeacao,nomeacao_primeira_lista)
#         print("Peritos: "+str(len(nomeacao_primeira_lista)))
#         n_peritos = len(nomeacao_primeira_lista)

#         #Lista com Palavras Positivas
#         nomeacao_segunda_lista = separando_positivo (keyword_positivas,lista_sobra)
#         nomeacao_segunda_lista = removendo_negativo (keyword_negativas,nomeacao_segunda_lista)
#         lista_sobra2 = removendo_lista(lista_sobra,nomeacao_segunda_lista)
#         print("Palavras: "+str(len(nomeacao_segunda_lista)))

#         #Lista Outros
#         keyword_negativas2=keyword_negativas+peritos_negativos
#         nomeacao_terceira_lista = removendo_negativo (keyword_negativas2,lista_sobra2)
#         print("Outros: "+str(len(nomeacao_terceira_lista)))

#         #Juntando as listas
#         list1=separando_n_processos(nomeacao_primeira_lista)
#         list2=separando_n_processos(nomeacao_segunda_lista)
#         list3=separando_n_processos(nomeacao_terceira_lista)
#         lista_total = []
#         lista_total.append (list1)
#         lista_total.append (list2)
#         lista_total.append (list3)

#         return  lista_total, n_processos, n_nomeacoes, n_peritos