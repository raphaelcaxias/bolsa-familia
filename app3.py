# appy3.py
# CNPq Analytics Dashboard - Versão Otimizada
# Desenvolvido por: Raphael Pires

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
import re
import logging
import io

# ============================================================
# CONFIGURAÇÃO CENTRALIZADA
# ============================================================
CONFIG = {
    "COLUNAS_OBRIGATORIAS": ["valor_pago"],
    "ENCODINGS": ["latin1", "utf-8", "cp1252"],
    "DELIMITADOR": ";",
    "CLUSTER_DEFAULT": 3,
    "PERCENTIL_OUTLIER": 0.99,
    "MAX_ROWS_TABLE": 100,  # Limite para exibição de tabelas
    "CACHE_TTL": 3600  # Cache em segundos
}

# ============================================================
# LOGGING CONFIG
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ============================================================
# FILTROS DE AVISOS
# ============================================================
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
# CORES E TEMA (fixo)
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

/* Responsividade mobile */
@media (max-width: 768px) {{
    .hero h1 {{ font-size: 2rem; }}
    .block-container {{ padding: 1rem !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES AUXILIARES - FORMATAÇÃO
# ============================================================
def fmt_brl(valor):
    """Formata valor monetário para padrão brasileiro"""
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    try:
        valor_float = float(valor)
        if valor_float >= 1_000_000_000:
            return f"R$ {valor_float/1_000_000_000:.2f}B".replace(".", ",")
        if valor_float >= 1_000_000:
            return f"R$ {valor_float/1_000_000:.2f}M".replace(".", ",")
        if valor_float >= 1_000:
            return f"R$ {valor_float/1_000:.2f}K".replace(".", ",")
        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def fmt_num(valor):
    """Formata número com separador de milhar"""
    if pd.isna(valor):
        return "0"
    try:
        return f"{int(valor):,}".replace(",", ".")
    except:
        return str(valor)

def parse_moeda_br(valor_str):
    """Converte string monetária BR para float"""
    if pd.isna(valor_str):
        return np.nan
    # Remove R$, espaços, pontos de milhar e substitui vírgula decimal por ponto
    limpo = re.sub(r'[R$\s]', '', str(valor_str)).replace('.', '').replace(',', '.').strip()
    try:
        return float(limpo) if limpo else np.nan
    except ValueError:
        return np.nan

# ============================================================
# FUNÇÕES DE MÉTRICAS E ANÁLISE
# ============================================================
@st.cache_data(ttl=CONFIG["CACHE_TTL"])
def calcular_hhi(df, coluna):
    """Calcula Índice Herfindahl-Hirschman (concentração de mercado)"""
    total = df[coluna].sum()
    if total == 0 or total is None:
        return 0
    participacoes = (df[coluna] / total) ** 2
    return participacoes.sum() * 10000

@st.cache_data(ttl=CONFIG["CACHE_TTL"])
def calcular_cagr(serie):
    """Calcula CAGR (Compound Annual Growth Rate)"""
    if len(serie) < 2:
        return 0
    primeiro = serie.iloc[0]
    ultimo = serie.iloc[-1]
    n = len(serie) - 1
    if primeiro is None or primeiro <= 0 or ultimo is None:
        return 0
    return (pow(ultimo/primeiro, 1/n) - 1) * 100

@st.cache_data(ttl=CONFIG["CACHE_TTL"])
def calcular_pareto(df, coluna):
    """Calcula curva de Pareto (80/20)"""
    df_sorted = df.sort_values(coluna, ascending=False).reset_index(drop=True)
    total = df_sorted[coluna].sum()
    if total == 0:
        df_sorted['percentual_acumulado'] = 0
    else:
        df_sorted['percentual_acumulado'] = (df_sorted[coluna].cumsum() / total) * 100
    return df_sorted

@st.cache_data(ttl=CONFIG["CACHE_TTL"])
def calcular_clusterizacao(df, coluna_grupo, colunas_features, n_clusters=None):
    """Realiza clusterização K-Means com cache"""
    if n_clusters is None:
        n_clusters = CONFIG["CLUSTER_DEFAULT"]
    
    # Agrupa dados
    agg_dict = {col: 'sum' if col != coluna_grupo else 'first' for col in colunas_features}
    cluster_data = df.groupby(coluna_grupo).agg(agg_dict).reset_index()
    cluster_data = cluster_data.dropna(subset=colunas_features)
    
    if len(cluster_data) < n_clusters:
        return None, "Dados insuficientes para clusterização"
    
    try:
        scaler = StandardScaler()
        features = scaler.fit_transform(cluster_data[colunas_features])
        kmeans = KMeans(n_clusters=min(n_clusters, len(cluster_data)), random_state=42, n_init=10)
        cluster_data["cluster"] = kmeans.fit_predict(features)
        return cluster_data, None
    except Exception as e:
        logger.error(f"Erro na clusterização: {e}")
        return None, str(e)

# ============================================================
# CARREGAMENTO E VALIDAÇÃO DE DADOS
# ============================================================
@st.cache_data(ttl=CONFIG["CACHE_TTL"])
def carregar_dados(uploaded_file):
    """Carrega CSV com validação robusta e cache"""
    logger.info(f"Iniciando carregamento: {uploaded_file.name}")
    
    for enc in CONFIG["ENCODINGS"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file, 
                delimiter=CONFIG["DELIMITADOR"], 
                encoding=enc, 
                low_memory=False
            )
            # Normaliza nomes de colunas
            df.columns = df.columns.str.lower().str.strip()
            
            # Valida colunas obrigatórias
            missing_cols = set(CONFIG["COLUNAS_OBRIGATORIAS"]) - set(df.columns)
            if missing_cols:
                logger.warning(f"Colunas faltando para encoding {enc}: {missing_cols}")
                continue
            
            # Processa valor_pago
            if 'valor_pago' in df.columns:
                df['valor_pago'] = df['valor_pago'].apply(parse_moeda_br)
                df = df.dropna(subset=['valor_pago'])
                df = df[df['valor_pago'] > 0]
            
            # Processa datas
            if 'data_inicio_processo' in df.columns:
                df['data_inicio_processo'] = pd.to_datetime(
                    df['data_inicio_processo'], errors='coerce', dayfirst=True
                )
                df['ano'] = df['data_inicio_processo'].dt.year
            
            # Mapeia regiões
            regioes_map = {
                'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste', 
                'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte', 
                'EX': 'Exterior', 'NI': 'Não Informado'
            }
            if 'regiao' in df.columns:
                df['regiao_nome'] = df['regiao'].map(regioes_map).fillna(df['regiao'])
            
            logger.info(f"Carregado {len(df)} registros com encoding {enc}")
            return df, enc
            
        except UnicodeDecodeError:
            logger.debug(f"Encoding {enc} falhou, tentando próximo...")
            continue
        except Exception as e:
            logger.error(f"Erro ao processar com encoding {enc}: {e}")
            continue
    
    logger.error("Nenhum encoding funcionou para carregar o arquivo")
    return None, None

# ============================================================
# FUNÇÃO PARA DOWNLOAD DE GRÁFICOS
# ============================================================
def download_graph_button(fig, filename, label="📥 Baixar gráfico"):
    """Cria botão de download para gráfico Plotly"""
    try:
        img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
        return st.download_button(
            label=label,
            data=img_bytes,
            file_name=f"{filename}.png",
            mime="image/png",
            key=f"dl_{filename}"
        )
    except Exception as e:
        logger.warning(f"Não foi possível gerar download do gráfico: {e}")
        return None

# ============================================================
# LINK PARA DATASET DE EXEMPLO
# ============================================================
LINK_CSV = "https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub"

# ============================================================
# PÁGINA INICIAL - HERO SECTION
# ============================================================
def render_hero():
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
        st.markdown(f"""
        <div style="background: rgba(18,25,45,0.5); border-radius: 1rem; padding: 0.6rem;">
            <h4 style="margin: 0;">📌 Fonte</h4>
            <p style="font-size: 0.65rem;">Portal Dados Abertos (CGU/CNPq)</p>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        st.markdown(f"""
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
# SIDEBAR - CONTROLES E FILTROS
# ============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🎛️ Central Analítica")
        st.markdown(f"📥 [Baixar CSV exemplo]({LINK_CSV})")
        st.markdown("---")
        
        uploaded_file = st.file_uploader("📂 Carregar CSV (bolsa_familia.csv)", type=["csv"])
        
        if uploaded_file is None:
            st.info("👈 Envie o arquivo para iniciar a análise")
            return None, None
        
        with st.spinner("🔄 Processando arquivo..."):
            df, encoding = carregar_dados(uploaded_file)
        
        if df is None:
            st.error(f"❌ Erro ao carregar CSV. Verifique:\n• Separador: `{CONFIG['DELIMITADOR']}`\n• Encoding suportado: {CONFIG['ENCODINGS']}\n• Coluna obrigatória: `{CONFIG['COLUNAS_OBRIGATORIAS'][0]}`")
            return None, None
        
        st.success(f"✅ {df.shape[0]:,} registros carregados")
        st.caption(f"📁 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        st.markdown("---")
        st.markdown("### 🧬 Filtros")
        df_filtrado = df.copy()
        
        # Filtro por ano
        if "ano" in df.columns:
            anos = sorted(df["ano"].dropna().unique().astype(int))
            if len(anos) > 1:
                ano_sel = st.slider("Ano", min(anos), max(anos), (min(anos), max(anos)), step=1)
                df_filtrado = df_filtrado[(df_filtrado["ano"] >= ano_sel[0]) & (df_filtrado["ano"] <= ano_sel[1])]
        
        # Filtro por área do conhecimento
        if "grande_area" in df.columns:
            areas = sorted(df["grande_area"].dropna().unique())
            areas_sel = st.multiselect("Grande Área", areas, default=areas[:6] if len(areas)>6 else areas)
            if areas_sel:
                df_filtrado = df_filtrado[df_filtrado["grande_area"].isin(areas_sel)]
        
        # Filtro por região
        if "regiao_nome" in df.columns:
            regioes = sorted(df["regiao_nome"].dropna().unique())
            reg_sel = st.multiselect("Região", regioes, default=regioes)
            if reg_sel:
                df_filtrado = df_filtrado[df_filtrado["regiao_nome"].isin(reg_sel)]
        
        return df_filtrado, df

# ============================================================
# KPIs PRINCIPAIS
# ============================================================
def render_kpis(df_filtrado):
    total_volume = df_filtrado["valor_pago"].sum()
    total_bolsas = df_filtrado.shape[0]
    ticket_medio = total_volume / total_bolsas if total_bolsas > 0 else 0
    n_pesq = df_filtrado["beneficiario"].nunique() if "beneficiario" in df_filtrado.columns else 0
    n_inst = df_filtrado["instituicao_destino"].nunique() if "instituicao_destino" in df_filtrado.columns else 0

    col1, col2, col3, col4 = st.columns(4)

    # CAGR para delta
    if "ano" in df_filtrado.columns:
        evol_ano = df_filtrado.groupby("ano")["valor_pago"].sum()
        cagr = calcular_cagr(evol_ano)
        cagr_str = f"CAGR: {cagr:+.1f}%" if cagr != 0 and not pd.isna(cagr) else ""
    else:
        cagr_str = ""

    with col1:
        st.metric(
            "💰 INVESTIMENTO TOTAL", 
            fmt_brl(total_volume), 
            delta=cagr_str,
            help="CAGR = Taxa de crescimento anual composta"
        )
    with col2:
        st.metric("🎓 BOLSAS", fmt_num(total_bolsas))
    with col3:
        st.metric("👥 PESQUISADORES", fmt_num(n_pesq))
    with col4:
        st.metric("🏛️ INSTITUIÇÕES", fmt_num(n_inst))

    st.caption(f"📊 Ticket médio: {fmt_brl(ticket_medio)} | Média por pesquisador: {fmt_brl(total_volume/n_pesq) if n_pesq>0 else 'N/A'}")
    
    return total_volume, total_bolsas, ticket_medio, n_pesq, n_inst

# ============================================================
# RESUMO EXECUTIVO COM INSIGHTS
# ============================================================
def render_resumo(df_filtrado, total_volume):
    st.markdown("## 🔍 Resumo Executivo")

    insights = []

    if "regiao_nome" in df_filtrado.columns and not df_filtrado["regiao_nome"].isna().all():
        reg_share = df_filtrado.groupby("regiao_nome")["valor_pago"].sum()
        if not reg_share.empty:
            top_reg = reg_share.idxmax()
            pct_reg = (reg_share.max() / total_volume) * 100 if total_volume > 0 else 0
            insights.append(f"📍 A região **{top_reg}** concentra **{pct_reg:.1f}%** do investimento total.")

    if "grande_area" in df_filtrado.columns and not df_filtrado["grande_area"].isna().all():
        area_share = df_filtrado.groupby("grande_area")["valor_pago"].sum()
        if not area_share.empty:
            top_area = area_share.idxmax()
            pct_area = (area_share.max() / total_volume) * 100 if total_volume > 0 else 0
            insights.append(f"🧬 A área **{top_area}** lidera com **{pct_area:.1f}%** dos recursos.")

    if "ano" in df_filtrado.columns:
        evol_ano = df_filtrado.groupby("ano")["valor_pago"].sum()
        if len(evol_ano) >= 2 and evol_ano.iloc[-2] > 0:
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
# TAB 1: EVOLUÇÃO TEMPORAL
# ============================================================
def render_tab_evolucao(df_filtrado):
    st.markdown("### 📈 Evolução Temporal")
    
    if "ano" not in df_filtrado.columns or df_filtrado["ano"].isna().all():
        st.info("ℹ️ Coluna 'ano' não disponível para análise temporal.")
        return
    
    evol_data = df_filtrado.groupby("ano")["valor_pago"].sum().reset_index()
    
    fig_evol = px.line(
        evol_data, x="ano", y="valor_pago", markers=True,
        title="Evolução do Investimento por Ano",
        labels={"ano": "Ano", "valor_pago": "Investimento (R$)"}
    )
    fig_evol.update_layout(template="plotly_dark", height=450)
    fig_evol.update_traces(line=dict(width=3, color=COR_AZUL), marker=dict(size=8, color=COR_VERDE))
    st.plotly_chart(fig_evol, use_container_width=True)
    download_graph_button(fig_evol, "evolucao_investimento", "📥 Baixar gráfico (PNG)")
    
    # Projeção linear
    if len(evol_data) >= 3:
        with st.expander("🔮 Projeção para próximos 2 anos", expanded=False):
            X = np.array(evol_data["ano"]).reshape(-1, 1)
            y = evol_data["valor_pago"].values
            model = LinearRegression()
            model.fit(X, y)
            r2 = model.score(X, y)
            
            anos_futuros = np.arange(evol_data["ano"].max() + 1, evol_data["ano"].max() + 3).reshape(-1, 1)
            pred = model.predict(anos_futuros)
            proj_data = pd.DataFrame({"ano": anos_futuros.flatten(), "projecao": pred})
            
            st.caption(f"📊 Modelo: Regressão Linear | R² = {r2:.3f}")
            
            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(
                x=evol_data["ano"], y=evol_data["valor_pago"], 
                mode="lines+markers", name="Histórico",
                line=dict(color=COR_AZUL, width=2)
            ))
            fig_proj.add_trace(go.Scatter(
                x=proj_data["ano"], y=proj_data["projecao"], 
                mode="lines+markers", name="Projeção",
                line=dict(color=COR_VERDE, width=2, dash="dash")
            ))
            fig_proj.update_layout(
                template="plotly_dark", height=400,
                title="Projeção Linear de Investimento",
                xaxis_title="Ano", yaxis_title="Investimento (R$)"
            )
            st.plotly_chart(fig_proj, use_container_width=True)

# ============================================================
# TAB 2: DISTRIBUIÇÃO REGIONAL
# ============================================================
def render_tab_regional(df_filtrado):
    st.markdown("### 🗺️ Distribuição Regional")
    
    if "regiao_nome" not in df_filtrado.columns or df_filtrado["regiao_nome"].isna().all():
        st.info("ℹ️ Dados regionais não disponíveis.")
        return
    
    reg_data = df_filtrado.groupby("regiao_nome")["valor_pago"].sum().reset_index()
    reg_data.columns = ["Região", "Valor"]
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        fig_bar = px.bar(
            reg_data, x="Região", y="Valor", color="Valor",
            color_continuous_scale="Blues",
            text=reg_data["Valor"].apply(fmt_brl),
            title="Investimento por Região",
            labels={"Valor": "Investimento (R$)"}
        )
        fig_bar.update_layout(template="plotly_dark", height=450)
        fig_bar.update_traces(textposition="outside", textfont=dict(size=9))
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col_r2:
        fig_pie = px.pie(
            reg_data, names="Região", values="Valor", hole=0.4,
            title="Participação por Região",
            color_discrete_sequence=[COR_AZUL, COR_VERDE, COR_AMARELO, COR_VERMELHO, "#64748B", "#8B5CF6"]
        )
        fig_pie.update_layout(template="plotly_dark", height=450)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Ticket médio por região
    ticket_reg = df_filtrado.groupby("regiao_nome")["valor_pago"].mean().reset_index()
    ticket_reg.columns = ["Região", "Ticket Médio"]
    fig_ticket = px.bar(
        ticket_reg, x="Região", y="Ticket Médio", color="Ticket Médio",
        color_continuous_scale="Greens", title="Ticket Médio por Região",
        labels={"Ticket Médio": "Valor Médio (R$)"}
    )
    fig_ticket.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_ticket, use_container_width=True)

# ============================================================
# TAB 3: ÁREAS DO CONHECIMENTO
# ============================================================
def render_tab_areas(df_filtrado):
    st.markdown("### 🧬 Áreas do Conhecimento")
    
    if "grande_area" not in df_filtrado.columns or df_filtrado["grande_area"].isna().all():
        st.info("ℹ️ Dados de área do conhecimento não disponíveis.")
        return
    
    area_data = df_filtrado.groupby("grande_area")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
    area_data.columns = ["Área", "Valor"]
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        fig_area = px.bar(
            area_data, x="Valor", y="Área", orientation="h",
            color="Valor", color_continuous_scale="Viridis",
            text=area_data["Valor"].apply(fmt_brl),
            title="Top 10 Áreas com Maior Investimento",
            labels={"Valor": "Investimento (R$)"}
        )
        fig_area.update_layout(template="plotly_dark", height=500)
        fig_area.update_traces(textposition="outside", textfont=dict(size=9))
        st.plotly_chart(fig_area, use_container_width=True)
    
    with col_a2:
        fig_treemap = px.treemap(
            area_data, path=["Área"], values="Valor",
            title="Distribuição do Investimento por Área",
            color="Valor", color_continuous_scale="Blues"
        )
        fig_treemap.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Análise de Pareto
    with st.expander("📊 Análise de Pareto (80/20)", expanded=True):
        pareto_data = calcular_pareto(area_data.copy(), "Valor")
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pareto.add_trace(
            go.Bar(x=pareto_data["Área"], y=pareto_data["Valor"], name="Investimento", marker_color=COR_AZUL),
            secondary_y=False
        )
        fig_pareto.add_trace(
            go.Scatter(x=pareto_data["Área"], y=pareto_data["percentual_acumulado"], 
                      name="% Acumulado", mode="lines+markers", 
                      line=dict(color=COR_VERMELHO, width=3)),
            secondary_y=True
        )
        fig_pareto.update_layout(
            template="plotly_dark", height=400,
            title="Curva de Pareto: Concentração do Investimento",
            xaxis_title="Área do Conhecimento",
            yaxis_title="Investimento (R$)",
            yaxis2_title="% Acumulado",
            yaxis2=dict(range=[0, 105])
        )
        fig_pareto.add_hline(y=80, line_dash="dot", line_color=COR_AMARELO, annotation_text="80%", annotation_position="top right")
        st.plotly_chart(fig_pareto, use_container_width=True)

# ============================================================
# TAB 4: RANKINGS
# ============================================================
def render_tab_rankings(df_filtrado):
    st.markdown("### 🏆 Rankings")
    
    col_r1, col_r2 = st.columns(2)
    
    # Top Pesquisadores
    with col_r1:
        st.markdown("#### 👤 Top 10 Pesquisadores")
        if "beneficiario" in df_filtrado.columns:
            top_people = df_filtrado.groupby("beneficiario")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
            top_people.columns = ["Pesquisador", "Total"]
            top_people["Total_fmt"] = top_people["Total"].apply(fmt_brl)
            total_ref = df_filtrado["valor_pago"].sum()
            top_people["Participação"] = top_people["Total"].apply(lambda x: f"{(x / total_ref * 100):.1f}%" if total_ref > 0 else "0%")
            
            display_df = top_people[["Pesquisador", "Total_fmt", "Participação"]].copy()
            display_df.columns = ["Pesquisador", "Total Recebido", "Participação"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Busca de pesquisador
            with st.expander("🔍 Buscar pesquisador específico"):
                busca = st.text_input("Digite parte do nome", key="busca_pesq")
                if busca:
                    resultados = df_filtrado[df_filtrado["beneficiario"].str.contains(busca, case=False, na=False)]
                    if not resultados.empty:
                        st.dataframe(
                            resultados[["beneficiario", "valor_pago", "instituicao_destino"]].head(CONFIG["MAX_ROWS_TABLE"]), 
                            use_container_width=True
                        )
                        st.caption(f"Exibindo até {CONFIG['MAX_ROWS_TABLE']} resultados")
                    else:
                        st.info("Nenhum resultado encontrado")
        else:
            st.info("ℹ️ Dados de beneficiário não disponíveis")
    
    # Top Instituições
    with col_r2:
        st.markdown("#### 🏛️ Top 10 Instituições")
        if "instituicao_destino" in df_filtrado.columns:
            top_inst = df_filtrado.groupby("instituicao_destino")["valor_pago"].sum().sort_values(ascending=False).head(10).reset_index()
            top_inst.columns = ["Instituição", "Total"]
            top_inst["Total_fmt"] = top_inst["Total"].apply(fmt_brl)
            
            display_inst = top_inst[["Instituição", "Total_fmt"]].copy()
            display_inst.columns = ["Instituição", "Total Recebido"]
            st.dataframe(display_inst, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Dados de instituição não disponíveis")
    
    # Modalidades
    st.markdown("#### 🎓 Modalidades Mais Frequentes")
    if "modalidade" in df_filtrado.columns:
        top_mod = df_filtrado["modalidade"].value_counts().head(10).reset_index()
        top_mod.columns = ["Modalidade", "Quantidade"]
        fig_mod = px.bar(
            top_mod, x="Quantidade", y="Modalidade", orientation="h",
            title="Top 10 Modalidades de Bolsa", color="Quantidade", color_continuous_scale="Oranges"
        )
        fig_mod.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_mod, use_container_width=True)
    else:
        st.info("ℹ️ Dados de modalidade não disponíveis")

# ============================================================
# TAB 5: ESTATÍSTICAS
# ============================================================
def render_tab_estatisticas(df_filtrado):
    st.markdown("### 📊 Estatísticas Descritivas")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown("#### 📦 Distribuição dos Valores")
        fig_box = px.box(
            df_filtrado, y="valor_pago", title="Boxplot: Distribuição e Outliers",
            labels={"valor_pago": "Valor Pago (R$)"}
        )
        fig_box.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_box, use_container_width=True)
        
        st.markdown("#### 📋 Métricas Principais")
        stats = {
            "Média": fmt_brl(df_filtrado["valor_pago"].mean()),
            "Mediana": fmt_brl(df_filtrado["valor_pago"].median()),
            "Desvio Padrão": fmt_brl(df_filtrado["valor_pago"].std()),
            "Mínimo": fmt_brl(df_filtrado["valor_pago"].min()),
            "Máximo": fmt_brl(df_filtrado["valor_pago"].max()),
            "Q1 (25%)": fmt_brl(df_filtrado["valor_pago"].quantile(0.25)),
            "Q3 (75%)": fmt_brl(df_filtrado["valor_pago"].quantile(0.75)),
        }
        st.json(stats)
    
    with col_s2:
        st.markdown("#### 📈 Histograma com Densidade")
        fig_hist = px.histogram(
            df_filtrado, x="valor_pago", nbins=50, marginal="violin",
            title="Distribuição de Frequência dos Valores",
            labels={"valor_pago": "Valor Pago (R$)"}
        )
        fig_hist.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Correlação se houver ano
        if "ano" in df_filtrado.columns:
            with st.expander("🔗 Correlação Ano × Investimento"):
                corr_data = df_filtrado[["ano", "valor_pago"]].dropna()
                if len(corr_data) > 1:
                    corr_matrix = corr_data.corr()
                    fig_corr = px.imshow(
                        corr_matrix, text_auto=".2f", aspect="auto", 
                        title="Matriz de Correlação", color_continuous_scale="RdBu_r"
                    )
                    fig_corr.update_layout(template="plotly_dark", height=350)
                    st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.info("Dados insuficientes para calcular correlação")

# ============================================================
# TAB 6: ANÁLISES AVANÇADAS
# ============================================================
def render_tab_avancadas(df_filtrado):
    st.markdown("### 🤖 Análises Avançadas")
    
    # Clusterização
    with st.expander("🧠 Clusterização de Instituições (K-Means)", expanded=True):
        if "instituicao_destino" in df_filtrado.columns and "valor_pago" in df_filtrado.columns:
            n_clusters = st.slider("Número de clusters", 2, 6, CONFIG["CLUSTER_DEFAULT"], key="n_clusters")
            
            with st.spinner("Processando clusterização..."):
                cluster_result, error = calcular_clusterizacao(
                    df_filtrado, 
                    coluna_grupo="instituicao_destino",
                    colunas_features=["valor_pago"],
                    n_clusters=n_clusters
                )
            
            if cluster_result is not None:
                fig_cluster = px.scatter(
                    cluster_result, x="valor_pago", y=cluster_result.index, color="cluster",
                    size="valor_pago", hover_name="instituicao_destino",
                    title=f"Clusterização: {n_clusters} Grupos de Instituições",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    labels={"valor_pago": "Investimento Total (R$)", "index": "Instituição"}
                )
                fig_cluster.update_layout(template="plotly_dark", height=500, yaxis=dict(visible=False))
                st.plotly_chart(fig_cluster, use_container_width=True)
                
                # Resumo dos clusters
                st.markdown("##### 📊 Resumo por Cluster")
                cluster_summary = cluster_result.groupby("cluster")["valor_pago"].agg(["count", "sum", "mean"]).reset_index()
                cluster_summary.columns = ["Cluster", "Qtd Instituições", "Investimento Total", "Média por Instituição"]
                cluster_summary["Investimento Total"] = cluster_summary["Investimento Total"].apply(fmt_brl)
                cluster_summary["Média por Instituição"] = cluster_summary["Média por Instituição"].apply(fmt_brl)
                st.dataframe(cluster_summary, use_container_width=True, hide_index=True)
            else:
                st.warning(f"⚠️ {error}")
        else:
            st.info("ℹ️ Dados insuficientes para clusterização")
    
    # Detecção de Outliers
    with st.expander("⚠️ Detecção de Outliers", expanded=False):
        p99 = df_filtrado["valor_pago"].quantile(CONFIG["PERCENTIL_OUTLIER"])
        outliers = df_filtrado[df_filtrado["valor_pago"] > p99]
        
        st.metric(
            "Registros acima do percentil 99", 
            f"{len(outliers)}", 
            delta=f"Limite: {fmt_brl(p99)}",
            help=f"Valores acima de {CONFIG['PERCENTIL_OUTLIER']*100}% da distribuição"
        )
        
        if not outliers.empty:
            with st.expander(f"Ver {len(outliers)} outliers"):
                cols_display = [c for c in ["beneficiario", "valor_pago", "instituicao_destino", "grande_area"] if c in outliers.columns]
                outliers_display = outliers[cols_display].copy()
                if "valor_pago" in outliers_display.columns:
                    outliers_display["valor_pago_fmt"] = outliers_display["valor_pago"].apply(fmt_brl)
                st.dataframe(outliers_display.head(CONFIG["MAX_ROWS_TABLE"]), use_container_width=True)
                st.caption(f"Exibindo até {CONFIG['MAX_ROWS_TABLE']} registros")

# ============================================================
# EXPORTAÇÃO E RODAPÉ
# ============================================================
def render_export_footer(df_filtrado):
    st.markdown("---")
    st.markdown("### 📥 Exportar Dados")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # CSV dos dados filtrados
        csv_buffer = io.StringIO()
        df_filtrado.to_csv(csv_buffer, index=False, sep=";", encoding="utf-8-sig")
        csv_bytes = csv_buffer.getvalue().encode("utf-8")
        
        st.download_button(
            "📄 Baixar CSV (dados filtrados)",
            data=csv_bytes,
            file_name=f"cnpq_analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            key="btn_csv_filtrado"
        )
    
    with col_exp2:
        st.markdown(f'<a href="{LINK_CSV}" target="_blank" style="text-decoration: none;"><div class="download-btn" style="text-align: center;">📥 Baixar CSV original (Google Drive)</div></a>', unsafe_allow_html=True)
    
    # Rodapé
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        🔬 CNPq Analytics · Fonte: Portal Brasileiro de Dados Abertos (CGU/CNPq)<br>
        Dashboard desenvolvido para portfólio de Análise de Dados – Raphael Pires<br>
        <span style="color: {COR_TEXTO_MUTED};">Versão: appy3.py · Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================
def main():
    logger.info("Iniciando aplicação CNPq Analytics")
    
    # Renderiza hero section
    render_hero()
    
    # Renderiza sidebar e carrega dados
    df_filtrado, df_original = render_sidebar()
    
    if df_filtrado is None:
        # Aguarda upload
        st.markdown("<br>" * 3, unsafe_allow_html=True)
        render_export_footer(pd.DataFrame())  # Rodapé mesmo sem dados
        return
    
    # KPIs principais
    render_kpis(df_filtrado)
    
    # Resumo executivo
    render_resumo(df_filtrado, df_filtrado["valor_pago"].sum())
    
    # Tabs de análise
    st.markdown("## 📊 Análises Interativas")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Evolução", "🗺️ Regional", "🧬 Áreas",
        "🏆 Rankings", "📊 Estatísticas", "🤖 Avançadas"
    ])
    
    with tab1:
        render_tab_evolucao(df_filtrado)
    
    with tab2:
        render_tab_regional(df_filtrado)
    
    with tab3:
        render_tab_areas(df_filtrado)
    
    with tab4:
        render_tab_rankings(df_filtrado)
    
    with tab5:
        render_tab_estatisticas(df_filtrado)
    
    with tab6:
        render_tab_avancadas(df_filtrado)
    
    # Sobre o analista
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
    
    # Exportação e rodapé
    render_export_footer(df_filtrado)
    
    logger.info("Aplicação renderizada com sucesso")

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
