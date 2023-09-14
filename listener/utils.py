import pandas as pd

def marcar_n_receber(nome, oab, cel):
    nome = nome
    oab = oab
    cel = cel
    
    data_df = pd.read_csv('/app/data/data_df.csv', sep=',')
    data_df = data_df.applymap(str)
    
    restriction_df = pd.read_csv('/app/data/restriction_df.csv', sep=',')
    restriction_df = restriction_df.applymap(str)

    user_to_mark = data_df[(data_df['Nome'] == nome) & 
                             (data_df['OAB'] == oab) & 
                             (data_df['telefone'] == cel)]
    user_to_mark.reset_index(inplace=True, drop=True)
    
    colunas = ["Nome", "OAB", "telefone"]
    valores = [[user_to_mark.Nome[0], user_to_mark.OAB[0], user_to_mark.telefone[0]]]

    
    df_to_mark = pd.DataFrame(valores, columns=colunas)
    restriction_df = pd.concat([restriction_df, df_to_mark], ignore_index=True)
    restriction_df.to_csv('/app/data/restriction_df.csv', index=False)