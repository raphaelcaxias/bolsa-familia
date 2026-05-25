import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="CNPq Analytics – Painel de Bolsas de Pesquisa",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# TEMA (CLARO / ESCURO)
# ============================================================
if "tema" not in st.session_state:
    st.session_state.tema = "claro"

if st.session_state.tema == "claro":
    COR_FUNDO       = "#F8FAFC"
    COR_CARD        = "#FFFFFF"
    COR_TEXTO       = "#1E293B"
    COR_BORDA       = "#E2E8F0"
    COR_PRIMARIA    = "#0F172A"
    COR_SECUNDARIA  = "#2563EB"
    COR_SUCESSO     = "#16A34A"
    COR_ALERTA      = "#DC2626"
    COR_ATENCAO     = "#D97706"
    PLOTLY_TEMPLATE = "plotly_white"
    COR_GRID        = "rgba(0,0,0,0.06)"
else:
    COR_FUNDO       = "#0B0F19"
    COR_CARD        = "#111827"
    COR_TEXTO       = "#F3F4F6"
    COR_BORDA       = "#1F2937"
    COR_PRIMARIA    = "#38BDF8"
    COR_SECUNDARIA  = "#60A5FA"
    COR_SUCESSO     = "#34D399"
    COR_ALERTA      = "#F87171"
    COR_ATENCAO     = "#FBBF24"
    PLOTLY_TEMPLATE = "plotly_dark"
    COR_GRID        = "rgba(255,255,255,0.06)"

