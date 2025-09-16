import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz

# ===============================
# Configurações
# ===============================
TZ = pytz.timezone("America/Sao_Paulo")

# Lê os dados do CSV
df = pd.read_csv("defesas_ib.csv")

# Converte colunas de data/hora
df["data"] = pd.to_datetime(df["data"], format="%d/%m/%y")
df["hora"] = pd.to_datetime(df["hora"], format="%H:%M").dt.time

# Cria colunas datetime completas
df["inicio_dt"] = df.apply(lambda r: TZ.localize(datetime.combine(r["data"], r["hora"])), axis=1)
df["fim_dt"] = df["inicio_dt"] + timedelta(hours=4)  # duração padrão

# Hora atual
agora = datetime.now(TZ)

# Classificação
def classificar(row):
    if row["inicio_dt"] <= agora <= row["fim_dt"]:
        return "andamento"
    elif agora < row["inicio_dt"]:
        return "proxima"
    return "encerrada"

df["status"] = df.apply(classificar, axis=1)

# Tempo formatado
def tempo_formatado(delta):
    total_min = int(delta.total_seconds() // 60)
    h, m = divmod(total_min, 60)
    return f"{h:02d}h {m:02d}m"

def info_tempo(row):
    if row["status"] == "andamento":
        return "⏳ " + tempo_formatado(row["fim_dt"] - agora)
    elif row["status"] == "proxima":
        return "🕒 " + tempo_formatado(row["inicio_dt"] - agora)
    else:
        return "✔️ Encerrada"

df["tempo"] = df.apply(info_tempo, axis=1)

# ===============================
# UI
# ===============================
st.set_page_config(layout="wide")
st.title("🎓 Painel de Defesas - IB Unicamp")
st.markdown(f"### 📅 Agora: {agora.strftime('%d/%m/%Y %H:%M')}")

# CSS para estilizar
st.markdown("""
    <style>
    .mono {
        font-family: monospace;
        font-size: 15px;
    }
    td, th {
        font-size: 15px;
        padding: 6px 12px;
        text-align: center;
    }
    th {
        font-weight: bold;
    }
    table {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Função para exibir tabela customizada
def df_to_styled_html(df):
    df = df.rename(columns={"tempo": "Status"})
    df = df[["data", "hora", "aluno", "titulo", "orientador", "Status"]]
    html = df.to_html(index=False, escape=False)

    # aplica fonte monoespaçada em colunas de data/hora
    for col in ["data", "hora"]:
        for val in df[col].astype(str).unique():
            html = html.replace(f'<td>{val}', f'<td class="mono">{val}')
    return html

# Em andamento
df_andamento = df[df["status"] == "andamento"].sort_values(by="inicio_dt")
if not df_andamento.empty:
    st.subheader("📌 Defesas em andamento")
    st.markdown(df_to_styled_html(df_andamento), unsafe_allow_html=True)
else:
    st.info("Nenhuma defesa em andamento no momento.")

# Próximas
df_proximas = df[df["status"] == "proxima"].sort_values(by="inicio_dt")
if not df_proximas.empty:
    st.subheader("⏭️ Próximas defesas")
    st.markdown(df_to_styled_html(df_proximas), unsafe_allow_html=True)
else:
    st.info("Nenhuma defesa futura cadastrada.")

# Encerradas (opcional)
df_passadas = df[df["status"] == "encerrada"].sort_values(by="inicio_dt", ascending=False)
if not df_passadas.empty:
    st.subheader("✔️ Defesas encerradas")
    st.markdown(df_to_styled_html(df_passadas.head(5)), unsafe_allow_html=True)
