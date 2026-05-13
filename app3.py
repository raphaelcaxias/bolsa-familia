import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="CNPq Analytics · Bolsas de Pesquisa",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS — Design System Refinado
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── BASE ─────────────────────────────────────────── */
html, body, .stApp {
    background: #07080d !important;
    color: #f0f4ff !important;
    font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── BLOCK CONTAINER ──────────────────────────────── */
.block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1600px !important;
}

/* ── SIDEBAR ──────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0e1018 !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.25rem;
}

section[data-testid="stSidebar"] * {
    color: #f0f4ff !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── SIDEBAR LOGO ─────────────────────────────────── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.sidebar-logo-text {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 18px;
    color: #63d4ff !important;
    letter-spacing: -0.5px;
}

.sidebar-subtitle {
    font-size: 11px;
    color: #6b7898 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 20px;
}

/* ── HEADER ───────────────────────────────────────── */
.page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding-bottom: 20px;
    margin-bottom: 28px;
}

.page-header-left h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 34px !important;
    font-weight: 800 !important;
    color: #f0f4ff !important;
    letter-spacing: -1px;
    margin: 0 0 4px 0 !important;
    line-height: 1 !important;
}

.page-header-left p {
    color: #6b7898;
    font-size: 14px;
    margin: 0;
}

.page-header-right {
    text-align: right;
    font-size: 12px;
    color: #3d4560;
    line-height: 1.6;
}

.badge {
    display: inline-block;
    background: rgba(99,212,255,0.1);
    border: 1px solid rgba(99,212,255,0.2);
    color: #63d4ff;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── KPI CARDS ────────────────────────────────────── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}

.kpi-card {
    background: #141620;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px 22px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s;
}

.kpi-card:hover {
    border-color: rgba(99,212,255,0.25);
    transform: translateY(-3px);
}

.kpi-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #6b7898;
    font-weight: 600;
    margin-bottom: 12px;
}

.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #f0f4ff;
    line-height: 1;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.kpi-sub {
    font-size: 12px;
    color: #6b7898;
}

.kpi-icon {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 28px;
    opacity: 0.15;
}

/* ── SECTION HEADERS ──────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 32px 0 16px 0;
}

.section-header h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #f0f4ff !important;
    margin: 0 !important;
    letter-spacing: -0.3px;
}

.section-tag {
    font-size: 11px;
    color: #6b7898;
    border: 1px solid rgba(255,255,255,0.07);
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── CHART CARD ───────────────────────────────────── */
.chart-card {
    background: #141620;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 24px;
    padding: 24px;
}

/* ── INSIGHT CARDS ────────────────────────────────── */
.insight-wrap {
    display: flex;
    flex-direction: column;
    gap: 12px;
    height: 100%;
}

.insight-card {
    background: #141620;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    flex: 1;
}

.insight-card::after {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: #63d4ff;
    border-radius: 4px 0 0 4px;
}

.insight-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #f0f4ff;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.insight-body {
    font-size: 13px;
    color: #6b7898;
    line-height: 1.6;
}

.insight-body b {
    color: #f0f4ff;
    font-weight: 600;
}

.highlight-positive { color: #34d399 !important; }
.highlight-negative { color: #f87171 !important; }

/* ── FILTER LABEL ─────────────────────────────────── */
.filter-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6b7898;
    margin-bottom: 4px;
    margin-top: 14px;
    font-weight: 600;
}

/* ── STATUS BAR ───────────────────────────────────── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(52,211,153,0.07);
    border: 1px solid rgba(52,211,153,0.2);
    padding: 10px 16px;
    border-radius: 10px;
    margin: 0 0 24px 0;
    font-size: 13px;
    color: #34d399;
}

.filter-info {
    background: rgba(251,191,36,0.07);
    border: 1px solid rgba(251,191,36,0.2);
    padding: 10px 16px;
    border-radius: 10px;
    font-size: 13px;
    color: #fbbf24;
    margin-bottom: 20px;
}

/* ── EXPORT SECTION ───────────────────────────────── */
.export-card {
    background: #141620;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 22px;
    text-align: center;
}

.export-title {
    font-size: 13px;
    font-weight: 600;
    color: #6b7898;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
}

.stDownloadButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #63d4ff, #818cf8) !important;
    color: #07080d !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 12px !important;
    letter-spacing: 0.3px;
    transition: opacity 0.2s !important;
}