# ============================================================
# CSS PERSONALIZADO
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
html, body, .stApp {{
    background-color: {COR_FUNDO};
    color: {COR_TEXTO};
    font-family: 'IBM Plex Sans', sans-serif;
}}
.block-container {{ padding: 1rem 1.5rem; }}
.kpi-card {{
    background: {COR_CARD};
    border-left: 4px solid {COR_SECUNDARIA};
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
}}
.kpi-title {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; color: #64748B; font-weight: 600; }}
.kpi-value {{ font-size: 1.6rem; font-weight: 700; color: {COR_TEXTO}; margin-top: 0.15rem; }}
.insight-box {{
    background: {COR_CARD};
    border: 1px solid {COR_BORDA};
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}}
.insight-label {{ font-size: 0.65rem; text-transform: uppercase; color: #94A3B8; font-weight: 600; }}
.insight-text  {{ font-size: 0.85rem; color: {COR_TEXTO}; line-height: 1.5; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES DE FORMATAÇÃO
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

# ============================================================
# CARREGAMENTO DE DADOS (com múltiplos encodings)
# ============================================================
@st.cache_data(ttl=3600)
def carregar_dados():
    for enc in ["utf-8", "latin1", "cp1252", "ISO-8859-1"]:
        try:
            df = pd.read_csv("bolsa_familia.csv", sep=";", encoding=enc, low_memory=False)
            df.columns = df.columns.str.lower().str.strip()
            # Converte valor_pago
            if "valor_pago" in df.columns:
                df["valor_pago"] = pd.to_numeric(
                    df["valor_pago"].astype(str).str.replace(",", ".", regex=False)
                    .str.extract(r"(\d+\.?\d*)", expand=False),
                    errors="coerce"
                )
            # Remove linhas sem valor
            df = df.dropna(subset=["valor_pago"])
            df = df[df["valor_pago"] > 0]
            # Converte data se existir
            if "data_inicio_processo" in df.columns:
                df["data_inicio_processo"] = pd.to_datetime(df["data_inicio_processo"], errors="coerce", dayfirst=True)
                df["ano"] = df["data_inicio_processo"].dt.year
            # Mapeia regiões se coluna 'regiao' existir
            if "regiao" in df.columns:
                regioes_map = {
                    "SE": "Sudeste", "SU": "Sul", "NE": "Nordeste",
                    "CO": "Centro-Oeste", "N": "Norte", "NO": "Norte",
                    "EX": "Exterior", "NI": "Não Informado"
                }
                df["regiao_nome"] = df["regiao"].map(regioes_map).fillna(df["regiao"])
            return df, enc
        except Exception:
            continue
    return None, None

df, encoding = carregar_dados()
if df is None or len(df) == 0:
    st.error("❌ Erro ao carregar os dados. Verifique se o arquivo 'bolsa_familia.csv' está presente.")
    st.stop()

# ============================================================
# SIDEBAR (filtros e tema)
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Controles")
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

    # Filtros
    df_filtrado = df.copy()

    if "ano" in df.columns:
        anos = sorted(df["ano"].dropna().unique().astype(int))
        ano_sel = st.slider("Ano", min(anos), max(anos), (min(anos), max(anos)), step=1)
        df_filtrado = df_filtrado[(df_filtrado["ano"] >= ano_sel[0]) & (df_filtrado["ano"] <= ano_sel[1])]

    if "grande_area" in df.columns:
        areas = sorted(df["grande_area"].dropna().unique())
        areas_sel = st.multiselect("Grande Área", areas, default=areas[:6] if len(areas) > 6 else areas)
        if areas_sel:
            df_filtrado = df_filtrado[df_filtrado["grande_area"].isin(areas_sel)]

    if "regiao_nome" in df.columns:
        regioes = sorted(df["regiao_nome"].dropna().unique())
        reg_sel = st.multiselect("Região", regioes, default=regioes)
        if reg_sel:
            df_filtrado = df_filtrado[df_filtrado["regiao_nome"].isin(reg_sel)]

    if st.button("🔄 Limpar Filtros", use_container_width=True):
        st.rerun()

# ============================================================
# HEADER PRINCIPAL E STORYTELLING
# ============================================================
st.title("🔬 CNPq Analytics – Bolsas de Pesquisa")
st.caption("Análise de investimentos em ciência e tecnologia – Fonte: CNPq / Dados Abertos")

with st.container():
    col_origem, col_link = st.columns([3, 1])
    with col_origem:
        st.markdown("""
        **📌 Sobre os dados**  
        Este dashboard analisa mais de **213 mil bolsas de pesquisa** concedidas pelo CNPq entre 2014 e 2027, totalizando **mais de R$ 1 bilhão** em investimentos.  
        Os dados foram extraídos do **Portal Brasileiro de Dados Abertos (CGU/CNPq)** e incluem informações por área do conhecimento, região, instituição e modalidade de bolsa.
        """)
    with col_link:
        st.markdown(f"""
        <div style="background:{COR_CARD}; padding:0.8rem; border-radius:10px; text-align:center; border:1px solid {COR_BORDA}">
        🔗 <a href="https://dados.gov.br/" target="_blank" style="color:{COR_SECUNDARIA}">Fonte original →</a>
        </div>
        """, unsafe_allow_html=True)

    # KPIs principais
    total_volume = df_filtrado["valor_pago"].sum()
    total_bolsas = df_filtrado.shape[0]
    ticket_medio = total_volume / total_bolsas if total_bolsas > 0 else 0
    num_pesquisadores = df_filtrado["beneficiario"].nunique() if "beneficiario" in df_filtrado.columns else 0
    num_instituicoes = df_filtrado["instituicao_destino"].nunique() if "instituicao_destino" in df_filtrado.columns else 0

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">💰 Investimento Total</div><div class="kpi-value">{fmt_brl(total_volume)}</div></div>', unsafe_allow_html=True)
    with col_k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">🎓 Bolsas Concedidas</div><div class="kpi-value">{fmt_num(total_bolsas)}</div></div>', unsafe_allow_html=True)
    with col_k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">👥 Pesquisadores</div><div class="kpi-value">{fmt_num(num_pesquisadores)}</div></div>', unsafe_allow_html=True)
    with col_k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">🏛️ Instituições</div><div class="kpi-value">{fmt_num(num_instituicoes)}</div></div>', unsafe_allow_html=True)

    # Principais conclusões (insights automáticos)
    st.markdown("### 📌 Principais Conclusões")

    if "grande_area" in df_filtrado.columns:
        area_lider = df_filtrado.groupby("grande_area")["valor_pago"].sum().idxmax()
        pct_area = (df_filtrado.groupby("grande_area")["valor_pago"].sum().max() / total_volume) * 100
    else:
        area_lider = "N/D"
        pct_area = 0

    if "regiao_nome" in df_filtrado.columns:
        reg_lider = df_filtrado.groupby("regiao_nome")["valor_pago"].sum().idxmax()
        pct_reg = (df_filtrado.groupby("regiao_nome")["valor_pago"].sum().max() / total_volume) * 100
    else:
        reg_lider = "N/D"
        pct_reg = 0

    col_conc1, col_conc2 = st.columns(2)
    with col_conc1:
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-label">🧬 Área do Conhecimento Líder</div>
            <div class="insight-text"><b>{area_lider}</b> responde por <b>{pct_area:.1f}%</b> do investimento total.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_conc2:
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-label">🗺️ Região de Maior Investimento</div>
            <div class="insight-text"><b>{reg_lider}</b> concentra <b>{pct_reg:.1f}%</b> dos recursos.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("👉 **Navegue pelas abas abaixo para explorar os gráficos interativos.**")

# ============================================================
# ABAS DE ANÁLISE
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Por Área do Conhecimento",
    "🗺️ Por Região",
    "📈 Evolução Temporal",
    "🏆 Rankings"
])

# ---------- TAB 1: ÁREAS ----------
with tab1:
    if "grande_area" in df_filtrado.columns:
        area_data = df_filtrado.groupby("grande_area")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
        area_data.columns = ["Área", "Valor"]

        fig_area = px.bar(area_data, x="Valor", y="Área", orientation="h",
                          color="Valor", color_continuous_scale="Blues",
                          text=area_data["Valor"].apply(lambda x: fmt_brl(x)),
                          title="Top 10 Áreas com Maior Investimento")
        fig_area.update_layout(template=PLOTLY_TEMPLATE, height=500, margin=dict(l=20, r=20, t=50, b=20))
        fig_area.update_traces(textposition="outside")
        st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': True})
    else:
        st.info("Coluna 'grande_area' não disponível.")

# ---------- TAB 2: REGIÕES ----------
with tab2:
    if "regiao_nome" in df_filtrado.columns:
        reg_data = df_filtrado.groupby("regiao_nome")["valor_pago"].sum().reset_index()
        reg_data.columns = ["Região", "Valor"]

        col1, col2 = st.columns(2)
        with col1:
            fig_bar = px.bar(reg_data, x="Região", y="Valor", color="Valor",
                             color_continuous_scale="Blues", text=reg_data["Valor"].apply(lambda x: fmt_brl(x)),
                             title="Investimento por Região")
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(template=PLOTLY_TEMPLATE, height=450)
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': True})

        with col2:
            fig_pie = px.pie(reg_data, names="Região", values="Valor", hole=0.4,
                             title="Distribuição Regional",
                             color_discrete_sequence=[COR_SECUNDARIA, COR_ATENCAO, COR_SUCESSO, COR_ALERTA, "#64748B"])
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(template=PLOTLY_TEMPLATE, height=450)
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': True})
    else:
        st.info("Coluna 'regiao_nome' não disponível.")

# ---------- TAB 3: EVOLUÇÃO TEMPORAL ----------
with tab3:
    if "ano" in df_filtrado.columns:
        evolucao = df_filtrado.groupby("ano")["valor_pago"].sum().reset_index()
        fig_evol = px.line(evolucao, x="ano", y="valor_pago", markers=True,
                           title="Evolução do Investimento ao Longo dos Anos",
                           labels={"ano": "Ano", "valor_pago": "Investimento (R$)"})
        fig_evol.update_traces(line=dict(width=2, color=COR_SECUNDARIA), marker=dict(size=8))
        fig_evol.update_layout(template=PLOTLY_TEMPLATE, height=450)
        st.plotly_chart(fig_evol, use_container_width=True, config={'displayModeBar': True})
    else:
        st.info("Coluna 'ano' não disponível.")

# ---------- TAB 4: RANKINGS ----------
with tab4:
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("#### 🏆 Top 10 Pesquisadores")
        if "beneficiario" in df_filtrado.columns:
            top_pesq = df_filtrado.groupby("beneficiario")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
            top_pesq.columns = ["Pesquisador", "Total"]
            top_pesq["Total"] = top_pesq["Total"].apply(fmt_brl)
            st.dataframe(top_pesq, use_container_width=True, hide_index=True)
        else:
            st.info("Dados de beneficiário não disponíveis.")
    with col_r2:
        st.markdown("#### 🏛️ Top 10 Instituições")
        if "instituicao_destino" in df_filtrado.columns:
            top_inst = df_filtrado.groupby("instituicao_destino")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
            top_inst.columns = ["Instituição", "Total"]
            top_inst["Total"] = top_inst["Total"].apply(fmt_brl)
            st.dataframe(top_inst, use_container_width=True, hide_index=True)
        else:
            st.info("Dados de instituição não disponíveis.")

    st.markdown("#### 🎓 Modalidades Mais Frequentes")
    if "modalidade" in df_filtrado.columns:
        modalidades = df_filtrado["modalidade"].value_counts().head(10).reset_index()
        modalidades.columns = ["Modalidade", "Quantidade"]
        st.dataframe(modalidades, use_container_width=True, hide_index=True)
    else:
        st.info("Dados de modalidade não disponíveis.")

# ============================================================
# RODAPÉ
# ============================================================
st.markdown("---")
st.markdown(f"""
<p style='text-align:center; color:#64748B; font-size:0.7rem;'>
    🔬 CNPq Analytics · Fonte: CNPq / Portal Brasileiro de Dados Abertos<br>
    Dados de bolsas de pesquisa concedidas entre 2014 e 2027.
</p>""", unsafe_allow_html=True)
