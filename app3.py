import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="CNPq Analytics | Intelligence Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CORES PREMIUM
# ============================================================
COR_FUNDO = "#0A0F1C"
COR_CARD = "rgba(18, 25, 45, 0.85)"
COR_BORDA = "rgba(56, 189, 248, 0.3)"
COR_GLOW = "rgba(56, 189, 248, 0.5)"
COR_TEXTO = "#F1F5F9"
COR_TEXTO_MUTED = "#94A3B8"
COR_AZUL = "#3B82F6"
COR_VERDE = "#10B981"

# ============================================================
# CSS PREMIUM
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

.stApp {{
    background: radial-gradient(circle at 20% 30%, #0A0F1C, #030712);
    font-family: 'Inter', sans-serif;
}}

.block-container {{
    padding: 1.5rem 2rem !important;
}}

/* Hero Section com Glow */
.hero {{
    background: linear-gradient(135deg, rgba(56,189,248,0.1) 0%, rgba(16,185,129,0.05) 100%);
    border-radius: 2rem;
    padding: 2rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid {COR_BORDA};
    box-shadow: 0 0 40px {COR_GLOW};
}}

.hero h1 {{
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FFFFFF, #38BDF8);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 0.5rem;
}}

.hero p {{
    font-size: 1rem;
    color: {COR_TEXTO_MUTED};
    margin-bottom: 1.2rem;
}}

.hero-badges {{
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
}}

.hero-badge {{
    background: rgba(56,189,248,0.15);
    border: 1px solid {COR_BORDA};
    padding: 0.3rem 0.8rem;
    border-radius: 2rem;
    font-size: 0.75rem;
    color: {COR_AZUL};
}}

/* Preview Cards */
.preview-grid {{
    display: flex;
    gap: 1.2rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}}

.preview-card {{
    flex: 1;
    min-width: 150px;
    background: {COR_CARD};
    backdrop-filter: blur(10px);
    border: 1px solid {COR_BORDA};
    border-radius: 1.2rem;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
}}

.preview-card:hover {{
    transform: translateY(-4px);
    border-color: {COR_AZUL};
    box-shadow: 0 0 20px {COR_GLOW};
}}

.preview-number {{
    font-size: 1.8rem;
    font-weight: 800;
    color: white;
}}

.preview-label {{
    font-size: 0.65rem;
    color: {COR_TEXTO_MUTED};
    text-transform: uppercase;
    margin-top: 0.2rem;
}}

/* Value Cards */
.value-card {{
    background: {COR_CARD};
    backdrop-filter: blur(10px);
    border: 1px solid {COR_BORDA};
    border-radius: 1rem;
    padding: 1rem;
    text-align: center;
    height: 100%;
}}

/* Upload Card */
.upload-card {{
    background: {COR_CARD};
    backdrop-filter: blur(10px);
    border: 2px dashed {COR_AZUL};
    border-radius: 1.5rem;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
}}

/* Botão */
.stButton > button {{
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border: 1px solid {COR_AZUL};
    border-radius: 2rem;
    color: white;
    padding: 0.4rem 1.2rem;
    font-weight: 500;
    transition: all 0.2s;
}}

.stButton > button:hover {{
    border-color: {COR_VERDE};
    box-shadow: 0 0 12px {COR_GLOW};
}}

/* Footer */
.footer {{
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    margin-top: 2rem;
    border-top: 1px solid {COR_BORDA};
    color: {COR_TEXTO_MUTED};
    font-size: 0.65rem;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: rgba(10, 15, 28, 0.95);
    backdrop-filter: blur(12px);
    border-right: 1px solid {COR_BORDA};
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES
# ============================================================
def fmt_brl(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0"
    if valor >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.1f}B".replace(".", ",")
    if valor >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    return f"R$ {valor:,.0f}".replace(",", ".")

def fmt_num(valor):
    if pd.isna(valor):
        return "0"
    return f"{int(valor):,}".replace(",", ".")

@st.cache_data
def carregar_dados(uploaded_file):
    for enc in ["latin1", "utf-8", "cp1252"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, delimiter=';', encoding=enc, low_memory=False)
            df.columns = df.columns.str.lower().str.strip()
            if 'valor_pago' in df.columns:
                df['valor_pago'] = pd.to_numeric(
                    df['valor_pago'].astype(str).str.replace(',', '.', regex=False).str.extract(r'(\d+\.?\d*)', expand=False),
                    errors='coerce'
                )
            df = df.dropna(subset=['valor_pago'])
            df = df[df['valor_pago'] > 0]
            if 'data_inicio_processo' in df.columns:
                df['data_inicio_processo'] = pd.to_datetime(df['data_inicio_processo'], errors='coerce', dayfirst=True)
                df['ano'] = df['data_inicio_processo'].dt.year
            regioes_map = {'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste', 'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte', 'EX': 'Exterior', 'NI': 'Não Informado'}
            if 'regiao' in df.columns:
                df['regiao_nome'] = df['regiao'].map(regioes_map).fillna(df['regiao'])
            return df
        except:
            continue
    return None

def grafico_barras_regional_vazio():
    """Gráfico de barras vazio (placeholder) antes do upload"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Aguardando dados...'],
        y=[0],
        marker_color=COR_AZUL,
        text=['Carregue o CSV para visualizar'],
        textposition='outside'
    ))
    fig.update_layout(
        title="📊 Distribuição Regional do Investimento",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Região",
        yaxis_title="Investimento (R$)",
        font=dict(color='white')
    )
    return fig

# ============================================================
# PÁGINA INICIAL (SEM UPLOAD)
# ============================================================
st.markdown("""
<div class="hero">
    <h1>🔬 CNPq Analytics</h1>
    <p>Inteligência estratégica para investimentos em pesquisa e desenvolvimento no Brasil</p>
    <div class="hero-badges">
        <span class="hero-badge">📊 Dados oficiais CNPq</span>
        <span class="hero-badge">🏛️ 213.735 bolsas</span>
        <span class="hero-badge">💰 R$ 1,02 bilhão</span>
        <span class="hero-badge">🗺️ Mapeamento regional</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Fonte dos dados e limites técnicos
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown("""
    <div style="background: rgba(18,25,45,0.5); border-radius: 1rem; padding: 1rem; margin-bottom: 1rem;">
        <h4 style="margin: 0 0 0.3rem 0;">📌 Fonte dos dados</h4>
        <p style="font-size: 0.75rem; color: #94A3B8;">Os dados são provenientes do <strong>Portal Brasileiro de Dados Abertos (CGU/CNPq)</strong>, com registros de bolsas de pesquisa concedidas entre 2014 e 2027.</p>
    </div>
    """, unsafe_allow_html=True)
with col_info2:
    st.markdown("""
    <div style="background: rgba(18,25,45,0.5); border-radius: 1rem; padding: 1rem; margin-bottom: 1rem;">
        <h4 style="margin: 0 0 0.3rem 0;">⚙️ Limite técnico</h4>
        <p style="font-size: 0.75rem; color: #94A3B8;">Arquivo CSV de até <strong>200 MB</strong> (recomendado até 500 mil linhas). O dashboard processa a base completa de 213.735 registros em tempo real.</p>
    </div>
    """, unsafe_allow_html=True)

# Prévia dos dados
st.markdown("### 📈 Conheça o potencial da análise")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="preview-card">
        <div class="preview-number">213.735</div>
        <div class="preview-label">Bolsas analisadas</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="preview-card">
        <div class="preview-number">R$ 1,02B</div>
        <div class="preview-label">Investimento total</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="preview-card">
        <div class="preview-number">88.079</div>
        <div class="preview-label">Pesquisadores</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div class="preview-card">
        <div class="preview-number">4.281</div>
        <div class="preview-label">Instituições</div>
    </div>
    """, unsafe_allow_html=True)

# Gráfico de barras vazio
st.markdown("### 🗺️ Visualize a distribuição geográfica")
st.plotly_chart(grafico_barras_regional_vazio(), use_container_width=True)

# Cards de valor agregado
st.markdown("### 💡 O que você vai descobrir")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    st.markdown("""
    <div class="value-card">
        <span style="font-size: 1.8rem;">🎯</span>
        <h4>Concentração regional</h4>
        <p style="color: #94A3B8; font-size: 0.75rem;">Identifique quais regiões lideram os investimentos</p>
    </div>
    """, unsafe_allow_html=True)
with col_v2:
    st.markdown("""
    <div class="value-card">
        <span style="font-size: 1.8rem;">🧬</span>
        <h4>Áreas do conhecimento</h4>
        <p style="color: #94A3B8; font-size: 0.75rem;">Saúde, Engenharia, Humanas – onde o dinheiro está</p>
    </div>
    """, unsafe_allow_html=True)
with col_v3:
    st.markdown("""
    <div class="value-card">
        <span style="font-size: 1.8rem;">🏆</span>
        <h4>Rankings de impacto</h4>
        <p style="color: #94A3B8; font-size: 0.75rem;">Top pesquisadores e instituições mais financiadas</p>
    </div>
    """, unsafe_allow_html=True)

# Upload card
st.markdown("""
<div class="upload-card">
    <span style="font-size: 2.5rem;">📂</span>
    <h3>Carregue o arquivo CSV</h3>
    <p style="color: #94A3B8; font-size: 0.8rem;">Baixe o dataset oficial do CNPq e faça upload para iniciar a análise completa</p>
    <p style="color: #3B82F6; font-size: 0.75rem;">⬅️ Use o menu lateral para enviar o arquivo</p>
</div>
""", unsafe_allow_html=True)

# Sidebar com upload
with st.sidebar:
    st.markdown("### 🎛️ Central Analítica")
    if st.button("☀️ Modo Claro", use_container_width=True):
        st.session_state.tema = "claro"
        st.rerun()
    if st.button("🌙 Modo Escuro", use_container_width=True):
        st.session_state.tema = "escuro"
        st.rerun()
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carregar CSV (bolsa_familia.csv)", type=["csv"])
    if uploaded_file is None:
        st.info("👈 Envie o arquivo para iniciar a análise avançada")
        st.stop()

# ============================================================
# PROCESSAMENTO APÓS UPLOAD
# ============================================================
with st.spinner("Processando dados..."):
    df = carregar_dados(uploaded_file)
if df is None:
    st.error("❌ Erro no CSV. Verifique separador ';' e encoding (latin1/utf-8).")
    st.stop()
st.success(f"✅ {df.shape[0]:,} registros carregados")

# Filtros
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧬 Filtros")
df_filtrado = df.copy()
if "ano" in df.columns:
    anos = sorted(df["ano"].dropna().unique().astype(int))
    if len(anos) > 1:
        ano_sel = st.sidebar.slider("Ano", min(anos), max(anos), (min(anos), max(anos)), step=1)
        df_filtrado = df_filtrado[(df_filtrado["ano"] >= ano_sel[0]) & (df_filtrado["ano"] <= ano_sel[1])]
if "grande_area" in df.columns:
    areas = sorted(df["grande_area"].dropna().unique())
    areas_sel = st.sidebar.multiselect("Grande Área", areas, default=areas[:6] if len(areas)>6 else areas)
    if areas_sel:
        df_filtrado = df_filtrado[df_filtrado["grande_area"].isin(areas_sel)]
if "regiao_nome" in df.columns:
    regioes = sorted(df["regiao_nome"].dropna().unique())
    reg_sel = st.sidebar.multiselect("Região", regioes, default=regioes)
    if reg_sel:
        df_filtrado = df_filtrado[df_filtrado["regiao_nome"].isin(reg_sel)]

# ============================================================
# DASHBOARD COMPLETO APÓS UPLOAD
# ============================================================
total_volume = df_filtrado["valor_pago"].sum()
total_bolsas = df_filtrado.shape[0]
ticket_medio = total_volume / total_bolsas if total_bolsas > 0 else 0
n_pesq = df_filtrado["beneficiario"].nunique() if "beneficiario" in df_filtrado.columns else 0
evolucao_ano = df_filtrado.groupby("ano")["valor_pago"].sum().sort_index()
if len(evolucao_ano) >= 2:
    delta_pct = (evolucao_ano.iloc[-1] / evolucao_ano.iloc[-2] - 1) * 100
    delta_sinal = "▲" if delta_pct > 0 else "▼"
else:
    delta_pct = 0
    delta_sinal = ""

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 INVESTIMENTO TOTAL", fmt_brl(total_volume), delta=f"{delta_sinal} {abs(delta_pct):.1f}% vs ano anterior")
with col2:
    st.metric("🎓 BOLSAS", fmt_num(total_bolsas))
with col3:
    st.metric("👥 PESQUISADORES", fmt_num(n_pesq))
with col4:
    st.metric("🎫 TICKET MÉDIO", fmt_brl(ticket_medio))

st.markdown("## 🔍 Insights Automáticos")
if "regiao_nome" in df_filtrado.columns:
    reg_share = df_filtrado.groupby("regiao_nome")["valor_pago"].sum()
    top_reg = reg_share.idxmax()
    pct_reg = (reg_share.max() / total_volume) * 100
    st.info(f"📍 Região líder: **{top_reg}** com **{pct_reg:.1f}%** dos recursos.")

if "grande_area" in df_filtrado.columns:
    area_share = df_filtrado.groupby("grande_area")["valor_pago"].sum()
    top_area = area_share.idxmax()
    pct_area = (area_share.max() / total_volume) * 100
    st.info(f"🧬 Área predominante: **{top_area}** concentra **{pct_area:.1f}%** dos investimentos.")

if len(evolucao_ano) >= 3:
    cresc_anual = (evolucao_ano.iloc[-1] / evolucao_ano.iloc[-2] - 1) * 100
    st.info(f"📈 Variação anual: {cresc_anual:+.1f}% no último ano.")

# Gráfico de barras regional com dados reais
if "regiao_nome" in df_filtrado.columns:
    st.markdown("## 🗺️ Distribuição Regional do Investimento")
    reg_data = df_filtrado.groupby("regiao_nome")["valor_pago"].sum().reset_index()
    reg_data.columns = ["Região", "Valor"]
    fig_reg = px.bar(reg_data, x="Região", y="Valor", color="Valor",
                     color_continuous_scale="Blues", text=reg_data["Valor"].apply(lambda x: fmt_brl(x)),
                     title="Investimento por Região")
    fig_reg.update_traces(textposition="outside")
    fig_reg.update_layout(template="plotly_dark", height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_reg, use_container_width=True)

# Ranking pesquisadores
if "beneficiario" in df_filtrado.columns:
    st.markdown("## 🏆 Top 10 Pesquisadores")
    top_people = df_filtrado.groupby("beneficiario")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
    top_people.columns = ["Pesquisador", "Total"]
    top_people["Total"] = top_people["Total"].apply(fmt_brl)
    st.dataframe(top_people, use_container_width=True, hide_index=True)

# Rodapé
st.markdown("---")
st.markdown("""
<div class="footer">
    🔬 CNPq Analytics · Fonte: Portal Brasileiro de Dados Abertos (CGU/CNPq)<br>
    Dashboard desenvolvido para portfólio de Análise de Dados.
</div>
""", unsafe_allow_html=True)