.stDownloadButton > button:hover {
    opacity: 0.85 !important;
}

/* ── EMPTY STATE ──────────────────────────────────── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 80px 40px;
    background: #141620;
    border: 1px dashed rgba(255,255,255,0.07);
    border-radius: 24px;
    margin: 32px 0;
}

.empty-state-icon {
    font-size: 64px;
    opacity: 0.4;
    margin-bottom: 20px;
}

.empty-state h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #f0f4ff !important;
    margin-bottom: 10px !important;
}

.empty-state p {
    color: #6b7898;
    font-size: 15px;
    max-width: 400px;
    line-height: 1.7;
}

.feature-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 28px;
    max-width: 500px;
}

.feature-item {
    background: #07080d;
    border: 1px solid rgba(255,255,255,0.07);
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 13px;
    color: #6b7898;
    text-align: left;
}

.feature-item b {
    display: block;
    color: #f0f4ff;
    font-size: 13px;
    margin-bottom: 2px;
}

/* ── ERROR STATE ──────────────────────────────────── */
.error-state {
    background: rgba(248,113,113,0.06);
    border: 1px solid rgba(248,113,113,0.2);
    border-radius: 16px;
    padding: 24px;
    color: #fca5a5;
    font-size: 14px;
}

/* ── FOOTER ───────────────────────────────────────── */
.page-footer {
    text-align: center;
    padding: 32px 0 16px;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin-top: 40px;
    color: #3d4560;
    font-size: 12px;
    letter-spacing: 0.5px;
}

