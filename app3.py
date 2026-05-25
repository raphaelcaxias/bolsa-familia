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
    page_title="CNPq Analytics – Bolsas de Pesquisa",
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
.download-card {{
    background: {COR_CARD};
    border: 1px dashed {COR_SECUNDARIA};
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
    margin: 1rem 0;
}}
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
# CARREGAMENTO DE DADOS COM UPLOAD
# ============================================================
@st.cache_data
def carregar_dados(uploaded_file):
    """Carrega CSV com detecção automática de encoding e separador"""
    for enc in ["utf-8", "latin1", "cp1252", "ISO-8859-1"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=";", encoding=enc, low_memory=False)
            df.columns = df.columns.str.lower().str.strip()
            
            if "valor_pago" in df.columns:
                df["valor_pago"] = pd.to_numeric(
                    df["valor_pago"].astype(str)
                    .str.replace(",", ".", regex=False)
                    .str.extract(r"(\d+\.?\d*)", expand=False),
                    errors="coerce"
                )
            df = df.dropna(subset=["valor_pago"])
            df = df[df["valor_pago"] > 0]
            
            if "data_inicio_processo" in df.columns:
                df["data_inicio_processo"] = pd.to_datetime(
                    df["data_inicio_processo"], errors="coerce", dayfirst=True
                )
                df["ano"] = df["data_inicio_processo"].dt.year
            
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

# ============================================================
# TELA INICIAL (ANTES DO UPLOAD) – PROFISSIONAL
# ============================================================
st.title("🔬 CNPq Analytics – Bolsas de Pesquisa")
st.caption("Análise de investimentos em ciência e tecnologia no Brasil")

# ----- DADOS DE PRÉVIA (para motivar o usuário) -----
preview_data = {
    "total_bolsas": 213735,
    "total_investido": 1_013_127_958,  # ~R$ 1,01 bi
    "pesquisadores": 88079,
    "instituicoes": 4281,
}

col_preview1, col_preview2, col_preview3, col_preview4 = st.columns(4)
with col_preview1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">📊 Base de dados</div><div class="kpi-value">{fmt_num(preview_data["total_bolsas"])}</div><div class="kpi-sub">registros de bolsas</div></div>', unsafe_allow_html=True)
with col_preview2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">💰 Investimento total</div><div class="kpi-value">{fmt_brl(preview_data["total_investido"])}</div><div class="kpi-sub">acumulado</div></div>', unsafe_allow_html=True)
with col_preview3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">👥 Pesquisadores</div><div class="kpi-value">{fmt_num(preview_data["pesquisadores"])}</div><div class="kpi-sub">beneficiários únicos</div></div>', unsafe_allow_html=True)
with col_preview4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">🏛️ Instituições</div><div class="kpi-value">{fmt_num(preview_data["instituicoes"])}</div><div class="kpi-sub">unidades atendidas</div></div>', unsafe_allow_html=True)

# ----- Explicação do projeto -----
st.markdown("""
### 📌 Sobre este dashboard

Este projeto analisa **mais de 213 mil bolsas de pesquisa** concedidas pelo CNPq entre 2014 e 2027, totalizando **mais de R$ 1 bilhão** em investimentos.  
Os dados são públicos e podem ser baixados diretamente do **Portal Brasileiro de Dados Abertos (CGU/CNPq)**.

#### O que você vai descobrir:
- ✅ Quais **áreas do conhecimento** recebem mais recursos (Ciências da Saúde, Engenharias, Ciências Agrárias…)
- ✅ **Distribuição regional** do investimento (Sudeste lidera com mais de 50%)
- ✅ **Rankings** de pesquisadores e instituições mais financiados
- ✅ **Evolução histórica** do investimento em ciência e tecnologia
- ✅ **Modalidades** de bolsa mais frequentes (Iniciação Científica, Mestrado, Doutorado…)
""")

