import streamlit as st
import pandas as pd
import numpy as np
import gdown

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
OUTPUT_PATH = "bolsa_familia.csv"

# ============================================
# FUNÇÃO PARA BAIXAR
# ============================================
@st.cache_data
def baixar_csv_do_drive(file_id, output_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, output_path, quiet=False)
        return True
    except Exception as e:
        st.error(f"Erro ao baixar: {e}")
        return False

# ============================================
# FUNÇÃO PARA LER CSV COM MÚLTIPLOS ENCODINGS
# ============================================
def ler_csv_com_encoding_correto(caminho_arquivo):
    # Lista de encodings comuns em português
    encodings = ['latin1', 'ISO-8859-1', 'cp1252', 'WIN1252', 'utf-8']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(caminho_arquivo, delimiter=';', encoding=encoding)
            st.info(f"✅ Funcionou com encoding: {encoding}")
            return df
        except:
            continue
    
    raise Exception("Não foi possível ler o arquivo com nenhum encoding testado")

# ============================================
# FUNÇÃO DE LIMPEZA
# ============================================
def limpar_dados(df):
    df_clean = df.copy()

    # Remove espaços dos nomes das colunas
    df_clean.columns = df_clean.columns.str.strip()

    # Converte datas
    for col in ['data_inicio_processo', 'data_termino_processo']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], format='%d/%m/%Y', errors='coerce')

    # Converte valor_pago
    if 'valor_pago' in df_clean.columns:
        df_clean['valor_pago'] = (
            df_clean['valor_pago']
            .astype(str)
            .str.replace(',', '.', regex=False)
            .str.extract(r'(\d+\.?\d*)', expand=False)
        )
        df_clean['valor_pago'] = pd.to_numeric(df_clean['valor_pago'], errors='coerce')

    # Remove nulos
    df_clean = df_clean.dropna(subset=['valor_pago'])

    # Padroniza texto
    for col in ['grande_area', 'regiao', 'modalidade']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()
            df_clean[col] = df_clean[col].replace(['NAN', 'NONE', '', 'NULO'], np.nan)

    return df_clean

# ============================================
# MAIN
# ============================================
if st.button("📥 Carregar dados do Google Drive"):
    with st.spinner("Baixando arquivo de 110MB do Google Drive... Isso pode levar alguns segundos."):
        if baixar_csv_do_drive(FILE_ID, OUTPUT_PATH):
            st.success("✅ Arquivo baixado com sucesso!")
            
            with st.spinner("Lendo arquivo..."):
                try:
                    df_raw = ler_csv_com_encoding_correto(OUTPUT_PATH)
                    st.success(f"✅ Arquivo lido: {df_raw.shape[0]:,} linhas brutas, {df_raw.shape[1]} colunas")
                    
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
                    
                except Exception as e:
                    st.error(f"❌ Erro ao processar: {e}")
        else:
            st.error("❌ Falha ao baixar. Verifique se o arquivo está público no Google Drive.")

else:
    st.info("👈 **Clique no botão acima para carregar os dados diretamente do Google Drive**")
