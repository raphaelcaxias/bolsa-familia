import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Dashboard CNPq - Bolsas de Pesquisa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PREMIUM (unificado)
# ============================================
st.markdown("""
<style>
/* ===== FUNDO ===== */
.stApp {
    background: #0f172a;
    color: white;
}

/* ===== REMOVE MENU STREAMLIT ===== */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* ===== HERO ===== */
.hero {
    padding: 2.5rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #111827, #1e293b);
    margin-bottom: 30px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 10px;
    color: white;
}

.hero p {
    color: #94a3b8;
    font-size: 18px;
}

/* ===== METRIC CARDS ===== */
.metric-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 28px;
    border-radius: 24px;
    transition: 0.3s;
    box-shadow: 0 8px 32px rgba(0,0,0,0.20);
}

.metric-card:hover {
    transform: translateY(-6px);
}

.metric-icon {
    font-size: 42px;
    margin-bottom: 15px;
}

.metric-title {
    color: #94a3b8;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    color: white;
    font-size: 34px;
    font-weight: 700;
    margin-top: 10px;
}

/* ===== INSIGHTS ===== */
.insight-card {
    background: rgba(255,255,255,0.04);
    border-left: 5px solid #3b82f6;
    padding: 22px;
    border-radius: 18px;
    margin-top: 10px;
    margin-bottom: 15px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.insight-card h4 {
    color: white;
    margin-bottom: 10px;
}

.insight-card p {
    color: #cbd5e1;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ===== TÍTULOS ===== */
h1, h2, h3, .stMarkdown h2, .stMarkdown h3 {
    color: white !important;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
}

/* ===== BOTÕES ===== */
.stDownloadButton button {
    width: 100%;
    border-radius: 14px;
    border: none;
    padding: 12px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
    font-weight: 600;
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    background-color: #1e293b;
    border-radius: 12px;
    color: white;
}

/* ===== CONTAINERS ===== */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# DICIONÁRIOS PARA LEGENDA
# ============================================
REGIOES_MAP = {
    'SE': 'Sudeste', 'SU': 'Sul', 'NE': 'Nordeste',
    'CO': 'Centro-Oeste', 'N': 'Norte', 'NO': 'Norte',
    'EX': 'Exterior', 'NI': 'Não Informado'
}

def formatar_moeda(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def carregar_dados(uploaded_file):
    """Carrega e limpa os dados"""
    encodings = ['latin1', 'utf-8', 'ISO-8859-1', 'cp1252']
    separadores = [';', ',']
    
    for encoding in encodings:
        for sep in separadores:
            try:
                uploaded_file.seek(0)
                df_test = pd.read_csv(uploaded_file, delimiter=sep, encoding=encoding, nrows=5)
                if 5 < len(df_test.columns) < 50:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, delimiter=sep, encoding=encoding, low_memory=False)
                    df.columns = df.columns.str.lower().str.strip()
                    
                    # Converte valor_pago
                    if 'valor_pago' in df.columns:
                        df['valor_pago'] = (
                            df['valor_pago']
                            .astype(str)
                            .str.replace(',', '.', regex=False)
                            .str.extract(r'(\d+\.?\d*)', expand=False)
                        )
                        df['valor_pago'] = pd.to_numeric(df['valor_pago'], errors='coerce')
                    
                    df = df.dropna(subset=['valor_pago'])
                    
                    if 'data_inicio_processo' in df.columns:
                        df['data_inicio_processo'] = pd.to_datetime(df['data_inicio_processo'], errors='coerce')
                        df['ano'] = df['data_inicio_processo'].dt.year
                    
                    if 'regiao' in df.columns:
                        df['regiao_nome'] = df['regiao'].map(REGIOES_MAP).fillna(df['regiao'])
                    
                    return df, encoding, sep
            except:
                continue
    
    return None, None, None

# ============================================
# HERO SECTION
# ============================================
st.markdown(f"""
<div class="hero">
    <h1>📊 Dashboard CNPq</h1>
    <p>Plataforma estratégica de análise de investimentos em pesquisa e desenvolvimento no Brasil.</p>
    <p style="margin-top:15px;">📅 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Controle Analítico")
    st.markdown("Explore os dados de investimento científico do Brasil.")
    st.divider()
    
    uploaded_file = st.file_uploader(
        "📤 Envie o arquivo CSV",
        type=["csv"],
        help="Arquivo bolsa_familia.csv do Google Drive"
    )
    
    st.markdown("---")
    st.markdown("🔗 **Baixe o CSV original:**")
    st.markdown("[Clique aqui para baixar](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)")

# ============================================
# PROCESSAMENTO PRINCIPAL
# ============================================
if uploaded_file is not None:
    with st.spinner("📥 Processando 110MB de dados... Isso leva ~30 segundos"):
        df, encoding, sep = carregar_dados(uploaded_file)
    
    if df is not None:
        st.success(f"✅ Dados carregados: {df.shape[0]:,} registros válidos")
        
        # ========================================
        # FILTROS
        # ========================================
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Filtros")
        
        df_filtrado = df.copy()
        
        if 'regiao_nome' in df.columns:
            regioes = sorted(df['regiao_nome'].dropna().unique())
            regioes_sel = st.sidebar.multiselect("📍 Região", regioes, default=regioes)
            if regioes_sel:
                df_filtrado = df_filtrado[df_filtrado['regiao_nome'].isin(regioes_sel)]
        
        if 'ano' in df.columns:
            anos_validos = sorted(df['ano'].dropna().unique())
            if len(anos_validos) > 1:
                ano_min, ano_max = int(min(anos_validos)), int(max(anos_validos))
                anos_sel = st.sidebar.slider("📅 Período", ano_min, ano_max, (ano_min, ano_max))
                df_filtrado = df_filtrado[(df_filtrado['ano'] >= anos_sel[0]) & (df_filtrado['ano'] <= anos_sel[1])]
        
        if 'grande_area' in df.columns:
            areas = sorted(df['grande_area'].dropna().unique())
            areas_sel = st.sidebar.multiselect("🧬 Grande Área", areas, default=areas[:5] if len(areas) > 5 else areas)
            if areas_sel:
                df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(areas_sel)]
        
        if df_filtrado.shape[0] < df.shape[0]:
            st.info(f"🔍 Filtros aplicados: exibindo {df_filtrado.shape[0]:,} de {df.shape[0]:,} registros ({100*df_filtrado.shape[0]/df.shape[0]:.1f}%)")
        
        # ========================================
        # KPIs
        # ========================================
        st.markdown("## 📈 Indicadores Estratégicos")
        
        col1, col2, col3, col4 = st.columns(4, gap="large")
        
        total_investido = df_filtrado['valor_pago'].sum()
        total_pesquisadores = df_filtrado['beneficiario'].nunique()
        total_instituicoes = df_filtrado['instituicao_destino'].nunique()
        ticket_medio = df_filtrado['valor_pago'].mean()
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-title">Investimento Total</div>
                <div class="metric-value">{formatar_moeda(total_investido)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-title">Pesquisadores</div>
                <div class="metric-value">{total_pesquisadores:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🏫</div>
                <div class="metric-title">Instituições</div>
                <div class="metric-value">{total_instituicoes:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-title">Ticket Médio</div>
                <div class="metric-value">{formatar_moeda(ticket_medio)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ========================================
        # GRÁFICO 1: INVESTIMENTO POR ÁREA
        # ========================================
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1.7, 1], gap="large")
        
        with col1:
            st.markdown("## 🧬 Investimento por Área")
            
            if 'grande_area' in df_filtrado.columns:
                area_invest = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                area_invest.columns = ['Área', 'Valor']
                
                fig = px.bar(
                    area_invest,
                    x='Área',
                    y='Valor',
                    color='Valor',
                    color_continuous_scale=['#06b6d4', '#3b82f6', '#6366f1']
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"),
                    title_font=dict(size=22),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=500,
                    coloraxis_showscale=False,
                    xaxis_tickangle=-45
                )
                fig.update_traces(
                    marker_line_width=0,
                    opacity=0.92,
                    texttemplate='R$ %{y:,.0f}',
                    textposition='outside',
                    hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("## 🔍 Insights")
            
            # Calcula insights reais
            if 'regiao_nome' in df_filtrado.columns:
                invest_regiao = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
                if len(invest_regiao) > 0:
                    regiao_top = invest_regiao.idxmax()
                    perc_top = (invest_regiao.max() / total_investido) * 100
                    
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>📌 Concentração Regional</h4>
                        <p>A região <b>{regiao_top}</b> concentra <b>{perc_top:.1f}%</b> do investimento total.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            if 'ano' in df_filtrado.columns and len(df_filtrado['ano'].unique()) > 1:
                invest_ano = df_filtrado.groupby('ano')['valor_pago'].sum()
                if len(invest_ano) > 1:
                    var_pct = ((invest_ano.iloc[-1] - invest_ano.iloc[-2]) / invest_ano.iloc[-2]) * 100
                    cor = "positivo" if var_pct > 0 else "negativo"
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>📈 Crescimento</h4>
                        <p>Variação entre {invest_ano.index[-2]} e {invest_ano.index[-1]}: <b style="color:{'#10b981' if var_pct>0 else '#ef4444'}">{var_pct:+.1f}%</b></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            if 'regiao_nome' in df_filtrado.columns:
                invest_regiao = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
                if len(invest_regiao) > 1 and invest_regiao.min() > 0:
                    desigualdade = invest_regiao.max() / invest_regiao.min()
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>⚖️ Desigualdade</h4>
                        <p>A diferença entre a maior e menor região é de <b>{desigualdade:.1f}x</b>.</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # ========================================
        # GRÁFICO 2: EVOLUÇÃO TEMPORAL
        # ========================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## 📅 Evolução Temporal")
        
        if 'ano' in df_filtrado.columns:
            invest_ano = df_filtrado.groupby('ano')['valor_pago'].sum().reset_index()
            invest_ano = invest_ano.dropna()
            
            fig2 = px.line(
                invest_ano,
                x='ano',
                y='valor_pago',
                markers=True
            )
            fig2.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=500,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="Ano",
                yaxis_title="Investimento (R$)"
            )
            fig2.update_traces(
                line=dict(width=4, color='#3b82f6'),
                marker=dict(size=10, color='#6366f1'),
                hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # ========================================
        # EXPORTAÇÃO
        # ========================================
        st.markdown("## 📥 Exportação")
        
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            csv_export = df_filtrado.to_csv(index=False, sep=';', decimal=',')
            st.download_button(
                "📄 Exportar CSV",
                data=csv_export,
                file_name=f"bolsas_analise_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            try:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_filtrado.to_excel(writer, sheet_name='Dados', index=False)
                st.download_button(
                    "📊 Exportar Excel",
                    data=output.getvalue(),
                    file_name=f"bolsas_analise_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except:
                st.download_button("📊 Exportar Excel", data="", file_name="dados.xlsx", disabled=True)
        
        with col3:
            relatorio = f"""
RELATÓRIO DE ANÁLISE
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

TOTAL INVESTIDO: {formatar_moeda(total_investido)}
PESQUISADORES: {total_pesquisadores:,}
INSTITUIÇÕES: {total_instituicoes:,}
TICKET MÉDIO: {formatar_moeda(ticket_medio)}
"""
            st.download_button(
                "📝 Exportar Relatório",
                data=relatorio,
                file_name=f"relatorio_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        # ========================================
        # RODAPÉ
        # ========================================
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; color:#64748b; padding:20px;">
        Dashboard desenvolvido com Streamlit • Plotly • Python • Fonte: CNPq
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("❌ Falha ao carregar o arquivo. Verifique o formato e tente novamente.")
else:
    # ========================================
    # TELA INICIAL
    # ========================================
    st.info("👈 **Faça upload do arquivo CSV no menu lateral para começar sua análise!**")
    
    st.markdown("""
    ### 📊 Sobre este Dashboard:
    
    - **213.735 bolsas de pesquisa** analisadas
    - **Mais de R$ 1 bilhão** em investimentos
    - **Filtros interativos** por região, período e área
    - **Gráficos dinâmicos** com Plotly
    - **Exportação** em CSV, Excel e TXT
    
    ### 🚀 Como usar:
    
    1. Baixe o CSV do Google Drive
    2. Faça upload no menu lateral
    3. Explore os filtros e gráficos
    """)
