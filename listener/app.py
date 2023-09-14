from flask import Flask, request
import requests
import os
import logging
import pandas as pd
import datetime
from whatsapp_api_client_python import API
from utils import marcar_n_receber

idInstance = os.environ.get('idInstance')
apiTokenInstance = os.environ.get('apiTokenInstance')
greenAPI = API.GreenApi(idInstance, apiTokenInstance)

messages_delivered = 0
messages_read = 0
messages_replied_with_1 = 0
messages_replied_with_2 = 0
messages_replied_with_3 = 0
different_message = 0

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/weebhook", methods=["GET", "POST"])
def resposta():
    global messages_delivered
    global messages_read
    global messages_replied_with_1
    global messages_replied_with_2
    global messages_replied_with_3
    global different_message
    
    hoje = datetime.datetime.now().strftime('%d-%m-%Y')

    data = request.get_json()
    logger.info(data)
       
    df = pd.read_csv("/app/data/data_df.csv", sep=',')
    df = df.applymap(str)
    
    try:
        messageData = data['messageData']['extendedTextMessageData']['text']
    except:    
        try:
            messageData = data['messageData']['textMessageData']['textMessage']
        except:
            logger.info('Mensagem não encontrada')
            
    try:
        senderData = data['senderData']['chatId']
        cel = senderData.strip('@c.us')
        cel = cel[2:]
        df_row = df[df.telefone == cel]
        if messageData == '1':
            message_text = df_row['t_sumarizado'].item()
            response = greenAPI.sending.sendMessage(f"55{cel}@c.us", message_text)
            messages_replied_with_1 += 1
        elif messageData == '2':
            message_text = 'Para mais detalhes entre em contato no 0800-104-0000'
            response = greenAPI.sending.sendMessage(f"55{cel}@c.us", message_text)
            messages_replied_with_2 += 1
            
            headers = {'Content-Type': 'application/json',}
            json_data = {
                'chatId': f'55{cel}@c.us',
                'message': 'Clique no botão "saber mais" e entraremos em contato no próximo dia útil',
                'buttons': [
                    {
                        'buttonId': '1',
                        'buttonText': 'tenho interesse',
                    },
                ],
            }
            response = requests.post(
                f'https://api.greenapi.com/waInstance{idInstance}/sendButtons/{apiTokenInstance}',
                headers=headers,
                json=json_data,
            )
        elif messageData == '3':
            message_text = 'Marcamos seu nº para não receber novas mensagens. Desculpe o incomodo'
            response = greenAPI.sending.sendMessage(f"55{cel}@c.us", message_text)
            messages_replied_with_3 += 1
            nome = df_row['Nome'].item()
            oab = df_row['OAB'].item()
            marcar_n_receber(nome, oab, cel)
        elif messageData not in ['1','2','3']:
            message_text = 'Somente 1, 2 e 3 são respostas válidas.'
            response = greenAPI.sending.sendMessage(f"55{cel}@c.us", message_text)
            different_message += 1
    except:
        logger.info('Sem mensagem')
        
    try:
        if data['status'] == 'delivered':
            messages_delivered +=1
        if data['status'] == 'read':
            messages_read +=1
    except:
        logger.info('Mensagem não possui status')
        
    metricas_escuta = {
        'data' : hoje,
        'messages_delivered' : messages_delivered,
        'messages_read': messages_read,
        'messages_replied_with_1' : messages_replied_with_1,
        'messages_replied_with_2' : messages_replied_with_2,
        'messages_replied_with_3' : messages_replied_with_3,
        'different_message' : different_message
    }
    
    metricas_escuta_df = pd.DataFrame([metricas_escuta])
    metricas_escuta_df = metricas_escuta_df.applymap(str)
    
    try:
        metricas_escuta_db = pd.read_csv('/app/data/metricas_escuta.csv', sep=',')
        metricas_escuta_db = metricas_escuta_db.applymap(str)
    except Exception as e:
        # Se houve uma exceção ao tentar ler (por exemplo, o arquivo não existe)
        # Criar um novo arquivo
        metricas_escuta_df.to_csv('/app/data/metricas_escuta.csv', index=False)
        metricas_escuta_db = pd.read_csv('/app/data/metricas_escuta.csv', sep=',')
        metricas_escuta_db = metricas_escuta_db.applymap(str)
        logger.info("Novo arquivo criado devido à exceção:", e)

    # Se chegou aqui, o arquivo foi lido com sucesso
    current_date = metricas_escuta_df['data'].iloc[0]
    last_date_in_db = metricas_escuta_db['data'].iloc[-1]

    if current_date == last_date_in_db:
        # Substitua a última linha se as datas forem iguais
        metricas_escuta_db.iloc[-1] = metricas_escuta_df.iloc[0]
    else:
        # Adicione uma nova linha se as datas forem diferentes
        metricas_escuta_db = pd.concat([metricas_escuta_db, metricas_escuta_df], ignore_index=True)

    # Salve o dataframe atualizado no arquivo
    metricas_escuta_db.to_csv('/app/data/metricas_escuta.csv', index=False)

    
    return 'Webhook ok'

    
if __name__ == '__main__':
    app.run()