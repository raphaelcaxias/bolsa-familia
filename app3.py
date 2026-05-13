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
# ID DO ARQUIVO (CORRIGIDO)
# ============================================
FILE_ID = "1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub"

# ============================================
# FUNÇÃO PARA BAIXAR DO GOOGLE DRIVE (MÉTODO ROBUSTO)
# ============================================
@st.cache_data
def baixar_csv_do_drive(file_id):
    # Método: download com confirmação (funciona para arquivos grandes)
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0"
    
    # Tenta também esta URL alternativa
    urls_tentar = [
        f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0",
        f"https://drive.google.com/uc?export=download&id={file_id}",
        f"https://drive.google.com/uc?id={file_id}&export=download"
    ]
    
    for url in urls_tentar:
        try:
            st.info(f"Tentando: {url[:50]}...")
            
            # Faz o download com stream
            response = requests.get(url, stream=True, allow_redirects=True)
            
            # Verifica se precisa de confirmação
            if "confirm=" in response.text and "download" in response.text.lower():
                # Extrai o token de confirmação
                import re
                confirm_match = re.search(r'confirm=([^&]+)', response.text)
                if confirm_match:
                    confirm_token = confirm_match.group(1)
                    url_confirm = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
                    response = requests.get(url_confirm, stream=True, allow_redirects=True)
            
            if response.status_code == 200:
                # Verifica se é um arquivo CSV (não uma página HTML)
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type and 'download' not in url:
                    continue  # Pula se for página HTML
                
                # Lê o conteúdo
                content = BytesIO(response.content)
                
                # Testa encodings
                encodings = ['latin1', 'ISO-8859-1', 'cp1252', 'WIN1252', 'utf-8']
                for encoding in encodings:
                    try:
                        content.seek(0)
                        df = pd.read_csv(content, delimiter=';', encoding=encoding)
                        st.success(f"✅ Funcionou com encoding: {encoding}")
                        return df
                    except:
                        continue
        except Exception as e:
            st.warning(f"Erro com esta URL: {str(e)[:100]}")
            continue
    
    return None

# ============================================
# FUNÇÃO DE LIMPEZA
# ============================================
def limpar_dados(df):
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.strip()

    for col in ['data_inicio_processo', 'data_termino_processo']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], format='%d/%m/%Y', errors='coerce')

    if 'valor_pago' in df_clean.columns:
        df_clean['valor_pago'] = (
            df_clean['valor_pago']
            .astype(str)
            .str.replace(',', '.', regex=False)
            .str.extract(r'(\d+\.?\d*)', expand=False)
        )
        df_clean['valor_pago'] = pd.to_numeric(df_clean['valor_pago'], errors='coerce')

    df_clean = df_clean.dropna(subset=['valor_pago'])

    for col in ['grande_area', 'regiao', 'modalidade']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()
            df_clean[col] = df_clean[col].replace(['NAN', 'NONE', '', 'NULO'], np.nan)

    return df_clean

# ============================================
# MAIN
# ============================================
if st.button("📥 Carregar dados do Google Drive"):
    with st.spinner("Baixando arquivo de 110MB do Google Drive... Isso pode levar até 2 minutos."):
        df_raw = baixar_csv_do_drive(FILE_ID)
        
        if df_raw is not None:
            st.success(f"✅ Arquivo carregado: {df_raw.shape[0]:,} linhas brutas, {df_raw.shape[1]} colunas")
            
            with st.expander("🔍 Ver primeiras linhas (dados brutos)"):
                st.dataframe(df_raw.head(10))
            
            with st.spinner("Limpando dados..."):
                df_clean = limpar_dados(df_raw)
            
            st.success(f"✅ Dados limpos: {df_clean.shape[0]:,} registros válidos")
            
            # Métricas
            st.subheader("📈 Visão geral do investimento")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Investimento total", f"R$ {df_clean['valor_pago'].sum():,.2f}")
            col2.metric("👥 Pesquisadores únicos", f"{df_clean['beneficiario'].nunique():,}")
            col3.metric("🏫 Instituições atendidas", f"{df_clean['instituicao_destino'].nunique():,}")
            col4.metric("🏆 Maior bolsa", f"R$ {df_clean['valor_pago'].max():,.2f}")
            
            # Tabelas
            st.subheader("📌 Investimento por Grande Área")
            area_invest = (
                df_clean.groupby('grande_area')['valor_pago']
                .sum()
                .sort_values(ascending=False)
                .reset_index()
                .round(2)
            )
            st.dataframe(area_invest, use_container_width=True)
            
            st.subheader("📍 Investimento por Região")
            reg_invest = (
                df_clean.groupby('regiao')['valor_pago']
                .sum()
                .sort_values(ascending=False)
                .reset_index()
                .round(2)
            )
            st.dataframe(reg_invest, use_container_width=True)
            
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
            st.error("❌ Falha ao baixar. Vamos tentar outra abordagem.")
            
            # Instruções manuais
            st.markdown("""
            ### 🔧 **Solução alternativa: Download manual**
            
            Como o download automático está falhando, faça o download manual:
            
            1. **Clique neste link** (abre em nova aba):
               [Baixar arquivo do Google Drive](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)
            
            2. **Salve o arquivo** no seu computador
            
            3. **Use o upload manual abaixo**:
            """)
            
            # Upload manual como fallback
            st.subheader("📤 Upload manual do arquivo")
            uploaded_file = st.file_uploader("Ou envie o arquivo CSV manualmente", type=["csv"])
            
            if uploaded_file is not None:
                df_raw = pd.read_csv(uploaded_file, delimiter=';', encoding='latin1')
                st.success("✅ Arquivo carregado via upload!")
                # ... resto do processamento

else:
    st.info("👈 **Clique no botão acima para carregar os dados diretamente do Google Drive**")
    st.markdown("""
    ### 📋 Sobre este app:
    - Baixa automaticamente um CSV de **110MB** do Google Drive
    - Detecta o encoding correto (latin1, utf-8, etc)
    - Aplica limpeza profissional
    - Gera métricas e tabelas para seu portfólio
    
    **Se o download automático falhar, use a opção de upload manual.**
    """)