# ----- Link para download do CSV (Google Drive) -----
st.markdown("""
<div class="download-card">
    <h4>📥 1. Baixe o arquivo CSV original</h4>
    <p>Os dados estão disponíveis gratuitamente no Google Drive.<br>
    Clique no botão abaixo para fazer o download do arquivo <strong>bolsa_familia.csv</strong> (110 MB).</p>
    <a href="https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub" target="_blank">
        <button style="background:#2563EB; color:white; border:none; border-radius:8px; padding:8px 20px; cursor:pointer;">
            📂 Baixar CSV (Google Drive)
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

# ----- Passo a passo -----
st.markdown("""
### 🚀 2. Faça o upload do arquivo

Após baixar o CSV, utilize o menu lateral para enviá-lo. O dashboard processará os dados e exibirá gráficos interativos e insights automáticos.
""")

# ----- Sidebar com upload (já existe, mas mantemos) -----
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
    
    uploaded_file = st.file_uploader(
        "📂 Envie o arquivo CSV (bolsa_familia.csv)",
        type=["csv"],
        help="Arquivo com dados de bolsas do CNPq"
    )
    
    if uploaded_file is None:
        st.info("👈 Faça upload do CSV para iniciar a análise completa.")
        st.stop()
    else:
        with st.spinner("Processando dados..."):
            df, encoding = carregar_dados(uploaded_file)
        if df is None:
            st.error("❌ Erro ao ler o arquivo. Verifique o formato (separador ';', encoding latin1/utf-8).")
            st.stop()
        st.success(f"✅ Dados carregados: {df.shape[0]:,} registros (encoding: {encoding})")

# ============================================================
# A PARTIR DAQUI OS DADOS JÁ ESTÃO CARREGADOS
# ============================================================

# Filtros laterais
st.sidebar.markdown("---")
df_filtrado = df.copy()

if "ano" in df.columns:
    anos = sorted(df["ano"].dropna().unique().astype(int))
    if len(anos) > 1:
        ano_sel = st.sidebar.slider("Ano", min(anos), max(anos), (min(anos), max(anos)), step=1)
        df_filtrado = df_filtrado[(df_filtrado["ano"] >= ano_sel[0]) & (df_filtrado["ano"] <= ano_sel[1])]

if "grande_area" in df.columns:
    areas = sorted(df["grande_area"].dropna().unique())
    areas_sel = st.sidebar.multiselect("Grande Área", areas, default=areas[:6] if len(areas) > 6 else areas)
    if areas_sel:
        df_filtrado = df_filtrado[df_filtrado["grande_area"].isin(areas_sel)]

if "regiao_nome" in df.columns:
    regioes = sorted(df["regiao_nome"].dropna().unique())
    reg_sel = st.sidebar.multiselect("Região", regioes, default=regioes)
    if reg_sel:
        df_filtrado = df_filtrado[df_filtrado["regiao_nome"].isin(reg_sel)]

if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True):
    st.rerun()

# ============================================================
# STORYTELLING E KPIs APÓS UPLOAD
# ============================================================
total_volume = df_filtrado["valor_pago"].sum()
total_bolsas = df_filtrado.shape[0]
ticket_medio = total_volume / total_bolsas if total_bolsas > 0 else 0
num_pesquisadores = df_filtrado["beneficiario"].nunique() if "beneficiario" in df_filtrado.columns else 0
num_instituicoes = df_filtrado["instituicao_destino"].nunique() if "instituicao_destino" in df_filtrado.columns else 0

col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">💰 Investimento Total</div><div class="kpi-value">{fmt_brl(total_volume)}</div></div>', unsafe_allow_html=True)
with col_k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">🎓 Bolsas</div><div class="kpi-value">{fmt_num(total_bolsas)}</div></div>', unsafe_allow_html=True)
with col_k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">👥 Pesquisadores</div><div class="kpi-value">{fmt_num(num_pesquisadores)}</div></div>', unsafe_allow_html=True)
with col_k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">🏛️ Instituições</div><div class="kpi-value">{fmt_num(num_instituicoes)}</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("👉 **Navegue pelas abas abaixo para explorar os gráficos interativos.**")

# ============================================================
# ABAS DE ANÁLISE (MESMO CÓDIGO ANTERIOR)
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
        fig_area.update_layout(template=PLOTLY_TEMPLATE, height=500)
        fig_area.update_traces(textposition="outside")
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("Coluna 'grande_area' não encontrada.")

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
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            fig_pie = px.pie(reg_data, names="Região", values="Valor", hole=0.4,
                             title="Distribuição Regional",
                             color_discrete_sequence=[COR_SECUNDARIA, COR_ATENCAO, COR_SUCESSO, COR_ALERTA, "#64748B"])
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(template=PLOTLY_TEMPLATE, height=450)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Coluna 'regiao_nome' não encontrada.")

# ---------- TAB 3: EVOLUÇÃO ----------
with tab3:
    if "ano" in df_filtrado.columns:
        evolucao = df_filtrado.groupby("ano")["valor_pago"].sum().reset_index()
        fig_evol = px.line(evolucao, x="ano", y="valor_pago", markers=True,
                           title="Evolução do Investimento ao Longo dos Anos",
                           labels={"ano": "Ano", "valor_pago": "Investimento (R$)"})
        fig_evol.update_traces(line=dict(width=2, color=COR_SECUNDARIA), marker=dict(size=8))
        fig_evol.update_layout(template=PLOTLY_TEMPLATE, height=450)
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Coluna 'ano' não encontrada.")

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
            st.info("Coluna 'beneficiario' não encontrada.")
    with col_r2:
        st.markdown("#### 🏛️ Top 10 Instituições")
        if "instituicao_destino" in df_filtrado.columns:
            top_inst = df_filtrado.groupby("instituicao_destino")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
            top_inst.columns = ["Instituição", "Total"]
            top_inst["Total"] = top_inst["Total"].apply(fmt_brl)
            st.dataframe(top_inst, use_container_width=True, hide_index=True)
        else:
            st.info("Coluna 'instituicao_destino' não encontrada.")

    st.markdown("#### 🎓 Modalidades Mais Frequentes")
    if "modalidade" in df_filtrado.columns:
        modalidades = df_filtrado["modalidade"].value_counts().head(10).reset_index()
        modalidades.columns = ["Modalidade", "Quantidade"]
        st.dataframe(modalidades, use_container_width=True, hide_index=True)
    else:
        st.info("Coluna 'modalidade' não encontrada.")

# ============================================================
# RODAPÉ
# ============================================================
st.markdown("---")
st.markdown(f"""
<p style='text-align:center; color:#64748B; font-size:0.7rem;'>
    🔬 CNPq Analytics · Fonte: CNPq / Portal Brasileiro de Dados Abertos<br>
    Dashboard desenvolvido para portfólio de Análise de Dados.
</p>""", unsafe_allow_html=True)
