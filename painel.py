import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

# ===============================
# Configurações
# ===============================
TZ = pytz.timezone("America/Sao_Paulo")

# Lê os dados (separador ;)
df = pd.read_csv("defesas_ib.csv", sep=";")

# Converte colunas de data e hora
df["data"] = pd.to_datetime(df["Data"], format="%d/%m/%y")
df["hora"] = pd.to_datetime(df["Hora"], format="%H:%M").dt.time

# Cria datetime completo
df["inicio"] = df.apply(lambda r: datetime.combine(r["data"].date(), r["hora"], tzinfo=TZ), axis=1)

# Define hora atual
agora = datetime.now(TZ)

# Status da defesa
def classificar(row):
    fim = row["inicio"] + timedelta(hours=3)  # estimando 3h por defesa
    if row["inicio"] <= agora <= fim:
        return "andamento"
    elif agora < row["inicio"]:
        return "proxima"
    else:
        return "encerrada"

df["status"] = df.apply(classificar, axis=1)

# Tempo restante ou até começar
def tempo_formatado(delta):
    total_min = int(delta.total_seconds() // 60)
    h, m = divmod(total_min, 60)
    return f"{h:02d}h {m:02d}m"

def info_tempo(row):
    fim = row["inicio"] + timedelta(hours=3)
    if row["status"] == "andamento":
        return tempo_formatado(fim - agora)
    elif row["status"] == "proxima":
        return tempo_formatado(row["inicio"] - agora)
    return None

df["tempo"] = df.apply(info_tempo, axis=1)

# ===============================
# UI
# ===============================
st.set_page_config(layout="wide")
st.title("📜 Painel de Defesas - IB Unicamp")
st.markdown(f"### 📅 Hoje: {agora.strftime('%d/%m/%Y')} | ⏰ Agora: {agora.strftime('%H:%M')}")

# Em andamento
df_andamento = df[df["status"] == "andamento"].sort_values("inicio")
if not df_andamento.empty:
    st.subheader("📌 Defesas em andamento")
    st.table(df_andamento[["Candidato", "Programa", "Nível", "Local", "inicio", "tempo"]])
else:
    st.info("Nenhuma defesa em andamento no momento.")

# Próximas
df_proximas = df[df["status"] == "proxima"].sort_values("inicio")
if not df_proximas.empty:
    st.subheader("⏭️ Próximas defesas")
    st.table(df_proximas[["Candidato", "Programa", "Nível", "Local", "inicio", "tempo"]])
else:
    st.info("Nenhuma defesa futura encontrada.")
