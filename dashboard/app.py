from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pandas as pd

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def dashboard():
    metricas_busca_ativa = pd.read_csv('/app/data/metricas_busca_ativa.csv', sep=',')
    metricas_escuta = pd.read_csv('/app/data/metricas_escuta.csv', sep=',')
    
    # Convertendo coluna 'data' para datetime
    # Convertendo coluna 'data' para datetime
    metricas_busca_ativa['data'] = pd.to_datetime(metricas_busca_ativa['data'], format='%d-%m-%Y')
    metricas_escuta['data'] = pd.to_datetime(metricas_escuta['data'], format='%d-%m-%Y')

    # Organizando pelo mais recente e selecionando as 7 entradas mais recentes
    metricas_busca_ativa = metricas_busca_ativa.sort_values(by='data', ascending=False)
    metricas_escuta = metricas_escuta.sort_values(by='data', ascending=False)


    return render_template('dashboard.html', metricas_busca_ativa=metricas_busca_ativa, metricas_escuta=metricas_escuta)

@socketio.on('request_update')
def handle_update():
    metricas_busca_ativa = pd.read_csv('/app/data/metricas_busca_ativa.csv', sep=',')
    metricas_escuta = pd.read_csv('/app/data/metricas_escuta.csv', sep=',')
    
    # Convertendo coluna 'data' para datetime
    metricas_busca_ativa['data'] = pd.to_datetime(metricas_busca_ativa['data'], format='%d-%m-%Y')  # Ajuste o formato conforme sua necessidade
    metricas_escuta['data'] = pd.to_datetime(metricas_escuta['data'], format='%d-%m-%Y')  # Ajuste o formato conforme sua necessidade

    # Organizando pelo mais recente e selecionando as 7 entradas mais recentes
    metricas_busca_ativa = metricas_busca_ativa.sort_values(by='data', ascending=False)
    metricas_escuta = metricas_escuta.sort_values(by='data', ascending=False)

    emit('data_update', {'busca_ativa': metricas_busca_ativa.to_dict(orient='records'), 
                         'escuta': metricas_escuta.to_dict(orient='records')})


if __name__ == "__main__":
    socketio.run(app, debug=True)
