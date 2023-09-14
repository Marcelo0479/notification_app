import pandas as pd

def get_existing_phones(df, data_df):
    for i in df.index:
        phone_number = df['telefone'][i]
        row = data_df.query('telefone == @phone_number')
        if len(row) == 1:
            df['telefone'][i] = row['telefone'].item()


def spliting_dataframes(df):
    df_to_add_phone = df[df['telefone'] == ' ']
    df_to_add_phone.reset_index(drop=True, inplace=True)

    df_with_phone = df[df['telefone'] != ' ']
    df_with_phone.reset_index(drop=True, inplace=True)
    
    return df_to_add_phone, df_with_phone
