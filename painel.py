import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from datetime import datetime
import pytz

TZ = pytz.timezone("America/Sao_Paulo")
URL = "https://www.ib.unicamp.br/pos/proximasdefesas"

def buscar_defesas():
    session = requests.Session()
    r = session.get(URL, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Tente achar tabelas ou listas de defesas
    # Você vai ter que inspecionar o HTML real (no navegador) para ver quais tags/classes são usadas
    # Exemplo fictício:
    rows = soup.select("table.defesas tbody tr")
    dados = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            titulo = cols[0].get_text(strip=True)
            autor = cols[1].get_text(strip=True)
            data_hora = cols[2].get_text(strip=True)
            local = cols[3].get_text(strip=True)
            # Parse data_hora, ex: "20/09/2025 14:00"
            try:
                dt = datetime.strptime(data_hora, "%d/%m/%Y %H:%M")
                dt = TZ.localize(dt)
            except ValueError:
                # tentar outros formatos
                dt = None
            dados.append({
                "titulo": titulo,
                "autor": autor,
                "data_hora": dt,
                "local": local
            })

    df = pd.DataFrame(dados)
    return df

def painel_defesas():
    st.title("🎓 Próximas Defesas - IB Unicamp")
    df = buscar_defesas()
    if df.empty:
        st.info("Não foi possível encontrar defesas ou página inacessível.")
    else:
        df = df.sort_values("data_hora")
        df["data"] = df["data_hora"].dt.strftime("%d/%m/%Y")
        df["hora"] = df["data_hora"].dt.strftime("%H:%M")
        st.table(df[["data", "hora", "titulo", "autor", "local"]])

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    painel_defesas()