/* ── STREAMLIT OVERRIDES ──────────────────────────── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; }

.stMultiSelect [data-baseweb="select"] {
    background: #141620 !important;
    border-color: rgba(255,255,255,0.07) !important;
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07);
}

div[data-testid="column"] { gap: 16px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTES
# ============================================================
REGIOES_MAP = {
    'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste',
    'CO': 'Centro-Oeste', 'N':  'Norte', 'NO': 'Norte',
    'EX': 'Exterior',    'NI': 'Não Informado'
}

PLOTLY_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#6b7898", size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    hoverlabel=dict(
        bgcolor="#141620",
        bordercolor="rgba(99,212,255,0.3)",
        font_color="#f0f4ff",
        font_size=13
    )
)

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================
def fmt_brl(valor):
    """Formata valor em reais brasileiro."""
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.2f}B".replace(".", ",")
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_num(n):
    """Formata número inteiro com separador de milhar."""
    if pd.isna(n):
        return "—"
    return f"{int(n):,}".replace(",", ".")

@st.cache_data(show_spinner=False)
def carregar_dados(uploaded_file):
    """Lê CSV com detecção automática de encoding e separador."""
    encodings = ['latin1', 'utf-8', 'ISO-8859-1', 'cp1252']
    separadores = [';', ',']

    for enc in encodings:
        for sep in separadores:
            try:
                uploaded_file.seek(0)
                probe = pd.read_csv(uploaded_file, delimiter=sep, encoding=enc, nrows=5)
                if 5 < len(probe.columns) < 60:
                    uploaded_file.seek(0)
                    df = pd.read_csv(
                        uploaded_file, delimiter=sep,
                        encoding=enc, low_memory=False
                    )
                    df.columns = df.columns.str.strip().str.lower()

                    # ── valor_pago ──
                    if 'valor_pago' in df.columns:
                        df['valor_pago'] = (
                            df['valor_pago']
                            .astype(str)
                            .str.replace(',', '.', regex=False)
                            .str.extract(r'(\d+\.?\d*)', expand=False)
                        )
                        df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')

                    df = df.dropna(subset=['valor_pago'])
                    df = df[df['valor_pago'] > 0]

                    # ── datas ──
                    for col in ['data_inicio_processo', 'data_inicio', 'data']:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                            df['ano'] = df[col].dt.year.astype('Int64')
                            break

                    # ── regiões ──
                    if 'regiao' in df.columns:
                        df['regiao_nome'] = df['regiao'].map(REGIOES_MAP).fillna(df['regiao'])

                    return df
            except Exception:
                continue

    return None

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span style="font-size:22px">🔬</span>
        <span class="sidebar-logo-text">CNPq Analytics</span>
    </div>
    <div class="sidebar-subtitle">Painel de Investimentos em C&T</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Carregar arquivo CSV",
        type=["csv"],
        help="Formato: bolsas_cnpq.csv — separador ; ou , — encoding latin1/utf-8"
    )

    st.markdown("""
    <div style="margin-top:10px; padding:12px 14px; background:rgba(99,212,255,0.05);
         border:1px solid rgba(99,212,255,0.12); border-radius:10px; font-size:12px; color:#6b7898;">
        📥 Não tem o CSV?<br>
        <a href="https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub"
           target="_blank" style="color:#63d4ff; text-decoration:none; font-weight:600;">
           Baixar do Google Drive →</a>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Placeholder para filtros
    filtros_placeholder = st.empty()

# ============================================================
# HEADER DA PÁGINA
# ============================================================
st.markdown(f"""
<div class="page-header">
    <div class="page-header-left">
        <h1>Bolsas de Pesquisa · CNPq</h1>
        <p>Análise estratégica de investimentos em ciência e tecnologia no Brasil</p>
    </div>
    <div class="page-header-right">
        <span class="badge">Dashboard</span><br><br>
        Atualizado em {datetime.now().strftime('%d %b %Y  %H:%M')}
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================
if uploaded_file is not None:
    with st.spinner("Carregando dados…"):
        df = carregar_dados(uploaded_file)

    if df is None or df.empty:
        st.markdown("""
        <div class="error-state">
            <b>❌ Não foi possível ler o arquivo.</b><br>
            Verifique se é um CSV válido com separador <code>;</code> ou <code>,</code>
            e encoding latin1 / UTF-8.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── FILTROS NA SIDEBAR ─────────────────────────────────
    df_filtrado = df.copy()

    with filtros_placeholder.container():
        st.markdown('<div class="filter-label">Região</div>', unsafe_allow_html=True)
        if 'regiao_nome' in df.columns:
            regioes = sorted(df['regiao_nome'].dropna().unique())
            sel_regioes = st.multiselect("Região", regioes, default=regioes, label_visibility="collapsed")
            if sel_regioes:
                df_filtrado = df_filtrado[df_filtrado['regiao_nome'].isin(sel_regioes)]

        if 'ano' in df.columns:
            anos_validos = sorted(df['ano'].dropna().unique().astype(int))
            if len(anos_validos) > 1:
                st.markdown('<div class="filter-label">Período</div>', unsafe_allow_html=True)
                ano_min, ano_max = int(min(anos_validos)), int(max(anos_validos))
                sel_anos = st.slider("Período", ano_min, ano_max, (ano_min, ano_max), label_visibility="collapsed")
                df_filtrado = df_filtrado[
                    (df_filtrado['ano'] >= sel_anos[0]) &
                    (df_filtrado['ano'] <= sel_anos[1])
                ]

        if 'grande_area' in df.columns:
            areas = sorted(df['grande_area'].dropna().unique())
            st.markdown('<div class="filter-label">Grande Área</div>', unsafe_allow_html=True)
            default_areas = areas[:6] if len(areas) > 6 else areas
            sel_areas = st.multiselect("Grande Área", areas, default=default_areas, label_visibility="collapsed")
            if sel_areas:
                df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(sel_areas)]

        if 'modalidade' in df.columns:
            modalidades = sorted(df['modalidade'].dropna().unique())
            st.markdown('<div class="filter-label">Modalidade</div>', unsafe_allow_html=True)
            sel_mod = st.multiselect("Modalidade", modalidades, default=modalidades[:5] if len(modalidades) > 5 else modalidades, label_visibility="collapsed")
            if sel_mod:
                df_filtrado = df_filtrado[df_filtrado['modalidade'].isin(sel_mod)]

    # ── STATUS BAR ─────────────────────────────────────────
    total_r = df_filtrado.shape[0]
    total_o = df.shape[0]
    pct = 100 * total_r / total_o if total_o > 0 else 0

    if total_r < total_o:
        st.markdown(f"""
        <div class="filter-info">
            🔍 Filtros ativos — exibindo <b>{fmt_num(total_r)}</b> de <b>{fmt_num(total_o)}</b> registros ({pct:.1f}%)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-bar">
            ✓ <b>{fmt_num(total_r)}</b> registros carregados com sucesso
        </div>
        """, unsafe_allow_html=True)

    # ── KPIs ───────────────────────────────────────────────
    total_val   = df_filtrado['valor_pago'].sum()
    media_val   = df_filtrado['valor_pago'].mean()
    n_pesq      = df_filtrado['beneficiario'].nunique()      if 'beneficiario' in df_filtrado.columns else 0
    n_inst      = df_filtrado['instituicao_destino'].nunique() if 'instituicao_destino' in df_filtrado.columns else 0

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card" style="border-top:2px solid #63d4ff">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Investimento Total</div>
            <div class="kpi-value">{fmt_brl(total_val)}</div>
            <div class="kpi-sub">valor pago consolidado</div>
        </div>
        <div class="kpi-card" style="border-top:2px solid #818cf8">
            <div class="kpi-icon">🎓</div>
            <div class="kpi-label">Pesquisadores</div>
            <div class="kpi-value">{fmt_num(n_pesq)}</div>
            <div class="kpi-sub">beneficiários únicos</div>
        </div>
        <div class="kpi-card" style="border-top:2px solid #34d399">
            <div class="kpi-icon">🏛️</div>
            <div class="kpi-label">Instituições</div>
            <div class="kpi-value">{fmt_num(n_inst)}</div>
            <div class="kpi-sub">instituições de destino</div>
        </div>
        <div class="kpi-card" style="border-top:2px solid #fbbf24">
            <div class="kpi-icon">📊</div>
            <div class="kpi-label">Ticket Médio</div>
            <div class="kpi-value">{fmt_brl(media_val)}</div>
            <div class="kpi-sub">por bolsa concedida</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SEÇÃO 1: INVESTIMENTO POR ÁREA + INSIGHTS ──────────
    st.markdown("""
    <div class="section-header">
        <h2>Investimento por Grande Área</h2>
        <span class="section-tag">Top 10</span>
    </div>
    """, unsafe_allow_html=True)

    col_chart, col_insights = st.columns([1.8, 1], gap="large")

    with col_chart:
        if 'grande_area' in df_filtrado.columns:
            area_data = (
                df_filtrado.groupby('grande_area')['valor_pago']
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            area_data.columns = ['Área', 'Valor']

            fig = go.Figure(go.Bar(
                x=area_data['Área'],
                y=area_data['Valor'],
                marker=dict(
                    color=area_data['Valor'],
                    colorscale=[[0, '#818cf8'], [0.5, '#63d4ff'], [1, '#34d399']],
                    line=dict(width=0)
                ),
                hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
                customdata=[fmt_brl(v) for v in area_data['Valor']],
                opacity=0.9
            ))

            fig.update_layout(
                **PLOTLY_BASE,
                height=440,
                xaxis=dict(tickangle=-35, tickfont=dict(size=11), gridcolor='rgba(255,255,255,0.04)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickformat=',.0f'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna `grande_area` não encontrada no CSV.")

    with col_insights:
        insights = []

        # Concentração regional
        if 'regiao_nome' in df_filtrado.columns and total_val > 0:
            inv_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
            if len(inv_reg) > 0:
                top_reg  = inv_reg.idxmax()
                pct_reg  = 100 * inv_reg.max() / total_val
                insights.append(f"""
                <div class="insight-card">
                    <div class="insight-title">📍 Concentração Regional</div>
                    <div class="insight-body">
                        A região <b>{top_reg}</b> concentra <b>{pct_reg:.1f}%</b>
                        do total investido no período selecionado.
                    </div>
                </div>""")

        # Variação anual
        if 'ano' in df_filtrado.columns:
            inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum().dropna()
            inv_ano = inv_ano[inv_ano.index.notna()].sort_index()
            if len(inv_ano) >= 2:
                v_ant, v_ult = inv_ano.iloc[-2], inv_ano.iloc[-1]
                if v_ant > 0:
                    var = 100 * (v_ult - v_ant) / v_ant
                    cor_cls = "highlight-positive" if var > 0 else "highlight-negative"
                    sinal   = "▲" if var > 0 else "▼"
                    insights.append(f"""
                    <div class="insight-card">
                        <div class="insight-title">📈 Variação Anual</div>
                        <div class="insight-body">
                            De <b>{int(inv_ano.index[-2])}</b> para <b>{int(inv_ano.index[-1])}</b>:
                            <span class="{cor_cls}"><b>{sinal} {abs(var):.1f}%</b></span>
                            de variação no investimento.
                        </div>
                    </div>""")

        # Desigualdade regional
        if 'regiao_nome' in df_filtrado.columns:
            inv_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
            inv_reg = inv_reg[inv_reg > 0]
            if len(inv_reg) >= 2:
                razao = inv_reg.max() / inv_reg.min()
                insights.append(f"""
                <div class="insight-card">
                    <div class="insight-title">⚖️ Disparidade Regional</div>
                    <div class="insight-body">
                        A região mais financiada recebe <b>{razao:.1f}×</b>
                        mais recursos do que a menos financiada.
                    </div>
                </div>""")

        # Maior área
        if 'grande_area' in df_filtrado.columns and total_val > 0:
            inv_area = df_filtrado.groupby('grande_area')['valor_pago'].sum()
            if len(inv_area) > 0:
                top_area     = inv_area.idxmax()
                pct_area     = 100 * inv_area.max() / total_val
                insights.append(f"""
                <div class="insight-card">
                    <div class="insight-title">🧬 Área Líder</div>
                    <div class="insight-body">
                        <b>{top_area}</b> é a grande área com maior alocação,
                        representando <b>{pct_area:.1f}%</b> dos recursos.
                    </div>
                </div>""")

        if insights:
            st.markdown('<div class="insight-wrap">' + "".join(insights) + '</div>', unsafe_allow_html=True)
        else:
            st.info("Insights serão exibidos conforme os dados disponíveis.")

    # ── SEÇÃO 2: EVOLUÇÃO TEMPORAL ─────────────────────────
    if 'ano' in df_filtrado.columns:
        inv_ano = (
            df_filtrado.groupby('ano')['valor_pago']
            .agg(['sum', 'count', 'mean'])
            .reset_index()
            .rename(columns={'sum': 'Total', 'count': 'Bolsas', 'mean': 'Média'})
            .dropna(subset=['ano'])
        )
        inv_ano = inv_ano[inv_ano['ano'].notna()]

        if len(inv_ano) > 1:
            st.markdown("""
            <div class="section-header">
                <h2>Evolução Temporal do Investimento</h2>
                <span class="section-tag">Série Histórica</span>
            </div>
            """, unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["💰 Valor Total", "🎓 Número de Bolsas"])

            with tab1:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=inv_ano['ano'], y=inv_ano['Total'],
                    mode='lines+markers',
                    line=dict(width=3, color='#63d4ff'),
                    marker=dict(size=8, color='#63d4ff',
                                line=dict(width=2, color='#07080d')),
                    fill='tozeroy',
                    fillcolor='rgba(99,212,255,0.06)',
                    hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
                    customdata=[fmt_brl(v) for v in inv_ano['Total']]
                ))
                fig2.update_layout(
                    **PLOTLY_BASE, height=360,
                    xaxis=dict(dtick=1, gridcolor='rgba(255,255,255,0.04)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickformat=',.0f')
                )
                st.plotly_chart(fig2, use_container_width=True)

            with tab2:
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(
                    x=inv_ano['ano'], y=inv_ano['Bolsas'],
                    marker_color='#818cf8',
                    hovertemplate="<b>%{x}</b><br>%{y:,} bolsas<extra></extra>"
                ))
                fig3.update_layout(
                    **PLOTLY_BASE, height=360,
                    xaxis=dict(dtick=1, gridcolor='rgba(255,255,255,0.04)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig3, use_container_width=True)

    # ── SEÇÃO 3: DISTRIBUIÇÃO REGIONAL ─────────────────────
    if 'regiao_nome' in df_filtrado.columns:
        reg_data = (
            df_filtrado.groupby('regiao_nome')['valor_pago']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        reg_data.columns = ['Região', 'Valor']

        if len(reg_data) > 0:
            st.markdown("""
            <div class="section-header">
                <h2>Distribuição Regional</h2>
                <span class="section-tag">Proporção</span>
            </div>
            """, unsafe_allow_html=True)

            col_pie, col_bar = st.columns(2, gap="large")

            with col_pie:
                fig4 = px.pie(
                    reg_data, names='Região', values='Valor',
                    color_discrete_sequence=['#63d4ff','#818cf8','#34d399','#fbbf24','#f87171','#a78bfa','#2dd4bf']
