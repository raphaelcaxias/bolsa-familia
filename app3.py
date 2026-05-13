import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="CNPq Analytics", layout="wide")

# CSS básico
st.markdown("""
<style>
.stApp { background: #0f172a; }
</style>
""", unsafe_allow_html=True)

st.title("📊 CNPq Analytics - Bolsas de Pesquisa")

# Sidebar
with st.sidebar:
    st.markdown("## 🔬 Upload do Arquivo")
    uploaded_file = st.file_uploader("Envie o CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Tenta ler o arquivo
        df = pd.read_csv(uploaded_file, delimiter=';', encoding='latin1', low_memory=False)
        
        st.success(f"✅ {len(df):,} linhas carregadas")
        
        # Limpeza básica
        if 'valor_pago' in df.columns:
            df['valor_pago'] = df['valor_pago'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)')
            df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')
            df = df.dropna(subset=['valor_pago'])
        
        if 'data_inicio_processo' in df.columns:
            df['data_inicio_processo'] = pd.to_datetime(df['data_inicio_processo'], errors='coerce', dayfirst=True)
            df['ano'] = df['data_inicio_processo'].dt.year
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Investimento Total", f"R$ {df['valor_pago'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("👥 Pesquisadores", f"{df['beneficiario'].nunique():,}".replace(",", ".") if 'beneficiario' in df.columns else "N/A")
        col3.metric("🏫 Instituições", f"{df['instituicao_destino'].nunique():,}".replace(",", ".") if 'instituicao_destino' in df.columns else "N/A")
        col4.metric("📊 Ticket Médio", f"R$ {df['valor_pago'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        # Gráfico 1: Áreas
        if 'grande_area' in df.columns:
            st.subheader("📌 Investimento por Grande Área")
            area_data = df.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(area_data, x='grande_area', y='valor_pago', title="Top 10 Áreas")
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico 2: Regiões
        if 'regiao' in df.columns:
            st.subheader("🗺️ Distribuição Regional")
            reg_data = df.groupby('regiao')['valor_pago'].sum().reset_index()
            fig2 = px.bar(reg_data, x='regiao', y='valor_pago', title="Investimento por Região")
            fig2.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico 3: Evolução
        if 'ano' in df.columns:
            st.subheader("📅 Evolução Temporal")
            ano_data = df.groupby('ano')['valor_pago'].sum().reset_index()
            fig3 = px.line(ano_data, x='ano', y='valor_pago', markers=True, title="Evolução do Investimento")
            fig3.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Insights
        st.subheader("🔍 Principais Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'regiao' in df.columns:
                top_reg = df.groupby('regiao')['valor_pago'].sum().idxmax()
                st.info(f"📍 **Região com maior investimento:** {top_reg}")
        
        with col2:
            if 'grande_area' in df.columns:
                top_area = df.groupby('grande_area')['valor_pago'].sum().idxmax()
                st.info(f"🧬 **Área com maior investimento:** {top_area}")
        
        # Download
        st.subheader("📥 Download")
        csv = df.to_csv(index=False, sep=';').encode('utf-8')
        st.download_button("Baixar CSV", csv, f"dados_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
    except Exception as e:
        st.error(f"Erro: {e}")
        st.info("Tente salvar o CSV com encoding UTF-8 e separador ponto e vírgula (;)")

else:
    st.info("👈 Faça upload do arquivo CSV no menu lateral")
