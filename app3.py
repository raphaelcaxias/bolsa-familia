import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import warnings
import base64

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="CNPq Analytics | Análise de Bolsas de Pesquisa",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CORES ESCURAS PREMIUM (fixo, sem toggle)
# ============================================================
COR_FUNDO = "#0A0F1C"
COR_CARD = "rgba(18, 25, 45, 0.85)"
COR_BORDA = "rgba(56, 189, 248, 0.3)"
COR_GLOW = "rgba(56, 189, 248, 0.5)"
COR_TEXTO = "#F1F5F9"
COR_TEXTO_MUTED = "#94A3B8"
COR_AZUL = "#3B82F6"
COR_VERDE = "#10B981"
COR_VERMELHO = "#EF4444"
COR_AMARELO = "#F59E0B"

# ============================================================
# CSS PREMIUM
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

.stApp {{
    background: radial-gradient(circle at 20% 30%, #0A0F1C, #030712);
    font-family: 'Inter', sans-serif;
}}

.block-container {{ padding: 1.5rem 2rem !important; }}

.hero {{
    background: linear-gradient(135deg, rgba(56,189,248,0.1) 0%, rgba(16,185,129,0.05) 100%);
    border-radius: 2rem;
    padding: 2rem;
    margin-bottom: 1.5rem;
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
    margin-bottom: 1rem;
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
    font-size: 0.7rem;
    color: {COR_AZUL};
}}

.preview-card, .value-card, .upload-card, .kpi-card {{
    background: {COR_CARD};
    backdrop-filter: blur(10px);
    border: 1px solid {COR_BORDA};
    border-radius: 1rem;
    padding: 1rem;
    transition: all 0.3s ease;
}}

.preview-card:hover, .value-card:hover, .kpi-card:hover {{
    transform: translateY(-3px);
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
}}

.upload-card {{
    border: 2px dashed {COR_AZUL};
    text-align: center;
    margin: 1rem 0;
}}

.download-btn {{
    display: inline-block;
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border: 1px solid {COR_AZUL};
    border-radius: 2rem;
    padding: 0.5rem 1rem;
    color: white;
    text-decoration: none;
    font-size: 0.8rem;
    transition: all 0.2s;
    margin-top: 0.5rem;
    text-align: center;
}}
.download-btn:hover {{
    border-color: {COR_VERDE};
    box-shadow: 0 0 12px {COR_GLOW};
}}

section[data-testid="stSidebar"] {{
    background: rgba(10, 15, 28, 0.95);
    backdrop-filter: blur(12px);
    border-right: 1px solid {COR_BORDA};
}}

.footer {{
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    margin-top: 2rem;
    border-top: 1px solid {COR_BORDA};
    color: {COR_TEXTO_MUTED};
    font-size: 0.65rem;
}}

.stMetric {{
    background: {COR_CARD};
    backdrop-filter: blur(10px);
    border: 1px solid {COR_BORDA};
    border-radius: 1rem;
    padding: 0.5rem;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES AUXILIARES
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
    """Carrega CSV com cache – SEM barra de progresso"""
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
            
            return df, enc
        except:
            continue
    return None, None

def calcular_hhi(df, coluna):
    total = df[coluna].sum()
    if total == 0:
        return 0
    participacoes = (df[coluna] / total) ** 2
    return participacoes.sum() * 10000

def calcular_cagr(serie):
    if len(serie) < 2:
        return 0
    primeiro = serie.iloc[0]
    ultimo = serie.iloc[-1]
    n = len(serie) - 1
    if primeiro <= 0:
        return 0
    return (pow(ultimo/primeiro, 1/n) - 1) * 100

def calcular_pareto(df, coluna):
    df_sorted = df.sort_values(coluna, ascending=False).reset_index(drop=True)
    total = df_sorted[coluna].sum()
    df_sorted['percentual_acumulado'] = (df_sorted[coluna].cumsum() / total) * 100
    return df_sorted

# ============================================================
# LINK PARA DOWNLOAD DO CSV (Google Drive)
# ============================================================
LINK_CSV = "https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub"

# ============================================================
# PÁGINA INICIAL (ANTES DO UPLOAD)
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
        <span class="hero-badge">📈 Análise preditiva</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.markdown("""
    <div style="background: rgba(18,25,45,0.5); border-radius: 1rem; padding: 0.6rem;">
        <h4 style="margin: 0;">📌 Fonte</h4>
        <p style="font-size: 0.65rem;">Portal Dados Abertos (CGU/CNPq)</p>
    </div>
    """, unsafe_allow_html=True)
with col_info2:
    st.markdown("""
    <div style="background: rgba(18,25,45,0.5); border-radius: 1rem; padding: 0.6rem;">
        <h4 style="margin: 0;">⚙️ Limite</h4>
        <p style="font-size: 0.65rem;">CSV até 200MB · 213.735 registros</p>
    </div>
    """, unsafe_allow_html=True)
with col_info3:
    st.markdown(f"""
    <div style="background: rgba(18,25,45,0.5); border-radius: 1rem; padding: 0.6rem; text-align: center;">
        <a href="{LINK_CSV}" target="_blank" style="color:{COR_AZUL}; text-decoration: none; font-size: 0.7rem;">📥 Baixar CSV (Google Drive) →</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 📈 Conheça o potencial")
col1, col2, col3, col4 = st.columns(4)
for col, num, label in zip([col1, col2, col3, col4],
                           ["213.735", "R$ 1,02B", "88.079", "4.281"],
                           ["Bolsas analisadas", "Investimento total", "Pesquisadores", "Instituições"]):
    with col:
        st.markdown(f"""
        <div class="preview-card">
            <div class="preview-number">{num}</div>
            <div class="preview-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("### 💡 O que você vai descobrir")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    st.markdown('<div class="value-card"><span style="font-size:1.5rem;">🎯</span><h4>Concentração regional</h4><p style="color:#94A3B8; font-size:0.7rem;">Quais regiões lideram os investimentos</p></div>', unsafe_allow_html=True)
with col_v2:
    st.markdown('<div class="value-card"><span style="font-size:1.5rem;">🧬</span><h4>Áreas do conhecimento</h4><p style="color:#94A3B8; font-size:0.7rem;">Saúde, Engenharia, Humanas</p></div>', unsafe_allow_html=True)
with col_v3:
    st.markdown('<div class="value-card"><span style="font-size:1.5rem;">🏆</span><h4>Rankings de impacto</h4><p style="color:#94A3B8; font-size:0.7rem;">Top pesquisadores e instituições</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="upload-card">
    <span style="font-size:2rem;">📂</span>
    <h3>Carregue o arquivo CSV</h3>
    <p style="color:#94A3B8; font-size:0.75rem;">Baixe o dataset oficial do CNPq e faça upload</p>
    <p style="color:#3B82F6; font-size:0.7rem;">⬅️ Use o menu lateral para enviar o arquivo</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🎛️ Central Analítica")
    st.markdown(f"📥 [Baixar CSV exemplo]({LINK_CSV})")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Carregar CSV (bolsa_familia.csv)", type=["csv"])
    
    if uploaded_file is None:
        st.info("👈 Envie o arquivo para iniciar a análise")
        st.stop()
    
    with st.spinner("🔄 Processando arquivo de 110MB... Isso pode levar alguns segundos"):
        df, encoding = carregar_dados(uploaded_file)
    
    if df is None:
        st.error("❌ Erro no CSV. Verifique separador ';' e encoding (latin1/utf-8).")
        st.stop()
    
    st.success(f"✅ {df.shape[0]:,} registros carregados")
    st.caption(f"📁 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
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
# DASHBOARD PRINCIPAL
# ============================================================
total_volume = df_filtrado["valor_pago"].sum()
total_bolsas = df_filtrado.shape[0]
ticket_medio = total_volume / total_bolsas if total_bolsas > 0 else 0
n_pesq = df_filtrado["beneficiario"].nunique() if "beneficiario" in df_filtrado.columns else 0
n_inst = df_filtrado["instituicao_destino"].nunique() if "instituicao_destino" in df_filtrado.columns else 0

col1, col2, col3, col4 = st.columns(4)

if "ano" in df_filtrado.columns:
    evol_ano = df_filtrado.groupby("ano")["valor_pago"].sum()
    cagr = calcular_cagr(evol_ano)
    cagr_str = f"CAGR: {cagr:+.1f}%" if cagr != 0 else ""
else:
    cagr_str = ""

with col1:
    st.metric("💰 INVESTIMENTO TOTAL", fmt_brl(total_volume), delta=cagr_str)
with col2:
    st.metric("🎓 BOLSAS", fmt_num(total_bolsas))
with col3:
    st.metric("👥 PESQUISADORES", fmt_num(n_pesq))
with col4:
    st.metric("🏛️ INSTITUIÇÕES", fmt_num(n_inst))

st.caption(f"📊 Ticket médio: {fmt_brl(ticket_medio)} | Média por pesquisador: {fmt_brl(total_volume/n_pesq) if n_pesq>0 else 'N/A'}")

# ============================================================
# RESUMO EXECUTIVO
# ============================================================
st.markdown("## 🔍 Resumo Executivo")

insights = []

if "regiao_nome" in df_filtrado.columns:
    reg_share = df_filtrado.groupby("regiao_nome")["valor_pago"].sum()
    top_reg = reg_share.idxmax()
    pct_reg = (reg_share.max() / total_volume) * 100
    insights.append(f"📍 A região **{top_reg}** concentra **{pct_reg:.1f}%** do investimento total.")

if "grande_area" in df_filtrado.columns:
    area_share = df_filtrado.groupby("grande_area")["valor_pago"].sum()
    top_area = area_share.idxmax()
    pct_area = (area_share.max() / total_volume) * 100
    insights.append(f"🧬 A área **{top_area}** lidera com **{pct_area:.1f}%** dos recursos.")

if "ano" in df_filtrado.columns:
    evol_ano = df_filtrado.groupby("ano")["valor_pago"].sum()
    if len(evol_ano) >= 2:
        crescimento = (evol_ano.iloc[-1] / evol_ano.iloc[-2] - 1) * 100
        if crescimento > 10:
            insights.append(f"📈 Crescimento acelerado de **+{crescimento:.1f}%** no último ano.")
        elif crescimento < -5:
            insights.append(f"📉 Queda de **{crescimento:.1f}%** no último ano – atenção necessária.")
        else:
            insights.append(f"📊 Estabilidade: variação de **{crescimento:+.1f}%** no último ano.")

if "nome_conglomerado_financeiro" in df_filtrado.columns:
    hhi = calcular_hhi(df_filtrado, "valor_pago")
    if hhi > 2500:
        insights.append(f"⚠️ Alta concentração de recursos (HHI {hhi:.0f}) – poucas instituições dominam.")
    elif hhi > 1500:
        insights.append(f"🟡 Concentração moderada (HHI {hhi:.0f}).")
    else:
        insights.append(f"🟢 Mercado competitivo (HHI {hhi:.0f}).")

for insight in insights:
    st.info(insight)

# ============================================================
# ABAS
# ============================================================
st.markdown("## 📊 Análises Interativas")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Evolução Temporal", "🗺️ Distribuição Regional", "🧬 Áreas do Conhecimento",
    "🏆 Rankings", "📊 Estatísticas", "🤖 Análises Avançadas"
])

# TAB 1: EVOLUÇÃO TEMPORAL
with tab1:
    if "ano" in df_filtrado.columns:
        evol_data = df_filtrado.groupby("ano")["valor_pago"].sum().reset_index()
        fig_evol = px.line(evol_data, x="ano", y="valor_pago", markers=True,
                           title="Evolução do Investimento por Ano")
        fig_evol.update_layout(template="plotly_dark", height=450)
        fig_evol.update_traces(line=dict(width=3, color=COR_AZUL), marker=dict(size=8, color=COR_VERDE))
        st.plotly_chart(fig_evol, use_container_width=True)
        
        if len(evol_data) >= 3:
            st.markdown("#### 🔮 Projeção para próximos 2 anos")
            X = np.array(evol_data["ano"]).reshape(-1, 1)
            y = evol_data["valor_pago"].values
            model = LinearRegression()
            model.fit(X, y)
            anos_futuros = np.arange(evol_data["ano"].max() + 1, evol_data["ano"].max() + 3).reshape(-1, 1)
            pred = model.predict(anos_futuros)
            proj_data = pd.DataFrame({"ano": anos_futuros.flatten(), "projecao": pred})
            fig_proj = px.line(proj_data, x="ano", y="projecao", markers=True, title="Projeção Linear")
            fig_proj.add_scatter(x=evol_data["ano"], y=evol_data["valor_pago"], mode="lines+markers", name="Histórico")
            fig_proj.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_proj, use_container_width=True)
    else:
        st.info("Coluna 'ano' não disponível para análise temporal.")

# TAB 2: DISTRIBUIÇÃO REGIONAL
with tab2:
    if "regiao_nome" in df_filtrado.columns:
        reg_data = df_filtrado.groupby("regiao_nome")["valor_pago"].sum().reset_index()
        reg_data.columns = ["Região", "Valor"]
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            fig_bar = px.bar(reg_data, x="Região", y="Valor", color="Valor",
                             color_continuous_scale="Blues",
                             text=reg_data["Valor"].apply(lambda x: fmt_brl(x)),
                             title="Investimento por Região")
            fig_bar.update_layout(template="plotly_dark", height=450)
            fig_bar.update_traces(textposition="outside")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_r2:
            fig_pie = px.pie(reg_data, names="Região", values="Valor", hole=0.4,
                             title="Participação por Região",
                             color_discrete_sequence=[COR_AZUL, COR_VERDE, COR_AMARELO, COR_VERMELHO, "#64748B"])
            fig_pie.update_layout(template="plotly_dark", height=450)
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        ticket_reg = df_filtrado.groupby("regiao_nome")["valor_pago"].mean().reset_index()
        ticket_reg.columns = ["Região", "Ticket Médio"]
        fig_ticket = px.bar(ticket_reg, x="Região", y="Ticket Médio", color="Ticket Médio",
                            color_continuous_scale="Greens", title="Ticket Médio por Região")
        fig_ticket.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_ticket, use_container_width=True)
    else:
        st.info("Dados regionais não disponíveis.")

# TAB 3: ÁREAS DO CONHECIMENTO
with tab3:
    if "grande_area" in df_filtrado.columns:
        area_data = df_filtrado.groupby("grande_area")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
        area_data.columns = ["Área", "Valor"]
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            fig_area = px.bar(area_data, x="Valor", y="Área", orientation="h",
                              color="Valor", color_continuous_scale="Viridis",
                              text=area_data["Valor"].apply(lambda x: fmt_brl(x)),
                              title="Top 10 Áreas com Maior Investimento")
            fig_area.update_layout(template="plotly_dark", height=500)
            fig_area.update_traces(textposition="outside")
            st.plotly_chart(fig_area, use_container_width=True)
        
        with col_a2:
            fig_treemap = px.treemap(area_data, path=["Área"], values="Valor",
                                     title="Distribuição do Investimento por Área (Treemap)",
                                     color="Valor", color_continuous_scale="Blues")
            fig_treemap.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig_treemap, use_container_width=True)
        
        st.markdown("#### 📊 Análise de Pareto (80/20)")
        pareto_data = calcular_pareto(area_data, "Valor")
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=pareto_data["Área"], y=pareto_data["Valor"], name="Investimento", marker_color=COR_AZUL))
        fig_pareto.add_trace(go.Scatter(x=pareto_data["Área"], y=pareto_data["percentual_acumulado"], name="% Acumulado", yaxis="y2", mode="lines+markers", line=dict(color=COR_VERMELHO, width=2)))
        fig_pareto.update_layout(template="plotly_dark", height=400, yaxis2=dict(overlaying="y", side="right", range=[0, 105]))
        st.plotly_chart(fig_pareto, use_container_width=True)
    else:
        st.info("Dados de área do conhecimento não disponíveis.")

