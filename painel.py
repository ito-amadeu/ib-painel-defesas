import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

# ===============================
# Configurações
# ===============================
TZ = pytz.timezone("America/Sao_Paulo")
st.set_page_config(layout="wide")
st.title("🎓 Painel de Defesas - IB Unicamp")

# Lê os dados
df = pd.read_csv("defesas_ib.csv")

# Normaliza colunas (ajuste se os nomes diferirem no CSV)
# Esperado: data, hora, candidato, orientador, titulo, local
df["data"] = pd.to_datetime(df["data"], dayfirst=True).dt.date
df["hora"] = pd.to_datetime(df["hora"], format="%H:%M").dt.time

# Cria datetime completo
df["inicio_dt"] = df.apply(lambda r: datetime.combine(r["data"], r["hora"], tzinfo=TZ), axis=1)

# Hora atual
agora = datetime.now(TZ)

# Status
def classificar(row):
    if agora > row["inicio_dt"] + timedelta(hours=4):  # assume defesas duram até 4h
        return "encerrada"
    elif row["inicio_dt"] <= agora <= row["inicio_dt"] + timedelta(hours=4):
        return "andamento"
    else:
        return "proxima"

df["status"] = df.apply(classificar, axis=1)

# Coluna de tempo dinâmico
def tempo_formatado(delta):
    total_min = int(delta.total_seconds() // 60)
    h, m = divmod(total_min, 60)
    return f"{h:02d}h {m:02d}m"

def info_tempo(row):
    if row["status"] == "andamento":
        return "⏳ " + tempo_formatado((row["inicio_dt"] + timedelta(hours=4)) - agora)
    elif row["status"] ==
