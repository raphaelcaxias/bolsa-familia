import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import BytesIO

# ============================================
# CONFIGURAÇÃO
# ============================================
st.set_page_config(page_title="Análise de Bolsas CNPq", layout="wide")
st.title("📊 Impacto das bolsas de pesquisa do CNPq")
st.markdown("**Dados direto do Google Drive – Limpeza e análise para portfólio**")

# ============================================
# ID DO ARQUIVO
# ============================================
FILE_ID = "1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub"

# ============================================
# FUNÇÃO PARA BAIXAR DO GOOGLE DRIVE
# ============================================
@st.cache_data
def baixar_csv_do_drive(file_id):
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0"
    
    try:
        response = requests.get(url, stream=True, allow_redirects=True, timeout=120)
        
        if response.status_code == 200:
            content = BytesIO(response.content)
            return content
        else:
            return None
    except Exception as e:
        st.error(f"Erro no download: {e}")
        return None

# ============================================
# FUNÇÃO PARA LER CSV CORRETAMENTE
# ============================================
def ler_csv_corretamente(content):
    # Testa diferentes separadores e encodings
    separadores = [';', ',']
    encodings = ['latin1', 'utf-8', 'ISO-8859-1', 'cp1252']
    
    for encoding in encodings:
        for sep in separadores:
            try:
                content.seek(0)
                # Testa com poucas linhas primeiro
                df_test = pd.read_csv(content, delimiter=sep, encoding=encoding, nrows=5)
                
                # Se leu poucas colunas (menos de 30), é provavelmente o separador correto
                if len(df_test.columns) < 50:
                    content.seek(0)
                    df = pd.read_csv(content, delimiter=sep, encoding=encoding, low_memory=False)
                    st.success(f"✅ Leitura bem-sucedida! Separador: '{sep}', Encoding: {encoding}")
                    st.info(f"📊 Estrutura: {df.shape[0]} linhas, {df.shape[1]} colunas")
                    return df
            except:
                continue
    
    return None

# ============================================
# FUNÇÃO DE LIMPEZA CORRIGIDA
# ============================================
def limpar_dados(df):
    df_clean = df.copy()
    
    # Remove espaços dos nomes das colunas
    df_clean.columns = df_clean.columns.str.strip()
    
    # Verifica se as colunas esperadas existem
    colunas_esperadas = ['valor_pago', 'beneficiario', 'instituicao_destino']
    for col in colunas_esperadas:
        if col not in df_clean.columns:
            st.warning(f"Coluna '{col}' não encontrada. Colunas disponíveis: {list(df_clean.columns[:10])}")
            return None
    
    # Converte datas (vários formatos)
    for col in ['data_inicio_processo', 'data_termino_processo']:
        if col in df_clean.columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], format='%d/%m/%Y', errors='coerce')
            except:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], format='%Y-%m-%d', errors='coerce')
                except:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
    
    # Converte valor_pago
    if 'valor_pago' in df_clean.columns:
        df_clean['valor_pago'] = (
            df_clean['valor_pago']
            .astype(str)
            .str.replace(',', '.', regex=False)
            .str.replace('R$', '', regex=False)
            .str.replace(' ', '', regex=False)
            .str.extract(r'(\d+\.?\d*)', expand=False)
        )
        df_clean['valor_pago'] = pd.to_numeric(df_clean['valor_pago'], errors='coerce')
    
    # Remove linhas sem valor
    df_clean = df_clean.dropna(subset=['valor_pago'])
    
    if len(df_clean) == 0:
        st.error("Nenhum dado válido após limpeza!")
        return None
    
    # Padroniza texto
    for col in ['grande_area', 'regiao', 'modalidade']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()
            df_clean[col] = df_clean[col].replace(['NAN', 'NONE', '', 'NULO', 'NAN', 'NONE'], np.nan)
    
    return df_clean

# ============================================
# MAIN
# ============================================
st.sidebar.header("📂 Carregar Dados")

opcao = st.sidebar.radio(
    "Escolha como carregar os dados:",
    ["📥 Download automático do Google Drive", "📤 Upload manual do CSV"]
)