# TAB 4: RANKINGS
with tab4:
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("#### 🏆 Top 10 Pesquisadores")
        if "beneficiario" in df_filtrado.columns:
            top_people = df_filtrado.groupby("beneficiario")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
            top_people.columns = ["Pesquisador", "Total"]
            top_people["Total"] = top_people["Total"].apply(fmt_brl)
            total_pesq = df_filtrado["valor_pago"].sum()
            top_people["Participação"] = top_people["Total"].apply(lambda x: f"{(float(x.replace('R$', '').replace('M', '').replace(',', '.').strip()) * 1000000 / total_pesq * 100):.1f}%")
            st.dataframe(top_people, use_container_width=True, hide_index=True)
            
            st.markdown("#### 🔍 Buscar pesquisador")
            busca = st.text_input("Digite o nome")
            if busca:
                resultados = df_filtrado[df_filtrado["beneficiario"].str.contains(busca, case=False, na=False)]
                if not resultados.empty:
                    st.dataframe(resultados[["beneficiario", "valor_pago"]].head(10), use_container_width=True)
                else:
                    st.info("Nenhum resultado encontrado")
        else:
            st.info("Dados de beneficiário não disponíveis")
    
    with col_r2:
        st.markdown("#### 🏆 Top 10 Instituições")
        if "instituicao_destino" in df_filtrado.columns:
            top_inst = df_filtrado.groupby("instituicao_destino")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
            top_inst.columns = ["Instituição", "Total"]
            top_inst["Total"] = top_inst["Total"].apply(fmt_brl)
            st.dataframe(top_inst, use_container_width=True, hide_index=True)
        else:
            st.info("Dados de instituição não disponíveis")
    
    st.markdown("#### 🎓 Modalidades Mais Frequentes")
    if "modalidade" in df_filtrado.columns:
        top_mod = df_filtrado["modalidade"].value_counts().head(10).reset_index()
        top_mod.columns = ["Modalidade", "Quantidade"]
        fig_mod = px.bar(top_mod, x="Quantidade", y="Modalidade", orientation="h",
                         title="Top 10 Modalidades", color="Quantidade", color_continuous_scale="Oranges")
        fig_mod.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_mod, use_container_width=True)
    else:
        st.info("Dados de modalidade não disponíveis")

