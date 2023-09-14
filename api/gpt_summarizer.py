import os
import pandas as pd
import requests

openAiToken = os.environ.get('openAiToken')

def get_summary(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openAiToken}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": f"Resuma em 3ª pessoa o seguinte texto: {text}, nesse resumo retire os nomes dos advogados e do juiz."
        }],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

def summarize(df):
    max_length = 13656

    df['t_sumarizado'] = ''
    for i in df.index:
        if df.telefone[i] != 'Não encontrado':
            txt = df['T_Processo'][i]

            # Se o texto é muito longo, dividir, sumarizar partes, e depois sumarizar o conjunto
            if len(txt) > max_length:
                pieces = [txt[j:j+max_length] for j in range(0, len(txt), max_length)]
                summarized_pieces = [get_summary(piece) for piece in pieces]
                combined_summary = " ".join(summarized_pieces)
                df['t_sumarizado'][i] = get_summary(combined_summary)
            else:
                df['t_sumarizado'][i] = get_summary(txt)