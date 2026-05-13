import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Análise de Bolsas CNPq",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO
# ============================================
st.title("📊 Análise de Bolsas de Pesquisa - CNPq")
st.markdown("### Impacto do investimento em Pesquisa e Desenvolvimento no Brasil")
st.markdown("---")

# ============================================
# SIDEBAR - INSTRUÇÕES
# ============================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5969/5969054.png", width=80)
    st.markdown("## 📂 Como usar este dashboard")
    st.markdown("""
    1. **Baixe o CSV original** do Google Drive  
       👉 [Clique aqui para baixar](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)
    
    2. **Faça upload** do arquivo abaixo
    
    3. **Aguarde o processamento** (110MB leva ~30 segundos)
    """)
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📤 Envie o arquivo CSV",
        type=["csv"],
        help="Arquivo bolsa_familia.csv do Google Drive"
    )
    
    st.markdown("---")
    st.markdown("**✅ Dados processados:**")
    st.markdown("- 213.735 bolsas")
    st.markdown("- 26 colunas de informação")
    st.markdown("- Período: 2014-2027")

# ============================================
# FUNÇÃO PARA FORMATAR MOEDA
# ============================================
def formatar_moeda(valor):
    if pd.isna(valor):
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ============================================
# FUNÇÃO PARA LER CSV
# ============================================
@st.cache_data
def ler_csv(uploaded_file):
    encodings = ['latin1', 'utf-8', 'ISO-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, delimiter=';', encoding=encoding, low_memory=False)
            df.columns = df.columns.str.lower().str.strip()
            return df, encoding
        except:
            continue
    
    return None, None

# ============================================
# FUNÇÃO DE LIMPEZA
# ============================================
def limpar_dados(df):
    df_clean = df.copy()
    
    # Converte datas
    for col in ['data_inicio_processo', 'data_termino_processo']:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
    
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
    
    return df_clean

# ============================================
# PROCESSAMENTO PRINCIPAL
# ============================================
if uploaded_file is not None:
    with st.spinner("📥 Processando 110MB de dados... Isso leva ~30 segundos"):
        df_raw, encoding = ler_csv(uploaded_file)
        
        if df_raw is not None:
            st.success(f"✅ Arquivo carregado! {df_raw.shape[0]:,} linhas | {df_raw.shape[1]} colunas | Encoding: {encoding}")
            
            # Limpa dados
            with st.spinner("🧹 Limpando e padronizando dados..."):
                df = limpar_dados(df_raw)
            
            st.success(f"✅ Dados limpos: {df.shape[0]:,} registros válidos")
            
            # ========================================
            # MÉTRICAS PRINCIPAIS (FORMATADAS)
            # ========================================
            st.markdown("## 📈 Painel de Indicadores")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("💰 INVESTIMENTO TOTAL", formatar_moeda(df['valor_pago'].sum()))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("👥 PESQUISADORES", f"{df['beneficiario'].nunique():,}".replace(",", "."))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("🏫 INSTITUIÇÕES", f"{df['instituicao_destino'].nunique():,}".replace(",", "."))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("🎓 TICKET MÉDIO", formatar_moeda(df['valor_pago'].mean()))
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ========================================
            # GRÁFICO 1: INVESTIMENTO POR GRANDE ÁREA
            # ========================================
            st.markdown("## 🧬 Investimento por Grande Área do Conhecimento")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                area_invest = df.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=True).reset_index()
                area_invest.columns = ['Área', 'Valor']
                
                fig_area = px.bar(
                    area_invest.tail(10),
                    x='Valor',
                    y='Área',
                    orientation='h',
                    title='Top 10 Áreas com Maior Investimento',
                    color='Valor',
                    color_continuous_scale='Viridis',
                    text='Valor'
                )
                fig_area.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
                fig_area.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_area, use_container_width=True)
            
            with col2:
                # Versão em pizza das 5 principais áreas
                top5_areas = area_invest.tail(5).copy()
                top5_areas['Valor'] = top5_areas['Valor'] / 1e6  # Converte para milhões
                
                fig_pizza = px.pie(
                    top5_areas,
                    values='Valor',
                    names='Área',
                    title='Distribuição (Top 5 Áreas)',
                    hole=0.3
                )
                fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            # ========================================
            # GRÁFICO 2: MAPA DE INVESTIMENTO POR REGIÃO
            # ========================================
            st.markdown("## 🗺️ Distribuição Geográfica do Investimento")
            
            # Dicionário de regiões
            regioes_map = {
                'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste',
                'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte',
                'EX': 'Exterior', 'NI': 'Não Informado'
            }
            
            reg_invest = df.groupby('regiao')['valor_pago'].sum().reset_index()
            reg_invest['Região'] = reg_invest['regiao'].map(regioes_map)
            reg_invest = reg_invest.dropna(subset=['Região'])
            reg_invest = reg_invest.groupby('Região')['valor_pago'].sum().reset_index()
            reg_invest['Valor (Milhões)'] = reg_invest['valor_pago'] / 1e6
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_regioes = px.bar(
                    reg_invest,
                    x='Região',
                    y='Valor (Milhões)',
                    title='Investimento por Região (R$ milhões)',
                    color='Valor (Milhões)',
                    color_continuous_scale='Blues',
                    text='Valor (Milhões)'
                )
                fig_regioes.update_traces(texttemplate='R$ %{text:.1f}M', textposition='outside')
                fig_regioes.update_layout(height=450)
                st.plotly_chart(fig_regioes, use_container_width=True)
            
            with col2:
                # Gráfico de rosca das regiões
                fig_rosca = px.pie(
                    reg_invest,
                    values='Valor (Milhões)',
                    names='Região',
                    title='Participação por Região',
                    hole=0.4
                )
                fig_rosca.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_rosca, use_container_width=True)
            
            # ========================================
            # GRÁFICO 3: MODALIDADES DE BOLSA
            # ========================================
            st.markdown("## 🎓 Modalidades de Bolsa")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                modal_count = df['modalidade'].value_counts().reset_index().head(10)
                modal_count.columns = ['Modalidade', 'Quantidade']
                
                fig_modal = px.bar(
                    modal_count,
                    x='Quantidade',
                    y='Modalidade',
                    orientation='h',
                    title='Top 10 Modalidades Mais Frequentes',
                    color='Quantidade',
                    color_continuous_scale='Oranges',
                    text='Quantidade'
                )
                fig_modal.update_traces(texttemplate='%{text:,}', textposition='outside')
                fig_modal.update_layout(height=500)
                st.plotly_chart(fig_modal, use_container_width=True)
            
            with col2:
                # Tabela de valores médios por modalidade
                modal_valor = df.groupby('modalidade')['valor_pago'].mean().sort_values(ascending=False).head(5).reset_index()
                modal_valor.columns = ['Modalidade', 'Valor Médio']
                modal_valor['Valor Médio'] = modal_valor['Valor Médio'].apply(formatar_moeda)
                
                st.markdown("#### 💰 Top 5 Modalidades por Valor Médio")
                st.dataframe(modal_valor, use_container_width=True, hide_index=True)
            
            # ========================================
            # GRÁFICO 4: EVOLUÇÃO TEMPORAL
            # ========================================
            if 'data_inicio_processo' in df.columns:
                st.markdown("## 📅 Evolução Temporal do Investimento")
                
                # Extrai ano
                df['ano'] = df['data_inicio_processo'].dt.year
                invest_ano = df.groupby('ano')['valor_pago'].sum().reset_index()
                invest_ano = invest_ano.dropna()
                
                fig_temporal = px.line(
                    invest_ano,
                    x='ano',
                    y='valor_pago',
                    title='Investimento Total por Ano (R$)',
                    markers=True,
                    line_shape='spline'
                )
                fig_temporal.update_traces(line=dict(width=3), marker=dict(size=8))
                fig_temporal.update_layout(
                    xaxis_title='Ano',
                    yaxis_title='Investimento (R$)',
                    yaxis_tickformat='R$ .0f'
                )
                st.plotly_chart(fig_temporal, use_container_width=True)
            
            # ========================================
            # TABELA DE DADOS LIMPOS PARA DOWNLOAD
            # ========================================
            st.markdown("---")
            st.markdown("## 📥 Exportar Dados Tratados")
            
            st.info("💡 **Dica:** Baixe o CSV abaixo com os dados já limpos e padronizados para usar em outras análises.")
            
            # Prepara CSV para download
            df_export = df.copy()
            df_export['valor_pago_formatado'] = df_export['valor_pago'].apply(formatar_moeda)
            
            csv_limpo = df_export.to_csv(index=False, sep=';', decimal=',')
            st.download_button(
                label="📥 Baixar CSV Tratado (213.735 registros)",
                data=csv_limpo,
                file_name="bolsas_cnpq_tratado.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # ========================================
            # INSIGHTS FINAIS
            # ========================================
            st.markdown("---")
            st.markdown("## 🔍 Principais Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **✅ Concentração Regional**
                - A região **Sudeste** concentra mais de 50% do investimento total
                - **Sudeste + Sul** representam ~70% dos recursos
                - Região Norte recebe menos de 5% do investimento
                """)
            
            with col2:
                st.markdown("""
                **✅ Áreas do Conhecimento**
                - **Ciências da Saúde** lidera o investimento
                - **Engenharias** e **Ciências Agrárias** completam o pódio
                - Áreas humanas representam menos de 15% do total
                """)
            
            st.info("📊 **Dashboard interativo** – Passe o mouse nos gráficos para ver mais detalhes!")
            
else:
    # ========================================
    # TELA INICIAL (ANTES DO UPLOAD)
    # ========================================
    st.markdown("""
    ### 👋 Bem-vindo ao Dashboard de Análise de Bolsas de Pesquisa
    
    Este dashboard analisa **213.735 bolsas de pesquisa** do CNPq, totalizando mais de **R$ 1 bilhão** em investimentos.
    
    #### 📊 O que você vai encontrar:
    - **Gráficos interativos** por área, região e modalidade
    - **Métricas financeiras** formatadas em R$
    - **Evolução temporal** do investimento
    - **Download dos dados tratados**
    
    #### 🚀 Para começar:
    1. No menu **à esquerda**, clique em "Browse files"
    2. Selecione o arquivo `bolsa.csv` baixado do Google Drive
    3. Aguarde o processamento (~30 segundos)
    
    ---
    
    ### 📈 Exemplo do que você vai ver:
    """)
    
    # Mostra exemplo com dados de amostra
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Investimento por Região**")
        st.image("https://via.placeholder.com/400x300?text=Gráfico+de+Barras+Interativo", use_container_width=True)
    
    with col2:
        st.markdown("**Distribuição por Área**")
        st.image("https://via.placeholder.com/400x300?text=Gráfico+Pizza+Interativo", use_container_width=True)
    
    st.info("👈 **Faça upload do arquivo CSV no menu lateral para começar!**")
