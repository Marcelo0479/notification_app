import os
import datetime
import logging
from functions import codigo_padrao, obtendo_dados_processo_e_advogados
from get_cellphone import get_urlTJ, get_cells, clean_data_cell, time
from gpt_summarizer import summarize
from datas_tribs import tribunal, re_processos, peritos_negativos, peritos_positivas, keyword_negativas, keyword_positivas, re_tribs, ufs
from data_csv import pd, get_existing_phones, spliting_dataframes
from pdfs import obter_hash_do_arquivo_local, obter_hash_do_pdf, baixar_pdf
from whatsapp_api_client_python import API

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

data = datetime.datetime.now().strftime('%d-%m-%Y')
n_processos = n_nomeacoes = n_peritos = phones_in_db = phones_to_search = phones_found = phones_not_found = successful_messages = 0

tempo_de_espera = 600

def monitora_urls(urls, greenAPI, data_df, data, n_processos, n_nomeacoes, n_peritos, phones_in_db, phones_to_search, phones_found, phones_not_found, successful_messages):
    for url_i in range(len(urls)):
        nome_arquivo = f'diario_{tribunal[url_i]}.pdf'
        logger.info('Verificando hashs.')
        hash_local = obter_hash_do_arquivo_local(nome_arquivo)
        hash_atual = obter_hash_do_pdf(urls[url_i])
        if hash_local != hash_atual:
            baixar_pdf(urls[url_i], nome_arquivo, tribunal[url_i])
            logger.info('Obtendo dados dos processos.')
            lista_total_html, n_proc, n_nome, n_per  = codigo_padrao(urls[url_i],tribunal[url_i], re_processos[url_i], peritos_positivas[url_i], peritos_negativos, keyword_positivas, keyword_negativas)
            
            n_processos += n_proc
            n_nomeacoes += n_nome
            n_peritos += n_per
            
            dados = obtendo_dados_processo_e_advogados(lista_total_html, re_tribs[url_i])
            if dados[0][0] in ufs:
                df = pd.DataFrame(dados, columns=['UF', 'OAB', 'Nome', 'N_Processo', 'T_Processo'])
                df = df[['Nome', 'OAB', 'UF', 'N_Processo', 'T_Processo']]
            else:
                df = pd.DataFrame(dados, columns=['Nome', 'OAB', 'UF', 'N_Processo', 'T_Processo'])
                
            df.drop_duplicates(inplace=True, ignore_index=True)
            
            agora = datetime.datetime.now()
            if agora.hour < 6:
                n_processos = n_nomeacoes = n_peritos = phones_in_db = phones_to_search = phones_found = phones_not_found = successful_messages = 0
            n_processos += len(df)
            
            df['data'] = data
            df['telefone'] = ' '
            df = df[['Nome', 'OAB', 'UF', 'data', 'telefone', 'N_Processo', 'T_Processo']]
            # df = pd.read_csv('/app/data/df.csv', sep=',')
            df = df.applymap(str)
            
            logger.info('Verificando se alguma linha já tem número no csv')
            get_existing_phones(df, data_df)

            logger.info('Separando o datafreme em dois a partir das linhas que tem número e das que não tem')
            df_to_add_phone, df_with_phone = spliting_dataframes(df)
            phones_to_search += len(df_to_add_phone)
            phones_in_db += len(df_with_phone)
            
            logger.info('Buscando os números de celular.')
            df_new_phones = get_cells(df_to_add_phone)

            logger.info('Tratando os números de celular recem obtidos.')
            df_new_phones = df_new_phones.applymap(str)
            clean_data_cell(df_new_phones)

            phones_found += len(df_new_phones[df_new_phones['telefone'] != 'Não encontrado'])
            phones_not_found += len(df_new_phones[df_new_phones['telefone'] == 'Não encontrado'])

            logger.info('Juntando os dataframes com nº antigos e novos')
            df_new = pd.concat([df_with_phone, df_new_phones], ignore_index=True)
            
            # df = pd.read_csv('/app/data/df.csv', sep=',')
            # df_new = pd.concat([df_new, df], ignore_index=True)

            logger.info('Resumindo os processos com o chat GPT.')
            summarize(df_new)
            
            df_new.to_csv('/app/data/df_new', index=False)

            df_new = df_new.applymap(str)

            logger.info(f'Juntando CSVs. {len(data_df)} do antigo mais {len(df_new)} do novo')
            data_df = pd.concat([data_df, df_new], ignore_index=True)
            data_df.drop_duplicates(inplace=True, ignore_index=True)
            
            logger.info('Salvando CSV')
            data_df.to_csv('/app/data/data_df.csv', index=False)
            logger.info(f'CSV salvo, {len(data_df)} entradas')
            data_df = data_df.applymap(str)
                                    
            restriction_df = pd.read_csv('/app/data/restriction_df.csv', sep=',')
            restriction_df = restriction_df.applymap(str)

            logger.info('Enviando mensagens.')
            template_texto = 'Dr(a). {}, houve uma nomeação no processo {}.\n Digite 1 - Caso deseje ver um resumo da nomeação feito pelo chat GPT.\n Digite 2 - Caso deseje saber sobre o nosso programa de afiliados com até 15% de comissão por indicação e 5% de desconto para o cliente.\nDigite 3 - Caso não queira mais receber atualizações do nosso push.'
            for df_i in data_df.index:
                telefone = data_df.telefone[df_i]
                nome = data_df.Nome[df_i]
                if telefone != 'Não encontrado' and data_df.data[df_i] == data:
                    não_autorizado = restriction_df[restriction_df['telefone'] == telefone]
                    if não_autorizado.empty:
                        logger.info('autorizado')
                        response = greenAPI.sending.sendMessage('55'+f'{telefone}@c.us', template_texto.format(nome.capitalize(), data_df.N_Processo[df_i]))
                        if response.code == 200:
                            successful_messages += 1
                        
            metricas_busca_ativa = {
                'data': data,
                'n_processos': n_processos,
                'n_nomeacoes' : n_nomeacoes,
                'n_peritos' : n_peritos,
                'phones_in_db' : phones_in_db,
                'phones_to_search' : phones_to_search,
                'phones_found': phones_found,
                'phones_not_found': phones_not_found,
                'successful_messages': successful_messages
            }

            metricas_busca_ativa_df = pd.DataFrame([metricas_busca_ativa])
            metricas_busca_ativa_df = metricas_busca_ativa_df.applymap(str)
            try: 
                metricas_busca_ativa_db = pd.read_csv('/app/data/metricas_busca_ativa.csv', sep=',')
                metricas_busca_ativa_db = metricas_busca_ativa_db.applymap(str)
            except Exception as e:
                metricas_busca_ativa_df.to_csv('/app/data/metricas_busca_ativa.csv', index=False)
                metricas_busca_ativa_db = pd.read_csv('/app/data/metricas_busca_ativa.csv', sep=',')
                metricas_busca_ativa_db = metricas_busca_ativa_db.applymap(str)
                logger.info("Novo arquivo criado devido à exceção:", e)

            try:
                current_date = metricas_busca_ativa_df['data'].iloc[0]
                last_date_in_db = metricas_busca_ativa_db['data'].iloc[-1]
            except:
                logger.info(metricas_busca_ativa_df)
                
            if current_date == last_date_in_db:
                metricas_busca_ativa_db.iloc[-1] = metricas_busca_ativa_df.iloc[0]
            else:
                metricas_busca_ativa_db = pd.concat([metricas_busca_ativa_db, metricas_busca_ativa_df], ignore_index=True)

            metricas_busca_ativa_db.to_csv('/app/data/metricas_busca_ativa.csv', index=False)                    

def main():
    idInstance = os.environ.get('idInstance')
    apiTokenInstance = os.environ.get('apiTokenInstance')
    
    try:
        urlTJ = get_urlTJ()
    except Exception as e:
        print('Erro ao obter a URL do TJDFT:', str(e))

    urls = [urlTJ, 'https://diario.jt.jus.br/cadernos/Diario_J_18.pdf']
    greenAPI = API.GreenApi(idInstance, apiTokenInstance)

    logger.info('lendo CSV')
    data_df = pd.read_csv('/app/data/data_df.csv', sep=',')
    logger.info(f'CSV lido, {len(data_df)} entradas')
    
    logger.info(f"Monitorando URLs a cada {tempo_de_espera/60} minutos...")
    n_processos = n_nomeacoes = n_peritos = phones_in_db = phones_to_search = phones_found = phones_not_found = successful_messages = 0
    
    while True:
        logger.info('Verificando')
        monitora_urls(urls, greenAPI, data_df, data, n_processos, n_nomeacoes, n_peritos, phones_in_db, phones_to_search, phones_found, phones_not_found, successful_messages)
        time.sleep(tempo_de_espera)

if __name__ == '__main__':
    main()



    