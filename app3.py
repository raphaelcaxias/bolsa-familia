import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# ============================================
# CONFIGURAÇÃO
# ============================================
st.set_page_config(page_title="Análise de Bolsas CNPq", layout="wide")
st.title("📊 Impacto das bolsas de pesquisa do CNPq")
st.markdown("**Dados direto do Google Drive – Limpeza e análise para portfólio**")

# ============================================
# FUNÇÃO PARA LER CSV CORRETAMENTE
# ============================================
@st.cache_data
def ler_csv(uploaded_file):
    # Testa diferentes encodings
    encodings = ['latin1', 'utf-8', 'ISO-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, delimiter=';', encoding=encoding, low_memory=False)
            
            # Converte nomes das colunas para MINÚSCULO (padroniza)
            df.columns = df.columns.str.lower().str.strip()
            
            st.success(f"✅ Leitura bem-sucedida! Encoding: {encoding}")
            return df
        except:
            continue
    
    return None

# ============================================
# FUNÇÃO DE LIMPEZA (agora com nomes minúsculos)
# ============================================
def limpar_dados(df):
    df_clean = df.copy()
    
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
    
    # Converte valor_pago (agora em minúsculo)
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
    else:
        st.error("❌ Coluna 'valor_pago' não encontrada!")
        st.write("Colunas disponíveis:", list(df_clean.columns))
        return None
    
    # Remove linhas sem valor
    df_clean = df_clean.dropna(subset=['valor_pago'])
    
    if len(df_clean) == 0:
        st.error("Nenhum dado válido após limpeza!")
        return None
    
    return df_clean

# ============================================
# MAIN
# ============================================
st.sidebar.header("📂 Carregar Dados")

st.sidebar.markdown("""
### Como carregar:

1. **Baixe o CSV do Google Drive**
2. **Faça upload abaixo**
3. **Aguarde o processamento**

O arquivo tem 110MB e pode levar alguns segundos.
""")

# Upload manual
uploaded_file = st.sidebar.file_uploader(
    "📤 Envie o arquivo CSV", 
    type=["csv"],
    help="Arquivo bolsa_familia.csv do Google Drive"
)

if uploaded_file is not None:
    with st.spinner("📥 Lendo arquivo de 110MB... Isso pode levar até 30 segundos."):
        df_raw = ler_csv(uploaded_file)
        
        if df_raw is not None:
            st.success(f"✅ Arquivo carregado: {df_raw.shape[0]:,} linhas, {df_raw.shape[1]} colunas")
            
            # Mostra preview
            with st.expander("🔍 Ver primeiras linhas (dados brutos)"):
                st.dataframe(df_raw.head(10))
            
            with st.spinner("🧹 Limpando e padronizando dados..."):
                df_clean = limpar_dados(df_raw)
            
            if df_clean is not None:
                st.success(f"✅ Dados limpos: {df_clean.shape[0]:,} registros válidos")
                
                # ================================
                # MÉTRICAS PRINCIPAIS
                # ================================
                st.subheader("📈 Visão geral do investimento")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("💰 Investimento total", f"R$ {df_clean['valor_pago'].sum():,.2f}")
                col2.metric("👥 Pesquisadores únicos", f"{df_clean['beneficiario'].nunique():,}")
                col3.metric("🏫 Instituições atendidas", f"{df_clean['instituicao_destino'].nunique():,}")
                col4.metric("🏆 Maior bolsa", f"R$ {df_clean['valor_pago'].max():,.2f}")
                
                # ================================
                # TABELA 1: Investimento por Grande Área
                # ================================
                if 'grande_area' in df_clean.columns:
                    st.subheader("📌 Investimento por Grande Área do Conhecimento")
                    area_invest = (
                        df_clean.groupby('grande_area')['valor_pago']
                        .sum()
                        .sort_values(ascending=False)
                        .reset_index()
                        .round(2)
                    )
                    area_invest.columns = ['Grande Área', 'Total Investido (R$)']
                    st.dataframe(area_invest, use_container_width=True)
                
                # ================================
                # TABELA 2: Investimento por Região
                # ================================
                if 'regiao' in df_clean.columns:
                    st.subheader("📍 Investimento por Região")
                    reg_invest = (
                        df_clean.groupby('regiao')['valor_pago']
                        .sum()
                        .sort_values(ascending=False)
                        .reset_index()
                        .round(2)
                    )
                    reg_invest.columns = ['Região', 'Total Investido (R$)']
                    st.dataframe(reg_invest, use_container_width=True)
                
                # ================================
                # TABELA 3: Modalidades mais frequentes
                # ================================
                if 'modalidade' in df_clean.columns:
                    st.subheader("🎓 Top 10 Modalidades de Bolsa")
                    modal_count = (
                        df_clean['modalidade']
                        .value_counts()
                        .reset_index()
                        .head(10)
                    )
                    modal_count.columns = ['Modalidade', 'Quantidade']
                    st.dataframe(modal_count, use_container_width=True)
                
                # ================================
                # DOWNLOAD CSV LIMPO
                # ================================
                st.subheader("⬇️ Exportar dados limpos")
                csv_limpo = df_clean.to_csv(index=False, sep=';', decimal=',')
                st.download_button(
                    label="📥 Baixar CSV tratado",
                    data=csv_limpo,
                    file_name="bolsas_cnpq_tratado.csv",
                    mime="text/csv"
                )
                
                # ================================
                # ESTATÍSTICAS ADICIONAIS
                # ================================
                with st.expander("📊 Estatísticas detalhadas"):
                    st.write("**Distribuição dos valores das bolsas:**")
                    st.write(f"- Média: R$ {df_clean['valor_pago'].mean():,.2f}")
                    st.write(f"- Mediana: R$ {df_clean['valor_pago'].median():,.2f}")
                    st.write(f"- Desvio padrão: R$ {df_clean['valor_pago'].std():,.2f}")
                    
                    st.write("**Período dos dados:**")
                    if 'data_inicio_processo' in df_clean.columns:
                        st.write(f"- Data mais antiga: {df_clean['data_inicio_processo'].min()}")
                        st.write(f"- Data mais recente: {df_clean['data_inicio_processo'].max()}")
        else:
            st.error("❌ Falha ao ler o arquivo. Verifique se é o CSV correto (separador ';')")
else:
    st.info("👈 **Clique em 'Browse files' no menu lateral para fazer upload do CSV**")
    st.markdown("""
    ### 📋 Sobre este app:
    - Processa o CSV de **110MB** com **213.735 bolsas** de pesquisa
    - Detecta encoding automaticamente (latin1, utf-8)
    - Gera **tabelas agregadas** prontas para seu portfólio
    - Exporta os dados **limpos e tratados**
    
    ### 🔧 Como obter o CSV:
    1. Acesse o link do Google Drive
    2. Clique em **"Download"**
    3. Volte aqui e faça **upload**
    """)