# TAB 5: ESTATÍSTICAS
with tab5:
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("#### 📦 Boxplot")
        fig_box = px.box(df_filtrado, y="valor_pago", title="Distribuição dos valores (outliers)")
        fig_box.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_box, use_container_width=True)
        
        st.markdown("#### 📊 Estatísticas Descritivas")
        stats = {
            "Média": fmt_brl(df_filtrado["valor_pago"].mean()),
            "Mediana": fmt_brl(df_filtrado["valor_pago"].median()),
            "Desvio Padrão": fmt_brl(df_filtrado["valor_pago"].std()),
            "Mínimo": fmt_brl(df_filtrado["valor_pago"].min()),
            "Máximo": fmt_brl(df_filtrado["valor_pago"].max()),
        }
        st.json(stats)
    
    with col_s2:
        st.markdown("#### 📈 Histograma + Densidade")
        fig_hist = px.histogram(df_filtrado, x="valor_pago", nbins=50, marginal="violin",
                                title="Histograma com curva de densidade")
        fig_hist.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown("#### 🔥 Correlação")
        if "ano" in df_filtrado.columns and "valor_pago" in df_filtrado.columns:
            corr_data = df_filtrado[["ano", "valor_pago"]].dropna()
            corr_matrix = corr_data.corr()
            fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlação Ano × Investimento")
            fig_corr.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_corr, use_container_width=True)

