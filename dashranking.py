import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração do título do Dashboard
st.title("📊 Acompanhamento Diário - Equipe Cobrança")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregar Planilha de Dados", type=["xlsx"])

if uploaded_file:
    # Carregar os dados
    df = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_name = list(df.keys())[0]  # Pega a primeira aba do Excel
    df = df[sheet_name]
    
    # Ajustar nomes das colunas removendo espaços extras
    df.columns = df.columns.str.strip()
    
    # Conversão de datas
    df["Vencimento"] = pd.to_datetime(df["Vencimento"], errors='coerce')
    df["Liquidação"] = pd.to_datetime(df["Liquidação"], errors='coerce')
    
    # Cálculo de atraso
    df["Dias em Atraso"] = (df["Liquidação"] - df["Vencimento"]).dt.days
    
    # KPIs gerais
    volume_liquidacao = df["Pago"].sum()
    media_atraso = df["Dias em Atraso"].mean()
    valor_multa_juros = df["Multa"].sum() + df["Taxa Juros"].sum()
    
    # Exibição de KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Volume de Liquidação", f"R$ {volume_liquidacao:,.2f}")
    col2.metric("Média de Dias em Atraso", f"{media_atraso:.1f} dias")
    col3.metric("Multa + Juros", f"R$ {valor_multa_juros:,.2f}")
    
    # Ranking de recebimento por auxiliar
    auxiliares = ["Julia", "JUSSARA", "Rogerio"]
    df_auxiliar = df[df["Auxiliar"].isin(auxiliares)]
    recebido_por_auxiliar = df_auxiliar.groupby("Auxiliar")["Pago"].sum().reset_index()
    
    # Garantir que todos os auxiliares apareçam no ranking
    ranking_auxiliares = pd.DataFrame({"Auxiliar": auxiliares})
    ranking_auxiliares = ranking_auxiliares.merge(recebido_por_auxiliar, on="Auxiliar", how="left").fillna(0)
    ranking_auxiliares = ranking_auxiliares.sort_values(by="Pago", ascending=False)
    
    # Gráfico de recebimento por auxiliar
    st.subheader("Ranking de Recebimento por Auxiliar")
    if not ranking_auxiliares.empty:
        fig = px.bar(ranking_auxiliares, x="Auxiliar", y="Pago", title="Recebimento por Auxiliar", 
                     labels={"Auxiliar": "Auxiliar", "Pago": "Valor Recebido"}, text_auto=True)
        st.plotly_chart(fig)
    else:
        st.write("Nenhum dado disponível.")
else:
    st.warning("Por favor, faça o upload do arquivo Excel para visualizar os dados.")
