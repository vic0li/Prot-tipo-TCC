# Página Dashboard Geral

import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Smart ICU Analytics",
    page_icon="🏥",
    layout="wide"
)

# =====================================================
# CARREGAMENTO DOS DADOS
# =====================================================

df = pd.read_csv(
    "data/raw/UTI_simulada_avancada2.csv"
)

# =====================================================
# CABEÇALHO
# =====================================================

st.title("🏥 Smart ICU Analytics")
st.caption(
    "Monitoramento Inteligente de Risco Clínico e Operacional em UTI"
)

st.divider()

# =====================================================
# KPIs PRINCIPAIS
# =====================================================

total_pacientes = df["id_paciente"].nunique()

total_alertas = (
    df["alerta_fc"].sum()
    + df["alerta_spo2"].sum()
    + df["alerta_temp"].sum()
    + df["alerta_lactato"].sum()
)

spo2_media = round(
    df["saturacao_O2"].mean(),
    1
)

fc_media = round(
    df["frequencia_cardiaca"].mean(),
    1
)

temp_media = round(
    df["temperatura"].mean(),
    1
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "👨‍⚕️ Pacientes",
        total_pacientes
    )

with col2:
    st.metric(
        "🚨 Alertas",
        int(total_alertas)
    )

with col3:
    st.metric(
        "🫁 SpO₂ Média",
        f"{spo2_media}%"
    )

with col4:
    st.metric(
        "❤️ FC Média",
        f"{fc_media} bpm"
    )

with col5:
    st.metric(
        "🌡️ Temp Média",
        f"{temp_media} °C"
    )

st.divider()

# =====================================================
# GRÁFICOS DE TENDÊNCIA
# =====================================================

col_esq, col_dir = st.columns(2)

with col_esq:

    st.subheader("❤️ Tendência da Frequência Cardíaca")

    fc_hora = (
        df.groupby("Hora")[
            "frequencia_cardiaca"
        ]
        .mean()
        .reset_index()
    )

    fig_fc = px.line(
        fc_hora,
        x="Hora",
        y="frequencia_cardiaca",
        markers=True,
        title="Média da FC por Hora"
    )

    st.plotly_chart(
        fig_fc,
        use_container_width=True
    )

with col_dir:

    st.subheader("🫁 Tendência da Saturação de O₂")

    spo2_hora = (
        df.groupby("Hora")[
            "saturacao_O2"
        ]
        .mean()
        .reset_index()
    )

    fig_spo2 = px.line(
        spo2_hora,
        x="Hora",
        y="saturacao_O2",
        markers=True,
        title="Média da SpO₂ por Hora"
    )

    st.plotly_chart(
        fig_spo2,
        use_container_width=True
    )

st.divider()

# =====================================================
# PACIENTES MAIS CRÍTICOS
# =====================================================

st.subheader("🔴 Top 10 Pacientes Mais Críticos")

criticos = (
    df.sort_values(
        by="lactato",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    criticos[
        [
            "id_paciente",
            "motivo_internacao",
            "saturacao_O2",
            "frequencia_cardiaca",
            "temperatura",
            "lactato",
            "pressao_media"
        ]
    ],
    use_container_width=True
)

st.divider()

# =====================================================
# DISTRIBUIÇÃO DOS MOTIVOS DE INTERNAÇÃO
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📊 Motivos de Internação")

    fig_motivos = px.pie(
        df,
        names="motivo_internacao",
        hole=0.4
    )

    st.plotly_chart(
        fig_motivos,
        use_container_width=True
    )

with col2:

    st.subheader("👥 Faixa Etária")

    fig_idade = px.histogram(
        df,
        x="idade",
        nbins=10
    )

    st.plotly_chart(
        fig_idade,
        use_container_width=True
    )

st.divider()

# =====================================================
# ALERTAS CLÍNICOS
# =====================================================

st.subheader("🚨 Alertas Clínicos Ativos")

alertas = df[
    (df["alerta_fc"] == 1)
    |
    (df["alerta_spo2"] == 1)
    |
    (df["alerta_temp"] == 1)
    |
    (df["alerta_lactato"] == 1)
]

st.dataframe(
    alertas[
        [
            "id_paciente",
            "Hora",
            "frequencia_cardiaca",
            "saturacao_O2",
            "temperatura",
            "lactato",
            "motivo_internacao"
        ]
    ].head(30),
    use_container_width=True
)

st.divider()

# =====================================================
# RESUMO OPERACIONAL
# =====================================================

st.subheader("📋 Resumo Operacional da UTI")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        f"Pacientes monitorados: {total_pacientes}"
    )

with col2:
    st.warning(
        f"Alertas detectados: {int(total_alertas)}"
    )

with col3:
    st.success(
        f"SpO₂ média da UTI: {spo2_media}%"
    )

st.divider()

st.caption(
    "Protótipo Conceitual - Smart ICU Analytics | TCC Engenharia Biomédica"
)