# TAB 6: ANÁLISES AVANÇADAS
with tab6:
    st.markdown("#### 🧠 Clusterização de Instituições (K-Means)")
    if "nome_conglomerado_financeiro" in df_filtrado.columns and "valor_pago" in df_filtrado.columns:
        cluster_data = df_filtrado.groupby("nome_conglomerado_financeiro").agg({
            "valor_pago": "sum",
            "numero_operacoes": "sum" if "numero_operacoes" in df_filtrado.columns else "count"
        }).reset_index()
        cluster_data = cluster_data.dropna()
        if len(cluster_data) >= 3:
            scaler = StandardScaler()
            features = scaler.fit_transform(cluster_data[["valor_pago", "numero_operacoes"]])
            kmeans = KMeans(n_clusters=min(3, len(cluster_data)), random_state=42, n_init=10)
            cluster_data["cluster"] = kmeans.fit_predict(features)
            fig_cluster = px.scatter(cluster_data, x="valor_pago", y="numero_operacoes", color="cluster",
                                     size="valor_pago", hover_name="nome_conglomerado_financeiro",
                                     title="Clusterização por Investimento × Operações")
            fig_cluster.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig_cluster, use_container_width=True)
        else:
            st.info("Dados insuficientes para clusterização")
    else:
        st.info("Dados insuficientes para clusterização")
    
    st.markdown("#### ⚠️ Detecção de Outliers")
    p99 = df_filtrado["valor_pago"].quantile(0.99)
    outliers = df_filtrado[df_filtrado["valor_pago"] > p99]
    st.metric("Valores acima do percentil 99", f"{len(outliers)} registros", delta=f"Limite: {fmt_brl(p99)}")
    if not outliers.empty:
        with st.expander("Ver outliers"):
            st.dataframe(outliers[["beneficiario", "valor_pago", "instituicao_destino"]].head(20), use_container_width=True)

