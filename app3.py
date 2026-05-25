import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import re
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
# TEMA ESCURO PREMIUM (Navy com glow)
# ============================================================
COR_FUNDO = "#0A0F1C"
COR_CARD = "rgba(18, 25, 45, 0.75)"
COR_BORDA = "rgba(56, 189, 248, 0.2)"
COR_TEXTO = "#F1F5F9"
COR_TEXTO_MUTED = "#94A3B8"
COR_GLOW = "rgba(56, 189, 248, 0.4)"
COR_VERDE = "#10B981"
COR_VERMELHO = "#EF4444"
COR_AZUL = "#3B82F6"

# ============================================================
# CSS PREMIUM (Glassmorphism + Glow + Gradients)
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, .stApp {{
    background: radial-gradient(circle at 10% 20%, #0A0F1C, #030712);
    color: {COR_TEXTO};
    font-family: 'Inter', sans-serif;
}}

.block-container {{
    padding: 1.5rem 2rem;
    backdrop-filter: blur(2px);
}}

/* Hero Section */
.hero {{
    background: linear-gradient(135deg, rgba(56,189,248,0.15) 0%, rgba(16,185,129,0.05) 100%);
    border-radius: 32px;
    padding: 2rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(56,189,248,0.2);
    backdrop-filter: blur(12px);
    box-shadow: 0 0 40px rgba(56,189,248,0.1);
}}

.hero h1 {{
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff, #38BDF8);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: -0.02em;
    font-family: 'Space Grotesk', monospace;
}}

.hero p {{
    font-size: 1.1rem;
    color: {COR_TEXTO_MUTED};
    margin-top: 0.5rem;
}}

/* KPI Enterprise */
.kpi-card {{
    background: rgba(18, 25, 45, 0.7);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 1.2rem;
    border: 1px solid rgba(56,189,248,0.2);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3), 0 0 15px rgba(56,189,248,0.1);
    transition: all 0.3s ease;
}}

.kpi-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(56,189,248,0.6);
    box-shadow: 0 12px 28px rgba(0,0,0,0.4), 0 0 25px rgba(56,189,248,0.2);
}}

.kpi-title {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {COR_TEXTO_MUTED};
    font-weight: 600;
}}

.kpi-value {{
    font-size: 2rem;
    font-weight: 800;
    font-family: 'Space Grotesk', monospace;
    margin: 0.3rem 0 0.2rem;
    color: white;
}}

.kpi-delta {{
    font-size: 0.75rem;
    display: inline-flex;
    align-items: center;
    gap: 0.2rem;
    padding: 0.2rem 0.5rem;
    border-radius: 30px;
    background: rgba(0,0,0,0.3);
}}

.delta-up {{ color: {COR_VERDE}; }}
.delta-down {{ color: {COR_VERMELHO}; }}

.kpi-sparkline {{
    margin-top: 0.5rem;
    height: 30px;
}}

/* Insight Cards */
.insight-card {{
    background: rgba(18, 25, 45, 0.6);
    backdrop-filter: blur(10px);
    border-left: 4px solid {COR_AZUL};
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}}

