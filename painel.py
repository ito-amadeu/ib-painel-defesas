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

# Estima fim como +3h (ajuste se necessário)
df["fim"] = df["inicio"] + timedelta(hours=3)

# Hora atual
agora = datetime.now(TZ)
hoje = agora.date()
fim_semana = hoje + timedelta(days=6 - hoje.weekday())  # domingo

# Classificação por status
def classificar(row):
    if row["inicio"] <= agora <= row["fim"]:
        return "andamento"
    elif row["data"].date() == hoje and row["inicio"] > agora:
        return "hoje"
    elif hoje < row["data"].date() <= fim_semana:
        return "semana"
    elif row["data"].date() > fim_semana:
        return "futuro"
    else:
        return "encerrada"

df["status"] = df.apply(classificar, axis=1)

# Mantém só as não encerradas
df = df[df["status"] != "encerrada"]

# ===============================
# UI
# ===============================
st.set_page_config(layout="wide")
st.title("📜 Painel de Defesas - IB Unicamp")
st.markdown(f"### 📅 Hoje: {hoje.strftime('%d/%m/%Y')} | ⏰ Agora: {agora.strftime('%H:%M')}")

def show_block(title, icon, data, always_show=True):
    if not data.empty:
        st.subheader(f"{icon} {title}")
        st.table(
            data[
                ["Data", "Hora", "Candidato", "Orientador", "Título", "Programa", "Nível", "Local"]
            ]
        )
    elif always_show:
        # Só mostra aviso nos blocos semanais/futuros
        st.info(f"Nenhuma {title.lower()} encontrada.")

# Blocos
show_block("Defesas em andamento", "📌", df[df["status"] == "andamento"].sort_values("inicio"), always_show=False)
show_block("Próximas de hoje", "⏭️", df[df["status"] == "hoje"].sort_values("inicio"), always_show=False)
show_block("Próximas desta semana", "📅", df[df["status"] == "semana"].sort_values("inicio"))
show_block("Futuras", "🔮", df[df["status"] == "futuro"].sort_values("inicio"))