# ============================================================
# SOBRE O ANALISTA
# ============================================================
st.markdown("---")
st.markdown("""
<div style="background: rgba(18,25,45,0.5); border-radius: 1rem; padding: 1.2rem; margin: 1rem 0;">
    <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
        <div style="flex: 2;">
            <h3 style="margin: 0;">👨‍💻 Raphael Pires</h3>
            <p style="color: #94A3B8; font-size: 0.8rem;">Analista de Dados | SQL | Python | Streamlit | Power BI | Looker Studio</p>
            <p style="color: #94A3B8; font-size: 0.75rem; line-height: 1.4;">
                Especialista em transformar dados brutos em insights estratégicos para tomada de decisão.<br>
                Este dashboard demonstra habilidades em ETL, visualização interativa, machine learning e storytelling com dados.
            </p>
            <p style="margin-top: 0.5rem;">
                <a href="https://www.linkedin.com/in/raphael-pires-caxias/" target="_blank" style="color: #3B82F6;">🔗 LinkedIn</a>
                &nbsp;|&nbsp;
                <a href="https://github.com/raphaelcaxias" target="_blank" style="color: #3B82F6;">🐙 GitHub</a>
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# EXPORTAÇÃO E RODAPÉ
# ============================================================
st.markdown("### 📥 Exportar Dados")
col_exp1, col_exp2 = st.columns(2)
with col_exp1:
    csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("📄 Baixar CSV (dados filtrados)", csv_data, file_name=f"cnpq_analytics_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
with col_exp2:
    st.markdown(f'<a href="{LINK_CSV}" target="_blank" style="text-decoration: none;"><div class="download-btn" style="text-align: center;">📥 Baixar CSV original (Google Drive)</div></a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div class="footer">
    🔬 CNPq Analytics · Fonte: Portal Brasileiro de Dados Abertos (CGU/CNPq)<br>
    Dashboard desenvolvido para portfólio de Análise de Dados – Raphael Pires
</div>
""", unsafe_allow_html=True)
