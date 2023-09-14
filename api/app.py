import os
import time
import datetime
import logging
from functions import codigo_padrao, obtendo_dados_processo_e_advogados
from get_cellphone import get_cells, clean_data_cell, time
from gpt_summarizer import summarize
from datas_tribs import tribunal, re_processos, peritos_negativos, peritos_positivas, keyword_negativas, keyword_positivas, re_tribs, ufs
from data_csv import pd, get_existing_phones, spliting_dataframes
from pdfs import obter_hash_do_arquivo_local, obter_hash_do_pdf, baixar_pdf
from urls import get_url_TJDF, get_url_TRT18, get_url_TJSP
from scraping_TJSP import baixar_TJSP, rename_cads_temps
from whatsapp_api_client_python import API

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

hoje = datetime.datetime.now().strftime('%d-%m-%Y')
hora = datetime.datetime.now().strftime('%H:%M')
n_processos = n_nomeacoes = n_peritos = phones_in_db = phones_to_search = phones_found = phones_not_found = successful_messages = 0

tempo_de_espera = 600

def monitora_urls(data_df, hoje, hora, n_processos, n_nomeacoes, n_peritos, phones_in_db, phones_to_search, phones_found, phones_not_found, successful_messages):
    idInstance = os.environ.get('idInstance')
    apiTokenInstance = os.environ.get('apiTokenInstance')
    greenAPI = API.GreenApi(idInstance, apiTokenInstance)
    
    urls = [get_url_TJDF, get_url_TRT18, get_url_TJSP]
    for url_i in range(len(urls)):
        hora = datetime.datetime.now().strftime('%H:%M')

        try:
            url = urls[url_i]()
        except Exception as e:
            print(f'Erro ao obter a URL do {tribunal[url_i]}:', str(e))
        
        hash_local = ''
        hash_atual = ''
            
        if url_i == 2:
            nome_arquivo_local = 'diario_TJSPC.pdf'
            nome_arquivo_atual = 'diario_TJSPC_temp.pdf'
            for cad_TJSP in tribunal[2]:
                baixar_TJSP(cad_TJSP)
            logger.info(f'Hora: {hora}')
            logger.info(f'Verificando se tem diário novo do tribunal {tribunal[url_i]}.')
            hash_local = obter_hash_do_arquivo_local(nome_arquivo_local)
            hash_atual = obter_hash_do_arquivo_local(nome_arquivo_atual)
            logger.info(f'Diário novo: {hash_local != hash_atual}')
        else:
            nome_arquivo_local = f'diario_{tribunal[url_i]}.pdf'
            logger.info(f'Hora: {hora}')
            logger.info(f'Verificando se tem diário novo do tribunal {tribunal[url_i]}.')
            hash_local = obter_hash_do_arquivo_local(nome_arquivo_local)
            hash_atual = obter_hash_do_pdf(url)
            logger.info(f'Diário novo: {hash_local != hash_atual}')
        if hash_local != hash_atual:
            if url_i != 2:
                baixar_pdf(url, nome_arquivo_local, tribunal[url_i])
                logger.info('Obtendo dados dos processos.')
                lista_total_html, n_proc, n_nome, n_per  = codigo_padrao(tribunal[url_i], re_processos[url_i], peritos_positivas[url_i], peritos_negativos, keyword_positivas, keyword_negativas)
            if url_i == 2:
                for cad_TJSP in tribunal[2]:
                    rename_cads_temps(cad_TJSP)
                n_proc = n_nome = n_per = 0
                lista_total_html = []
                for trib in tribunal[2]:
                    logger.info('Obtendo dados dos processos.')
                    lista_total_tmp, n_proc_tmp, n_nome_tmp, n_per_tmp  = codigo_padrao(trib, re_processos[url_i], peritos_positivas[url_i], peritos_negativos, keyword_positivas, keyword_negativas)
                    lista_total_html += lista_total_tmp
                    n_proc += n_proc_tmp
                    n_nome += n_nome_tmp
                    n_per += n_per_tmp
            
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
            logger.info(f'Quantidade de processos a verificar no {tribunal[url_i]}: {len(df)}')
            
            agora = datetime.datetime.now()
            if agora.hour < 6:
                n_processos = n_nomeacoes = n_peritos = phones_in_db = phones_to_search = phones_found = phones_not_found = successful_messages = 0
            n_processos += len(df)
            
            df['data'] = hoje
            df['telefone'] = ' '
            df['data_ultima_msg'] = ''
            df = df[['Nome', 'OAB', 'UF', 'data','data_ultima_msg', 'telefone', 'N_Processo', 'T_Processo']]
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
            
            logger.info('Resumindo os processos com o chat GPT.')
            summarize(df_new)

            df_new = df_new.applymap(str)
            data_df = data_df.applymap(str)

            quant_linhas_subst = len(data_df[data_df['telefone'].isin(df_new['telefone'])])
            logger.info(f'Substituindo {quant_linhas_subst} linhas do CSV novo no antigo.')
            data_df = data_df[~data_df['telefone'].isin(df_new['telefone'])] 
            
            logger.info(f'Juntando CSVs. {len(data_df)} do antigo mais {len(df_new)} do novo')
            data_df = pd.concat([data_df, df_new], ignore_index=True) 
            data_df = data_df.applymap(str)
            
            logger.info('Salvando CSV')
            data_df.to_csv('/app/data/data_df.csv', index=False)
            logger.info(f'CSV salvo, {len(data_df)} entradas')
                                    
            restriction_df = pd.read_csv('/app/data/restriction_df.csv', sep=',')
            restriction_df = restriction_df.applymap(str)
            
            # df = pd.read_csv('/app/data/df.csv', sep=',')
            
            logger.info('Enviando mensagens.')
            template_texto = 'Prezado(a) Dr(a). {},\nSomos a PericialMed, empresa especialista em perícia médica judicial. Desejo comunicar uma movimentação significativa no processo {}. Preparamos um resumo desta movimentação para sua conveniência e compreensão.\nPor favor, selecione a melhor opção:\n1. Para receber o resumo da nomeação elaborado por nossa inteligência artificial, digite "1".\n2. Para obter informações sobre nosso programa de afiliados, que garante até 15% de comissão por indicação e proporciona 5% de desconto ao cliente, digite "2".\n3. Se optar por não receber mais atualizações de nosso sistema, por favor, digite "3".'
            for df_i in data_df.index:
                telefone = data_df.telefone[df_i]
                nome = data_df.Nome[df_i]
                if telefone != 'Não encontrado' and data_df.data[df_i] == hoje and data_df.data_ultima_msg[df_i] != hoje:
                    não_autorizado = restriction_df[restriction_df['telefone'] == telefone]
                    if não_autorizado.empty:
                        logger.info('autorizado')
                        response = greenAPI.sending.sendMessage('55'+f'{telefone}@c.us', template_texto.format(nome.capitalize(), data_df.N_Processo[df_i]))
                        if response.code == 200:
                            successful_messages += 1
                            data_df.data_ultima_msg[df_i] = hoje # Atualizando a data da última mensagem enviada

                        
            metricas_busca_ativa = {
                'data': hoje,
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
    logger.info('lendo CSV')
    data_df = pd.read_csv('/app/data/data_df.csv', sep=',')
    logger.info(f'CSV lido, {len(data_df)} entradas')
    
    logger.info(f"Monitorando URLs a cada {tempo_de_espera/60} minutos...")
    n_processos = n_nomeacoes = n_peritos = phones_in_db = phones_to_search = phones_found = phones_not_found = successful_messages = 0
    
    while True:
        agora = datetime.datetime.now()
        inicio = datetime.time(9, 0)  # 09:00 horas
        fim = datetime.time(18, 0)  # 17:00 horas

        if inicio <= agora.time() <= fim:
            logger.info('Passou no teste do horário')
            monitora_urls(data_df, hoje, hora, n_processos, n_nomeacoes, n_peritos, phones_in_db, phones_to_search, phones_found, phones_not_found, successful_messages)
            time.sleep(tempo_de_espera)
        else:
            logger.info("Fora do horário de funcionamento. Aguardando...")
            if agora.time() > fim:
                proximo_inicio = datetime.datetime(agora.year, agora.month, agora.day, 9, 0) + datetime.timedelta(days=1)
            else:
                proximo_inicio = datetime.datetime(agora.year, agora.month, agora.day, 9, 0)
          
            tempo_entredias = (proximo_inicio - agora).total_seconds()
            time.sleep(tempo_entredias)

if __name__ == '__main__':
    main()



    
