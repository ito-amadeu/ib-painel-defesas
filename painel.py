import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from datetime import datetime
import pytz

# Configurações
TZ = pytz.timezone("America/Sao_Paulo")
URL = "https://www.ib.unicamp.br/pos/proximasdefesas"

def buscar_defesas():
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Encontrar o container que lista as defesas
    # *** Isso vai variar dependendo da estrutura real da página ***
    items = soup.select(".classeOuTagDasDefesas")  # ajustar
    dados = []
    for it in items:
        nome = it.select_one(".nomeTese").get_text(strip=True)
        autor = it.select_one(".autor").get_text(strip=True)
        orientador = it.select_one(".orientador").get_text(strip=True)
        data_hora = it.select_one(".dataHorario").get_text(strip=True)
        local = it.select_one(".local").get_text(strip=True)

        # Converter data_hora para datetime com timezone
        # Exemplo assumindo formato "DD/MM/YYYY HH:MM"
        dt = datetime.strptime(data_hora, "%d/%m/%Y %H:%M")
        dt = TZ.localize(dt)

        dados.append({
            "nome": nome,
            "autor": autor,
            "orientador": orientador,
            "data_hora": dt,
            "local": local
        })

    df = pd.DataFrame(dados)
    return df

# Streamlit UI
st.title("🎓 Próximas defesas - IB Unicamp")

df = buscar_defesas()
if df.empty:
    st.info("Não foi possível encontrar defesas ou está vazio.")
else:
    # Ordenar por data
    df = df.sort_values("data_hora")

    # Formatar colunas
    df["data"] = df["data_hora"].dt.strftime("%d/%m/%Y")
    df["hora"] = df["data_hora"].dt.strftime("%H:%M")

    st.table(df[["data", "hora", "nome", "autor", "orientador", "local"]])
