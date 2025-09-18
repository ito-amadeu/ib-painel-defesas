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
st.set_page_config(
    page_title="Painel de Defesas - IB Unicamp",  # aparece na aba do navegador
    page_icon="📜",  # ícone na aba
    layout="wide"
)
# coloca no topo do seu app
st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

st.title("📜 Painel de Defesas - IB Unicamp")
st.markdown(f"### 📅 Hoje: {hoje.strftime('%d/%m/%Y')} | ⏰ Agora: {agora.strftime('%H:%M')}")

def show_block(title, icon, data, always_show=True):
    if not data.empty:
        st.subheader(f"{icon} {title}")

        # Seleciona colunas
        subset = data[["Data", "Hora", "Candidato", "Orientador", "Título", "Programa", "Nível", "Local"]]

        # Converte para HTML sem índice
        html = subset.to_html(index=False, escape=False)

        # CSS customizado
        st.markdown("""
            <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 6px 10px;
                text-align: left;
                font-size: 14px;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            td:nth-child(2) { text-align: center; font-family: monospace; } /* Hora */
            td:nth-child(1) { text-align: center; font-family: monospace; } /* Data */
            </style>
        """, unsafe_allow_html=True)

        st.markdown(html, unsafe_allow_html=True)

    elif always_show:
        st.info(f"Nenhuma {title.lower()} encontrada.")


# Blocos
show_block("Defesas em andamento", "📌", df[df["status"] == "andamento"].sort_values("inicio"), always_show=False)
show_block("Próximas de hoje", "⏭️", df[df["status"] == "hoje"].sort_values("inicio"), always_show=False)
show_block("Próximas desta semana", "📅", df[df["status"] == "semana"].sort_values("inicio"))
show_block("Futuras", "🔮", df[df["status"] == "futuro"].sort_values("inicio"))
