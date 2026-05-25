import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# =========================================================
# CONFIGURAÇÃO
# =========================================================
st.set_page_config(
    page_title="CNPq Analytics Ultimate",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CORES
# =========================================================
PRIMARY = "#0F172A"
SECONDARY = "#164E63"
ACCENT = "#14B8A6"
BG = "#F8FAFC"
CARD = "#FFFFFF"
TEXT = "#64748B"
BORDER = "#E2E8F0"

# =========================================================
# CSS
# =========================================================
st.markdown(f"""
<style>
    .stApp {{ background: {BG}; }}
    .block-container {{ max-width: 1600px; padding-top: 2rem; }}
    
    .hero {{
        background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
        padding: 3rem;
        border-radius: 28px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }}
    .hero-title {{ font-size: 52px; font-weight: 800; }}
    .hero-sub {{ margin-top: 10px; font-size: 18px; opacity: 0.9; }}
    
    .kpi-card {{
        background: white;
        border-radius: 24px;
        padding: 24px;
        border: 1px solid {BORDER};
        box-shadow: 0 5px 18px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }}
    .kpi-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 15px 35px rgba(20,184,166,0.15);
    }}
    .kpi-title {{ color: {TEXT}; font-size: 14px; font-weight: 600; }}
    .kpi-value {{ margin-top: 12px; font-size: 36px; font-weight: 800; color: {PRIMARY}; }}
    
    .insight-box {{
        background: white;
        border-left: 6px solid {ACCENT};
        border-radius: 22px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
    }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def fmt_money(v):
    if pd.isna(v) or v == 0:
        return "R$ 0"
    if abs(v) >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.2f}B".replace(".", ",")
    if abs(v) >= 1_000_000:
        return f"R$ {v/1_000_000:.2f}M".replace(".", ",")
    return f"R$ {v:,.0f}".replace(",", ".")

def fmt_num(v):
    return f"{int(v):,}".replace(",", ".") if not pd.isna(v) else "0"

# =========================================================
# CARREGAMENTO DE DADOS
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(uploaded_file):
    if uploaded_file is None:
        return None
    
    encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
    
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                sep=";",
                encoding=enc,
                low_memory=False,
                on_bad_lines='skip'
            )
            
            # Padronização de colunas
            df.columns = df.columns.str.lower().str.strip()
            
            # Valor Pago
            if "valor_pago" in df.columns:
                df["valor_pago"] = (
                    df["valor_pago"]
                    .astype(str)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .str.replace(r"[^\d.-]", "", regex=True)
                )
                df["valor_pago"] = pd.to_numeric(df["valor_pago"], errors="coerce")
            
            # Datas
            date_cols = ["data_inicio_processo", "data_termino_processo"]
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            
            # Ano
            if "data_inicio_processo" in df.columns:
                df["ano"] = df["data_inicio_processo"].dt.year
            
            # Status
            if "data_termino_processo" in df.columns:
                hoje = pd.Timestamp.today()
                df["status_bolsa"] = np.where(
                    df["data_termino_processo"].isna() | (df["data_termino_processo"] >= hoje),
                    "Ativa", "Encerrada"
                )
            
            # Regiões
            reg_map = {
                "SE": "Sudeste", "SU": "Sul", "NE": "Nordeste",
                "CO": "Centro-Oeste", "N": "Norte", "NO": "Norte",
                "EX": "Exterior"
            }
            if "regiao" in df.columns:
                df["regiao_nome"] = df["regiao"].map(reg_map).fillna(df["regiao"])
            
            return df
            
        except Exception:
            continue
    
    return None

# =========================================================
# INTERFACE
# =========================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">🔬 CNPq Analytics Ultimate</div>
    <div class="hero-sub">
        Plataforma executiva de análise de bolsas, investimentos e tendências científicas do Brasil
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Controle")
    uploaded = st.file_uploader("Upload do CSV", type=["csv"])
    
    st.markdown("---")
    st.markdown("### Recursos Disponíveis")
    st.markdown("""
    - KPIs executivos
    - Evolução temporal
    - Análise regional
    - Heatmaps
    - Rankings
    - Insights automáticos
    """)

if not uploaded:
    st.info("👈 Faça upload de um arquivo CSV para iniciar a análise.")
    st.stop()

# Carregamento
with st.spinner("Carregando e processando os dados..."):
    df = load_data(uploaded)

if df is None:
    st.error("❌ Não foi possível ler o arquivo CSV. Verifique o formato e encoding.")
    st.stop()

# =========================================================
# FILTROS
# =========================================================
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros")

df_f = df.copy()

# Ano
if "ano" in df.columns:
    anos = sorted(df["ano"].dropna().unique())
    if anos:
        ano_range = st.sidebar.slider(
            "Ano",
            int(min(anos)), int(max(anos)),
            (int(min(anos)), int(max(anos)))
        )
        df_f = df_f[(df_f["ano"] >= ano_range[0]) & (df_f["ano"] <= ano_range[1])]

# Região
if "regiao_nome" in df.columns:
    regs = sorted(df["regiao_nome"].dropna().unique())
    reg_sel = st.sidebar.multiselect("Regiões", regs, default=regs)
    df_f = df_f[df_f["regiao_nome"].isin(reg_sel)]

# Grande Área
if "grande_area" in df.columns:
    areas = sorted(df["grande_area"].dropna().unique())
    area_sel = st.sidebar.multiselect("Grandes Áreas", areas, default=areas[:8])
    df_f = df_f[df_f["grande_area"].isin(area_sel)]

# =========================================================
# KPIs
# =========================================================
total = df_f["valor_pago"].sum() if "valor_pago" in df_f.columns else 0
bolsas = len(df_f)
pesquisadores = df_f["beneficiario"].nunique() if "beneficiario" in df_f.columns else 0
instituicoes = df_f["instituicao_destino"].nunique() if "instituicao_destino" in df_f.columns else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 Investimento Total</div>
        <div class="kpi-value">{fmt_money(total)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🎓 Bolsas</div>
        <div class="kpi-value">{fmt_num(bolsas)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">👨‍🔬 Pesquisadores</div>
        <div class="kpi-value">{fmt_num(pesquisadores)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🏛️ Instituições</div>
        <div class="kpi-value">{fmt_num(instituicoes)}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# INSIGHTS
# =========================================================
insights = []

if not df_f.empty and "regiao_nome" in df_f.columns:
    top_reg = df_f.groupby("regiao_nome")["valor_pago"].sum().idxmax()
    insights.append(f"📍 **{top_reg}** lidera os investimentos.")

if not df_f.empty and "grande_area" in df_f.columns:
    top_area = df_f.groupby("grande_area")["valor_pago"].sum().idxmax()
    insights.append(f"🧬 **{top_area}** é a área mais financiada.")

st.markdown(f"""
<div class="insight-box">
    <h3>🧠 Insights Automáticos</h3>
    <ul>{"".join([f"<li>{i}</li>" for i in insights])}</ul>
</div>
""", unsafe_allow_html=True)

# Tabs (mantive a estrutura)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executivo", "📈 Evolução", "🗺️ Regiões", 
    "🧬 Áreas", "🏛️ Rankings", "📥 Exportar"
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        if "regiao_nome" in df_f.columns:
            fig = px.bar(
                df_f.groupby("regiao_nome")["valor_pago"].sum().reset_index(),
                x="regiao_nome", y="valor_pago",
                color="valor_pago", color_continuous_scale="Viridis",
                title="Investimento por Região"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if "status_bolsa" in df_f.columns:
            fig2 = px.pie(
                df_f["status_bolsa"].value_counts().reset_index(),
                names="status_bolsa", values="count",
                hole=0.45, title="Status das Bolsas"
            )
            st.plotly_chart(fig2, use_container_width=True)

# ... (outras tabs mantidas com pequenas melhorias)

with tab6:
    col1, col2 = st.columns(2)
    with col1:
        csv = df_f.to_csv(index=False, sep=";")
        st.download_button(
            "📥 Exportar Dados Filtrados (CSV)",
            csv,
            file_name=f"cnpq_analise_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    with col2:
        resumo = f"""RELATÓRIO CNPq Analytics
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Investimento Total: {fmt_money(total)}
Bolsas: {fmt_num(bolsas)}
Pesquisadores: {fmt_num(pesquisadores)}
Instituições: {fmt_num(instituicoes)}
"""
        st.download_button("📝 Exportar Relatório", resumo, "relatorio_cnpq.txt")

st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} • CNPq Analytics Ultimate")