if opcao == "📥 Download automático do Google Drive":
    if st.button("📥 Carregar dados do Google Drive"):
        with st.spinner("Baixando arquivo de 110MB... Isso pode levar até 2 minutos."):
            content = baixar_csv_do_drive(FILE_ID)
            
            if content:
                with st.spinner("Lendo e processando arquivo..."):
                    df_raw = ler_csv_corretamente(content)
                    
                    if df_raw is not None and len(df_raw.columns) < 100:
                        st.success(f"✅ Arquivo carregado: {df_raw.shape[0]:,} linhas, {df_raw.shape[1]} colunas")
                        
                        with st.expander("🔍 Ver primeiras linhas (dados brutos)"):
                            st.dataframe(df_raw.head(10))
                        
                        with st.spinner("Limpando dados..."):
                            df_clean = limpar_dados(df_raw)
                        
                        if df_clean is not None:
                            st.success(f"✅ Dados limpos: {df_clean.shape[0]:,} registros válidos")
                            
                            # Métricas
                            st.subheader("📈 Visão geral do investimento")
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("💰 Investimento total", f"R$ {df_clean['valor_pago'].sum():,.2f}")
                            col2.metric("👥 Pesquisadores únicos", f"{df_clean['beneficiario'].nunique():,}")
                            col3.metric("🏫 Instituições atendidas", f"{df_clean['instituicao_destino'].nunique():,}")
                            col4.metric("🏆 Maior bolsa", f"R$ {df_clean['valor_pago'].max():,.2f}")
                            
                            # Tabelas
                            if 'grande_area' in df_clean.columns:
                                st.subheader("📌 Investimento por Grande Área")
                                area_invest = (
                                    df_clean.groupby('grande_area')['valor_pago']
                                    .sum()
                                    .sort_values(ascending=False)
                                    .reset_index()
                                    .round(2)
                                )
                                st.dataframe(area_invest, use_container_width=True)
                            
                            if 'regiao' in df_clean.columns:
                                st.subheader("📍 Investimento por Região")
                                reg_invest = (
                                    df_clean.groupby('regiao')['valor_pago']
                                    .sum()
                                    .sort_values(ascending=False)
                                    .reset_index()
                                    .round(2)
                                )
                                st.dataframe(reg_invest, use_container_width=True)
                            
                            if 'modalidade' in df_clean.columns:
                                st.subheader("🎓 Top 10 Modalidades")
                                modal_count = (
                                    df_clean['modalidade']
                                    .value_counts()
                                    .reset_index()
                                    .head(10)
                                )
                                modal_count.columns = ['Modalidade', 'Quantidade']
                                st.dataframe(modal_count, use_container_width=True)
                            
                            # Download
                            st.subheader("⬇️ Exportar dados limpos")
                            csv_limpo = df_clean.to_csv(index=False, sep=';', decimal=',')
                            st.download_button(
                                label="Baixar CSV tratado",
                                data=csv_limpo,
                                file_name="bolsas_cnpq_tratado.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error("❌ Falha ao ler o arquivo. Use a opção de upload manual.")
            else:
                st.error("❌ Falha no download. Use a opção de upload manual.")

else:  # Upload manual
    st.info("👈 **Faça o upload manual do arquivo CSV**")
    
    uploaded_file = st.file_uploader("Envie o arquivo CSV (mesmo do Google Drive)", type=["csv"])
    
    if uploaded_file is not None:
        with st.spinner("Lendo arquivo..."):
            content = BytesIO(uploaded_file.getvalue())
            df_raw = ler_csv_corretamente(content)
            
            if df_raw is not None and len(df_raw.columns) < 100:
                st.success(f"✅ Arquivo carregado: {df_raw.shape[0]:,} linhas, {df_raw.shape[1]} colunas")
                
                with st.expander("🔍 Ver primeiras linhas (dados brutos)"):
                    st.dataframe(df_raw.head(10))
                
                with st.spinner("Limpando dados..."):
                    df_clean = limpar_dados(df_raw)
                
                if df_clean is not None:
                    st.success(f"✅ Dados limpos: {df_clean.shape[0]:,} registros válidos")
                    
                    # Métricas
                    st.subheader("📈 Visão geral do investimento")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("💰 Investimento total", f"R$ {df_clean['valor_pago'].sum():,.2f}")
                    col2.metric("👥 Pesquisadores únicos", f"{df_clean['beneficiario'].nunique():,}")
                    col3.metric("🏫 Instituições atendidas", f"{df_clean['instituicao_destino'].nunique():,}")
                    col4.metric("🏆 Maior bolsa", f"R$ {df_clean['valor_pago'].max():,.2f}")
                    
                    # Tabelas
                    if 'grande_area' in df_clean.columns:
                        st.subheader("📌 Investimento por Grande Área")
                        area_invest = (
                            df_clean.groupby('grande_area')['valor_pago']
                            .sum()
                            .sort_values(ascending=False)
                            .reset_index()
                            .round(2)
                        )
                        st.dataframe(area_invest, use_container_width=True)
                    
                    if 'regiao' in df_clean.columns:
                        st.subheader("📍 Investimento por Região")
                        reg_invest = (
                            df_clean.groupby('regiao')['valor_pago']
                            .sum()
                            .sort_values(ascending=False)
                            .reset_index()
                            .round(2)
                        )
                        st.dataframe(reg_invest, use_container_width=True)
                    
                    if 'modalidade' in df_clean.columns:
                        st.subheader("🎓 Top 10 Modalidades")
                        modal_count = (
                            df_clean['modalidade']
                            .value_counts()
                            .reset_index()
                            .head(10)
                        )
                        modal_count.columns = ['Modalidade', 'Quantidade']
                        st.dataframe(modal_count, use_container_width=True)
                    
                    # Download
                    st.subheader("⬇️ Exportar dados limpos")
                    csv_limpo = df_clean.to_csv(index=False, sep=';', decimal=',')
                    st.download_button(
                        label="Baixar CSV tratado",
                        data=csv_limpo,
                        file_name="bolsas_cnpq_tratado.csv",
                        mime="text/csv"
                    )
            else:
                st.error("❌ Falha ao ler o arquivo. Verifique se é o CSV correto.")