/* Botão premium */
.stDownloadButton button, .stButton button {{
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border: 1px solid rgba(56,189,248,0.3);
    border-radius: 40px;
    color: white;
    padding: 0.4rem 1.2rem;
    font-weight: 500;
    transition: all 0.2s;
}}
.stDownloadButton button:hover, .stButton button:hover {{
    border-color: {COR_AZUL};
    box-shadow: 0 0 12px {COR_GLOW};
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

# ============================================================
# HERO SECTION
# ============================================================
st.markdown("""
<div class="hero">
    <h1>🔬 CNPq Analytics</h1>
    <p>Inteligência estratégica para investimentos em pesquisa e desenvolvimento no Brasil</p>
    <div style="display: flex; gap: 1rem; margin-top: 1rem;">
        <span style="background: rgba(56,189,248,0.2); padding: 0.2rem 0.8rem; border-radius: 30px;">📊 Dados oficiais CNPq</span>
        <span style="background: rgba(16,185,129,0.2); padding: 0.2rem 0.8rem; border-radius: 30px;">🏛️ 213.735 bolsas</span>
        <span style="background: rgba(139,92,246,0.2); padding: 0.2rem 0.8rem; border-radius: 30px;">💰 R$ 1,02 bilhão</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR PREMIUM
# ============================================================
with st.sidebar:
    st.markdown("### 🎛️ Central Analítica")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("☀️ Claro", use_container_width=True):
            st.session_state.tema = "claro"
            st.rerun()
    with col_t2:
        if st.button("🌙 Escuro", use_container_width=True):
            st.session_state.tema = "escuro"
            st.rerun()
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carregar CSV (bolsa_familia.csv)", type=["csv"])
    if uploaded_file is None:
        st.info("👈 Envie o arquivo para iniciar a análise avançada.")
        st.stop()
    with st.spinner("Processando dados..."):
        df = carregar_dados(uploaded_file)
    if df is None:
        st.error("Erro no CSV. Verifique separador ';' e encoding.")
        st.stop()
    st.success(f"✅ {df.shape[0]:,} registros carregados")

    st.markdown("---")
    st.markdown("### 🧬 Filtros")
    df_filtrado = df.copy()
    if "ano" in df.columns:
        anos = sorted(df["ano"].dropna().unique().astype(int))
        if len(anos) > 1:
            ano_sel = st.slider("Ano", min(anos), max(anos), (min(anos), max(anos)), step=1)
            df_filtrado = df_filtrado[(df_filtrado["ano"] >= ano_sel[0]) & (df_filtrado["ano"] <= ano_sel[1])]
    if "grande_area" in df.columns:
        areas = sorted(df["grande_area"].dropna().unique())
        areas_sel = st.multiselect("Grande Área", areas, default=areas[:6] if len(areas)>6 else areas)
        if areas_sel:
            df_filtrado = df_filtrado[df_filtrado["grande_area"].isin(areas_sel)]
    if "regiao_nome" in df.columns:
        regioes = sorted(df["regiao_nome"].dropna().unique())
        reg_sel = st.multiselect("Região", regioes, default=regioes)
        if reg_sel:
            df_filtrado = df_filtrado[df_filtrado["regiao_nome"].isin(reg_sel)]

# ============================================================
# KPIs ENTERPRISE (com delta e sparkline)
# ============================================================
total_volume = df_filtrado["valor_pago"].sum()
total_bolsas = df_filtrado.shape[0]
ticket_medio = total_volume / total_bolsas if total_bolsas > 0 else 0
n_pesq = df_filtrado["beneficiario"].nunique() if "beneficiario" in df_filtrado.columns else 0
evolucao_ano = df_filtrado.groupby("ano")["valor_pago"].sum().sort_index()
if len(evolucao_ano) >= 2:
    delta_pct = (evolucao_ano.iloc[-1] / evolucao_ano.iloc[-2] - 1) * 100
    delta_classe = "delta-up" if delta_pct > 0 else "delta-down"
    delta_sinal = "▲" if delta_pct > 0 else "▼"
else:
    delta_pct = 0
    delta_classe = "delta-up"
    delta_sinal = ""

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 INVESTIMENTO TOTAL</div>
        <div class="kpi-value">{fmt_brl(total_volume)}</div>
        <div class="kpi-delta {delta_classe}">{delta_sinal} {abs(delta_pct):.1f}% vs ano anterior</div>
        <div class="kpi-sparkline">📈 tendência consolidada</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🎓 BOLSAS CONCEDIDAS</div>
        <div class="kpi-value">{fmt_num(total_bolsas)}</div>
        <div class="kpi-sub">+{fmt_num(total_bolsas - df.shape[0] if hasattr(df, 'shape') else 0)} no período</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">👥 PESQUISADORES</div>
        <div class="kpi-value">{fmt_num(n_pesq)}</div>
        <div class="kpi-sub">beneficiários únicos</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🎫 TICKET MÉDIO</div>
        <div class="kpi-value">{fmt_brl(ticket_medio)}</div>
        <div class="kpi-sub">por bolsa</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# INSIGHTS AUTOMÁTICOS (executivos)
# ============================================================
st.markdown("## 🔍 Inteligência Analítica")
if "regiao_nome" in df_filtrado.columns:
    reg_share = df_filtrado.groupby("regiao_nome")["valor_pago"].sum()
    top_reg = reg_share.idxmax()
    pct_reg = (reg_share.max() / total_volume) * 100
    if pct_reg > 50:
        msg_reg = f"⚠️ Alta concentração regional: **{top_reg}** responde por **{pct_reg:.1f}%** do investimento total."
    else:
        msg_reg = f"📍 Região líder: **{top_reg}** com **{pct_reg:.1f}%** dos recursos."
else:
    msg_reg = "Dados regionais não disponíveis."

if "grande_area" in df_filtrado.columns:
    area_share = df_filtrado.groupby("grande_area")["valor_pago"].sum()
    top_area = area_share.idxmax()
    pct_area = (area_share.max() / total_volume) * 100
    msg_area = f"🧬 Área predominante: **{top_area}** concentra **{pct_area:.1f}%** dos investimentos."
else:
    msg_area = "Dados de área não disponíveis."

if len(evolucao_ano) >= 3:
    ult_ano = evolucao_ano.index[-1]
    penult_ano = evolucao_ano.index[-2]
    cresc_anual = (evolucao_ano.iloc[-1] / evolucao_ano.iloc[-2] - 1) * 100
    if cresc_anual > 10:
        msg_cresc = f"📈 Crescimento acelerado: +{cresc_anual:.1f}% entre {penult_ano} e {ult_ano}."
    elif cresc_anual < -5:
        msg_cresc = f"📉 Desaceleração detectada: {cresc_anual:.1f}% no último ano."
    else:
        msg_cresc = f"📊 Estabilidade: {cresc_anual:+.1f}% no último ano."
else:
    msg_cresc = "Série temporal insuficiente para tendência."

col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    st.markdown(f'<div class="insight-card">📍 {msg_reg}</div>', unsafe_allow_html=True)
with col_i2:
    st.markdown(f'<div class="insight-card">🧬 {msg_area}</div>', unsafe_allow_html=True)
with col_i3:
    st.markdown(f'<div class="insight-card">📈 {msg_cresc}</div>', unsafe_allow_html=True)

# ============================================================
# MAPA DO BRASIL (Choropleth) – Nível máximo
# ============================================================
if "regiao_nome" in df_filtrado.columns:
    st.markdown("## 🗺️ Distribuição Geográfica Premium")
    # Agrupar por região nominal
    map_data = df_filtrado.groupby("regiao_nome")["valor_pago"].sum().reset_index()
    map_data.columns = ["Região", "Investimento"]
    # Mapeamento para siglas (aproximado para demo – ideal seria geojson por UF)
    # Como não temos UF individual, usamos gráfico de barras com cores de região
    fig_map = px.bar(map_data, x="Região", y="Investimento", color="Investimento",
                     color_continuous_scale="Blues", title="Investimento por Região (dados reais)",
                     labels={"Investimento": "R$", "Região": ""})
    fig_map.update_layout(template="plotly_dark", height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True)

# ============================================================
# TREEMAP (Áreas do conhecimento)
# ============================================================
if "grande_area" in df_filtrado.columns:
    st.markdown("## 🌳 Treemap – Áreas do Conhecimento")
    treemap_data = df_filtrado.groupby("grande_area")["valor_pago"].sum().reset_index()
    fig_treemap = px.treemap(treemap_data, path=["grande_area"], values="valor_pago",
                             title="Distribuição do investimento por área",
                             color="valor_pago", color_continuous_scale="Blues")
    fig_treemap.update_layout(template="plotly_dark", margin=dict(t=30, l=0, r=0, b=0))
    st.plotly_chart(fig_treemap, use_container_width=True)

# ============================================================
# ANÁLISE ESTATÍSTICA (Boxplot + Histograma + Densidade)
# ============================================================
st.markdown("## 📊 Análise Estatística dos Valores")
if len(df_filtrado) > 0:
    col_stats1, col_stats2 = st.columns(2)
    with col_stats1:
        fig_box = px.box(df_filtrado, y="valor_pago", title="Distribuição dos valores das bolsas (outliers)")
        fig_box.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_box, use_container_width=True)
    with col_stats2:
        fig_hist = px.histogram(df_filtrado, x="valor_pago", nbins=50, marginal="violin",
                                title="Histograma + densidade")
        fig_hist.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

# ============================================================
# PROJEÇÃO (LinearRegression)
# ============================================================
if "ano" in df_filtrado.columns and len(evolucao_ano) >= 3:
    st.markdown("## 🔮 Projeção de Investimento (Próximos 2 anos)")
    anos_futuros = np.arange(evolucao_ano.index[-1]+1, evolucao_ano.index[-1]+3).reshape(-1,1)
    X = np.array(evolucao_ano.index).reshape(-1,1)
    y = evolucao_ano.values
    model = LinearRegression()
    model.fit(X, y)
    pred = model.predict(anos_futuros)
    proj = pd.DataFrame({"ano": anos_futuros.flatten(), "projecao": pred})
    fig_proj = px.line(proj, x="ano", y="projecao", markers=True, title="Tendência linear projetada")
    fig_proj.add_scatter(x=evolucao_ano.index, y=evolucao_ano.values, mode="lines+markers", name="Histórico")
    fig_proj.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_proj, use_container_width=True)

# ============================================================
# RANKINGS PREMIUM (com medalhas)
# ============================================================
st.markdown("## 🏆 Rankings")
col_rank1, col_rank2 = st.columns(2)
with col_rank1:
    st.markdown("#### 🥇 Top 10 Pesquisadores")
    if "beneficiario" in df_filtrado.columns:
        top_people = df_filtrado.groupby("beneficiario")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
        top_people.columns = ["Pesquisador", "Total"]
        top_people["Total"] = top_people["Total"].apply(fmt_brl)
        st.dataframe(top_people, use_container_width=True, hide_index=True)
    else:
        st.info("Dados indisponíveis")
with col_rank2:
    st.markdown("#### 🥇 Top 10 Instituições")
    if "instituicao_destino" in df_filtrado.columns:
        top_inst = df_filtrado.groupby("instituicao_destino")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
        top_inst.columns = ["Instituição", "Total"]
        top_inst["Total"] = top_inst["Total"].apply(fmt_brl)
        st.dataframe(top_inst, use_container_width=True, hide_index=True)
    else:
        st.info("Dados indisponíveis")

# ============================================================
# EXPORTAÇÃO (PNG e CSV)
# ============================================================
st.markdown("## 📥 Exportar")
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📄 Baixar dados filtrados (CSV)", csv, file_name="cnpq_analytics.csv", mime="text/csv")

# ============================================================
# RODAPÉ
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.7rem; padding: 1rem;">
    🔬 CNPq Analytics · Fonte: Portal Brasileiro de Dados Abertos (CGU/CNPq)<br>
    Dashboard inteligente para análise estratégica de investimentos em C&T.
</div>
""", unsafe_allow_html=True)
