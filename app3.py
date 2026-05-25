import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="CNPq Analytics Ultimate",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DESIGN SYSTEM
# =========================================================
PRIMARY = "#0F172A"
SECONDARY = "#164E63"
ACCENT = "#14B8A6"
BG = "#F8FAFC"
CARD = "#FFFFFF"
TEXT = "#64748B"
BORDER = "#E2E8F0"

# =========================================================
# CSS PREMIUM
# =========================================================
st.markdown(f"""
<style>

html, body, [class*="css"] {{
    font-family: 'Segoe UI', sans-serif;
}}

.stApp {{
    background: {BG};
}}

.block-container {{
    max-width: 1600px;
    padding-top: 2rem;
}}

.hero {{
    background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
    padding: 3rem;
    border-radius: 28px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}}

.hero-title {{
    font-size: 52px;
    font-weight: 800;
}}

.hero-sub {{
    margin-top: 10px;
    font-size: 18px;
    opacity: 0.9;
}}

.kpi-card {{
    background: white;
    border-radius: 24px;
    padding: 24px;
    border: 1px solid {BORDER};
    box-shadow: 0 5px 18px rgba(0,0,0,0.05);
    transition: 0.3s;
}}

.kpi-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 15px 35px rgba(20,184,166,0.15);
}}

.kpi-title {{
    color: {TEXT};
    font-size: 14px;
    font-weight: 600;
}}

.kpi-value {{
    margin-top: 12px;
    font-size: 36px;
    font-weight: 800;
    color: {PRIMARY};
}}

.insight-box {{
    background: white;
    border-left: 6px solid {ACCENT};
    border-radius: 22px;
    padding: 24px;
    margin-top: 20px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.05);
}}

.footer {{
    margin-top: 60px;
    text-align: center;
    color: {TEXT};
    padding: 30px;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {PRIMARY}, #1E293B);
}}

section[data-testid="stSidebar"] * {{
    color: white !important;
}}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def fmt_money(v):

    if pd.isna(v):
        return "R$ 0"

    if abs(v) >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.2f}B".replace(".", ",")

    if abs(v) >= 1_000_000:
        return f"R$ {v/1_000_000:.2f}M".replace(".", ",")

    return f"R$ {v:,.0f}".replace(",", ".")


def fmt_num(v):

    if pd.isna(v):
        return "0"

    return f"{int(v):,}".replace(",", ".")

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(ttl=3600)
def load_data(file):

    encodings = ["utf-8", "latin1", "cp1252"]

    for enc in encodings:

        try:

            file.seek(0)

            df = pd.read_csv(
                file,
                sep=";",
                encoding=enc,
                low_memory=False
            )

            df.columns = (
                df.columns
                .str.lower()
                .str.strip()
            )

            # =================================================
            # VALOR PAGO
            # =================================================
            if "valor_pago" in df.columns:

                df["valor_pago"] = (
                    df["valor_pago"]
                    .astype(str)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )

                df["valor_pago"] = pd.to_numeric(
                    df["valor_pago"],
                    errors="coerce"
                )

            # =================================================
            # DATAS
            # =================================================
            date_cols = [
                "data_inicio_processo",
                "data_termino_processo"
            ]

            for col in date_cols:

                if col in df.columns:

                    df[col] = pd.to_datetime(
                        df[col],
                        errors="coerce",
                        dayfirst=True
                    )

            # =================================================
            # ANO
            # =================================================
            if "data_inicio_processo" in df.columns:

                df["ano"] = (
                    df["data_inicio_processo"]
                    .dt.year
                )

            # =================================================
            # STATUS
            # =================================================
            if "data_termino_processo" in df.columns:

                hoje = pd.Timestamp.today()

                df["status_bolsa"] = np.where(
                    df["data_termino_processo"] >= hoje,
                    "Ativa",
                    "Encerrada"
                )

            # =================================================
            # REGIÕES
            # =================================================
            mapa_regioes = {
                "SE": "Sudeste",
                "SU": "Sul",
                "NE": "Nordeste",
                "CO": "Centro-Oeste",
                "N": "Norte",
                "NO": "Norte",
                "EX": "Exterior"
            }

            if "regiao" in df.columns:

                df["regiao_nome"] = (
                    df["regiao"]
                    .map(mapa_regioes)
                    .fillna(df["regiao"])
                )

            return df

        except Exception:
            continue

    return None

# =========================================================
# HERO
# =========================================================
st.markdown(f"""
<div class="hero">
    <div class="hero-title">
        🔬 CNPq Analytics Ultimate
    </div>

    <div class="hero-sub">
        Plataforma executiva de análise de bolsas, investimentos
        e tendências científicas do Brasil.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.title("⚙️ Controle")

    uploaded = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    st.markdown("---")

    st.markdown("""
### 📊 Recursos

- KPIs executivos
- Heatmaps
- Rankings
- Insights automáticos
- Evolução temporal
- Análise regional
- Exportações
- Storytelling analítico
""")

# =========================================================
# EMPTY STATE
# =========================================================
if not uploaded:

    st.info("👈 Faça upload do CSV para iniciar a análise.")

    st.stop()

# =========================================================
# PROCESSAMENTO
# =========================================================
with st.spinner("Processando dataset..."):

    df = load_data(uploaded)

if df is None:

    st.error("Erro ao carregar o CSV.")

    st.stop()

# =========================================================
# FILTROS
# =========================================================
df_f = df.copy()

with st.sidebar:

    st.markdown("---")

    st.subheader("🔍 Filtros")

    # =====================================================
    # ANO
    # =====================================================
    if "ano" in df.columns:

        anos = sorted(
            df["ano"]
            .dropna()
            .unique()
        )

        if len(anos) > 0:

            ano_range = st.slider(
                "Ano",
                int(min(anos)),
                int(max(anos)),
                (
                    int(min(anos)),
                    int(max(anos))
                )
            )

            df_f = df_f[
                (df_f["ano"] >= ano_range[0]) &
                (df_f["ano"] <= ano_range[1])
            ]

    # =====================================================
    # REGIÕES
    # =====================================================
    if "regiao_nome" in df.columns:

        regs = sorted(
            df["regiao_nome"]
            .dropna()
            .unique()
        )

        reg_sel = st.multiselect(
            "Regiões",
            regs,
            default=regs
        )

        df_f = df_f[
            df_f["regiao_nome"]
            .isin(reg_sel)
        ]

    # =====================================================
    # ÁREAS
    # =====================================================
    if "grande_area" in df.columns:

        areas = sorted(
            df["grande_area"]
            .dropna()
            .unique()
        )

        area_sel = st.multiselect(
            "Grandes Áreas",
            areas,
            default=areas[:6]
        )

        df_f = df_f[
            df_f["grande_area"]
            .isin(area_sel)
        ]

# =========================================================
# KPIS
# =========================================================
total = df_f["valor_pago"].sum()

media = df_f["valor_pago"].mean()

bolsas = len(df_f)

pesquisadores = (
    df_f["beneficiario"].nunique()
    if "beneficiario" in df_f.columns
    else 0
)

instituicoes = (
    df_f["instituicao_destino"].nunique()
    if "instituicao_destino" in df_f.columns
    else 0
)

# =========================================================
# KPI CARDS
# =========================================================
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

if "regiao_nome" in df_f.columns:

    reg_top = (
        df_f.groupby("regiao_nome")["valor_pago"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(reg_top) > 0:

        insights.append(
            f"📍 {reg_top.index[0]} lidera os investimentos científicos."
        )

if "grande_area" in df_f.columns:

    area_top = (
        df_f.groupby("grande_area")["valor_pago"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(area_top) > 0:

        insights.append(
            f"🧬 {area_top.index[0]} é a área mais financiada."
        )

if "ano" in df_f.columns:

    anual = (
        df_f.groupby("ano")["valor_pago"]
        .sum()
        .sort_index()
    )

    if len(anual) >= 2:

        var = (
            (anual.iloc[-1] - anual.iloc[-2]) /
            anual.iloc[-2]
        ) * 100

        insights.append(
            f"📈 O último período apresentou variação de {var:.1f}%."
        )

# =========================================================
# INSIGHT BOX
# =========================================================
st.markdown(
    f"""
<div class="insight-box">

<h3>🧠 Insights Automáticos</h3>

<ul>
{''.join([f'<li>{i}</li>' for i in insights])}
</ul>

</div>
""",
    unsafe_allow_html=True
)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executivo",
    "📈 Evolução",
    "🗺️ Regiões",
    "🧬 Áreas",
    "🏛️ Rankings",
    "📥 Exportações"
])

# =========================================================
# TAB EXECUTIVO
# =========================================================
with tab1:

    col1, col2 = st.columns(2)

    # =====================================================
    # REGIÕES
    # =====================================================
    with col1:

        if "regiao_nome" in df_f.columns:

            reg = (
                df_f.groupby("regiao_nome")["valor_pago"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                reg,
                x="regiao_nome",
                y="valor_pago",
                color="valor_pago",
                color_continuous_scale="Viridis",
                title="Investimento por Região"
            )

            fig.update_layout(
                height=500,
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # =====================================================
    # STATUS
    # =====================================================
    with col2:

        if "status_bolsa" in df_f.columns:

            status = (
                df_f["status_bolsa"]
                .value_counts()
                .reset_index(name="total")
            )

            fig2 = px.pie(
                status,
                names="status_bolsa",
                values="total",
                hole=0.45,
                title="Status das Bolsas"
            )

            fig2.update_layout(
                height=500
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

# =========================================================
# TAB EVOLUÇÃO
# =========================================================
with tab2:

    if "ano" in df_f.columns:

        anual = (
            df_f.groupby("ano")["valor_pago"]
            .sum()
            .reset_index()
        )

        fig3 = px.area(
            anual,
            x="ano",
            y="valor_pago",
            markers=True,
            title="Evolução Temporal"
        )

        fig3.update_layout(
            height=600
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

# =========================================================
# TAB REGIÕES
# =========================================================
with tab3:

    if (
        "regiao_nome" in df_f.columns and
        "grande_area" in df_f.columns
    ):

        heat = (
            df_f.groupby([
                "regiao_nome",
                "grande_area"
            ])["valor_pago"]
            .sum()
            .reset_index()
        )

        fig4 = px.density_heatmap(
            heat,
            x="regiao_nome",
            y="grande_area",
            z="valor_pago",
            title="Heatmap Região x Área"
        )

        fig4.update_layout(
            height=700
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

# =========================================================
# TAB ÁREAS
# =========================================================
with tab4:

    if "grande_area" in df_f.columns:

        area = (
            df_f.groupby("grande_area")["valor_pago"]
            .sum()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )

        fig5 = px.treemap(
            area,
            path=["grande_area"],
            values="valor_pago",
            title="Treemap Grandes Áreas"
        )

        fig5.update_layout(
            height=700
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

# =========================================================
# TAB RANKINGS
# =========================================================
with tab5:

    col1, col2 = st.columns(2)

    # =====================================================
    # INSTITUIÇÕES
    # =====================================================
    with col1:

        st.subheader("🏛️ Top Instituições")

        if "instituicao_destino" in df_f.columns:

            top_inst = (
                df_f.groupby("instituicao_destino")["valor_pago"]
                .sum()
                .sort_values(ascending=False)
                .head(20)
                .reset_index()
            )

            top_inst["valor_pago"] = (
                top_inst["valor_pago"]
                .apply(fmt_money)
            )

            st.dataframe(
                top_inst,
                use_container_width=True
            )

    # =====================================================
    # PESQUISADORES
    # =====================================================
    with col2:

        st.subheader("👨‍🔬 Top Pesquisadores")

        if "beneficiario" in df_f.columns:

            top_pesq = (
                df_f.groupby("beneficiario")["valor_pago"]
                .sum()
                .sort_values(ascending=False)
                .head(20)
                .reset_index()
            )

            top_pesq["valor_pago"] = (
                top_pesq["valor_pago"]
                .apply(fmt_money)
            )

            st.dataframe(
                top_pesq,
                use_container_width=True
            )

# =========================================================
# TAB EXPORTAÇÃO
# =========================================================
with tab6:

    csv = df_f.to_csv(
        index=False,
        sep=";"
    )

    st.download_button(
        "📥 Exportar CSV",
        csv,
        file_name=f"cnpq_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    resumo = f"""
RELATÓRIO EXECUTIVO CNPq

Investimento total: {fmt_money(total)}
Pesquisadores: {fmt_num(pesquisadores)}
Instituições: {fmt_num(instituicoes)}
Bolsas: {fmt_num(bolsas)}
"""

    st.download_button(
        "📝 Exportar Relatório",
        resumo,
        file_name="relatorio.txt"
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown(f"""
<div class="footer">

🔬 CNPq Analytics Ultimate<br>
Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}

</div>
""", unsafe_allow_html=True)
