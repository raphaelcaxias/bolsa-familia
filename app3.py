import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(
    page_title="CNPq Analytics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS COMPLETO
# ============================================================
st.markdown("""
<style>
/* Reset */
.stApp {
    background: #F5F7FA !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E8ECF0 !important;
    padding: 24px 16px !important;
}
section[data-testid="stSidebar"] * {
    color: #1A2B4C !important;
}
.sidebar-header {
    text-align: center;
    padding: 0 0 24px 0;
    border-bottom: 1px solid #E8ECF0;
    margin-bottom: 24px;
}
.sidebar-header h1 {
    font-size: 24px;
    color: #0A66C2 !important;
    margin: 0;
}
.sidebar-header p {
    font-size: 12px;
    color: #6B7A8F !important;
    margin-top: 6px;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #0A66C2 0%, #004182 100%);
    border-radius: 20px;
    padding: 40px 35px;
    margin-bottom: 35px;
    color: white;
}
.hero h1 {
    font-size: 36px;
    font-weight: 700;
    margin: 0 0 12px 0;
    color: white;
}
.hero p {
    font-size: 16px;
    opacity: 0.9;
    margin: 0;
    color: white;
}
.hero-badge {
    background: rgba(255,255,255,0.2);
    display: inline-block;
    padding: 6px 14px;
    border-radius: 30px;
    font-size: 12px;
    margin-top: 20px;
    color: white;
}

/* Feature Cards */
.feature-grid {
    display: flex;
    gap: 20px;
    margin: 30px 0;
}
.feature-card {
    flex: 1;
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    border: 1px solid #E8ECF0;
    transition: all 0.2s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    border-color: #0A66C2;
}
.feature-icon {
    font-size: 40px;
    margin-bottom: 16px;
}
.feature-title {
    font-size: 16px;
    font-weight: 700;
    color: #1A2B4C;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 13px;
    color: #6B7A8F;
    line-height: 1.5;
}

/* Stats Cards */
.stats-grid {
    display: flex;
    gap: 20px;
    margin: 30px 0;
}
.stat-card {
    flex: 1;
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    border: 1px solid #E8ECF0;
}
.stat-number {
    font-size: 32px;
    font-weight: 700;
    color: #0A66C2;
    margin: 8px 0;
}
.stat-label {
    font-size: 12px;
    color: #6B7A8F;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stat-icon {
    font-size: 28px;
}

/* Steps */
.steps-container {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #E8ECF0;
    margin: 20px 0;
}
.step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px 0;
    border-bottom: 1px solid #E8ECF0;
}
.step:last-child {
    border-bottom: none;
}
.step-number {
    width: 32px;
    height: 32px;
    background: #E8F4FD;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #0A66C2;
    font-size: 14px;
    flex-shrink: 0;
}
.step-content h4 {
    font-size: 14px;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0 0 4px 0;
}
.step-content p {
    font-size: 13px;
    color: #6B7A8F;
    margin: 0;
}

/* Info Cards */
.info-grid {
    display: flex;
    gap: 16px;
    margin-top: 20px;
    flex-wrap: wrap;
}
.info-card {
    flex: 1;
    min-width: 180px;
    background: #F5F7FA;
    border-radius: 12px;
    padding: 16px;
}
.info-card strong {
    color: #1A2B4C;
    font-size: 14px;
}
.info-card p {
    color: #6B7A8F;
    font-size: 12px;
    margin-top: 6px;
}

/* Status Bar */
.status-bar {
    background: #E8F4FD;
    border-left: 4px solid #0A66C2;
    padding: 12px 16px;
    border-radius: 10px;
    margin: 15px 0 20px 0;
    font-size: 13px;
    color: #1A2B4C;
}

/* KPIs */
.kpi-grid {
    display: flex;
    gap: 20px;
    margin: 20px 0 30px 0;
    flex-wrap: wrap;
}
.kpi-card {
    flex: 1;
    min-width: 180px;
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px 16px;
    text-align: center;
    border: 1px solid #E8ECF0;
}
.kpi-icon {
    font-size: 28px;
    margin-bottom: 8px;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    color: #6B7A8F;
    margin-bottom: 8px;
}
.kpi-number {
    font-size: 28px;
    font-weight: 700;
    color: #1A2B4C;
    line-height: 1.2;
    margin: 8px 0;
}
.kpi-sub {
    font-size: 11px;
    color: #6B7A8F;
}

/* Insight Cards */
.insight-grid {
    display: flex;
    gap: 20px;
    margin: 20px 0;
}
.insight-card {
    flex: 1;
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #E8ECF0;
}
.insight-icon {
    font-size: 32px;
    margin-bottom: 12px;
}
.insight-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    color: #6B7A8F;
    margin-bottom: 8px;
}
.insight-value {
    font-size: 24px;
    font-weight: 700;
    color: #0A66C2;
    margin: 10px 0;
}
.insight-desc {
    font-size: 13px;
    color: #6B7A8F;
}
.insight-desc strong {
    color: #1A2B4C;
}

/* Section Header */
.section-header {
    margin: 30px 0 20px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #E8ECF0;
    padding-bottom: 10px;
}
.section-header h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
}
.section-badge {
    background: #E8F4FD;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    color: #0A66C2;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 8px 20px;
    color: #6B7A8F;
    border: 1px solid #E8ECF0;
}
.stTabs [aria-selected="true"] {
    background: #0A66C2;
    color: white;
    border: none;
}

/* Botões */
.stDownloadButton button {
    background: #0A66C2 !important;
    color: white !important;
    border-radius: 24px !important;
    padding: 8px 20px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    width: 100% !important;
    border: none !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px 20px 20px;
    margin-top: 40px;
    border-top: 1px solid #E8ECF0;
    color: #6B7A8F;
    font-size: 11px;
}

/* Expander */
.streamlit-expanderHeader {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E8ECF0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES
# ============================================================
def fmt_brl(valor):
    if pd.isna(valor) or valor == 0:
        return "R$ 0"
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.1f}B".replace(".", ",")
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M".replace(".", ",")
    return f"R$ {valor:,.0f}".replace(",", ".")

def fmt_num(n):
    if pd.isna(n):
        return "0"
    return f"{int(n):,}".replace(",", ".")

@st.cache_data
def carregar_dados(uploaded_file):
    for encoding in ['latin1', 'utf-8', 'cp1252']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, delimiter=';', encoding=encoding, low_memory=False)
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
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h1>🔬 CNPq Analytics</h1>
        <p>Dashboard de Pesquisa e Inovação</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📄 Upload do CSV", type=["csv"])
    
    st.markdown("---")
    st.markdown("### 📊 Dataset")
    st.markdown("""
    - **213.735** registros
    - **26** colunas
    - **R$ 1B+** investimento
    - **2014-2027** período
    """)
    
    st.markdown("---")
    st.markdown("📥 **Baixar CSV original**")
    st.markdown("[Link Google Drive](https://drive.google.com/uc?export=download&id=1UXxWqTc6u8_RID_5BbpUI7JLwmgT01ub)")

# ============================================================
# MAIN
# ============================================================
if uploaded_file is not None:
    with st.spinner("🔄 Processando dados..."):
        df = carregar_dados(uploaded_file)
    
    if df is not None and len(df) > 0:
        
        # FILTROS
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Filtros")
        
        df_filtrado = df.copy()
        
        if 'regiao_nome' in df.columns:
            regioes = sorted(df['regiao_nome'].dropna().unique())
            reg_sel = st.sidebar.multiselect("📍 Região", regioes, default=regioes)
            if reg_sel:
                df_filtrado = df_filtrado[df_filtrado['regiao_nome'].isin(reg_sel)]
        
        if 'ano' in df.columns:
            anos = sorted(df['ano'].dropna().unique())
            if len(anos) > 1:
                ano_min, ano_max = int(min(anos)), int(max(anos))
                ano_sel = st.sidebar.slider("📅 Período", ano_min, ano_max, (ano_min, ano_max))
                df_filtrado = df_filtrado[(df_filtrado['ano'] >= ano_sel[0]) & (df_filtrado['ano'] <= ano_sel[1])]
        
        if 'grande_area' in df.columns:
            areas = sorted(df['grande_area'].dropna().unique())
            areas_sel = st.sidebar.multiselect("🧬 Grande Área", areas, default=areas[:6] if len(areas) > 6 else areas)
            if areas_sel:
                df_filtrado = df_filtrado[df_filtrado['grande_area'].isin(areas_sel)]
        
        # STATUS
        if df_filtrado.shape[0] < df.shape[0]:
            st.markdown(f'<div class="status-bar">🔍 <strong>{df_filtrado.shape[0]:,}</strong> de <strong>{df.shape[0]:,}</strong> registros ({100*df_filtrado.shape[0]/df.shape[0]:.1f}%)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-bar">✅ <strong>{df_filtrado.shape[0]:,}</strong> registros carregados</div>', unsafe_allow_html=True)
        
        # KPIs
        total_val = df_filtrado['valor_pago'].sum()
        media_val = df_filtrado['valor_pago'].mean()
        n_pesq = df_filtrado['beneficiario'].nunique() if 'beneficiario' in df_filtrado.columns else 0
        n_inst = df_filtrado['instituicao_destino'].nunique() if 'instituicao_destino' in df_filtrado.columns else 0
        n_bolsas = df_filtrado.shape[0]
        
        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-label">INVESTIMENTO TOTAL</div>
                <div class="kpi-number">{fmt_brl(total_val)}</div>
                <div class="kpi-sub">valor consolidado</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-label">PESQUISADORES</div>
                <div class="kpi-number">{fmt_num(n_pesq)}</div>
                <div class="kpi-sub">beneficiários únicos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🏛️</div>
                <div class="kpi-label">INSTITUIÇÕES</div>
                <div class="kpi-number">{fmt_num(n_inst)}</div>
                <div class="kpi-sub">unidades atendidas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🎫</div>
                <div class="kpi-label">TICKET MÉDIO</div>
                <div class="kpi-number">{fmt_brl(media_val)}</div>
                <div class="kpi-sub">por bolsa</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # TABS
        tab1, tab2, tab3 = st.tabs(["📊 Por Área", "🗺️ Por Região", "📈 Evolução"])
        
        with tab1:
            if 'grande_area' in df_filtrado.columns:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    area_data = df_filtrado.groupby('grande_area')['valor_pago'].sum().sort_values(ascending=False).head(10).reset_index()
                    area_data.columns = ['Área', 'Valor']
                    
                    fig = px.bar(area_data, x='Valor', y='Área', orientation='h',
                                color='Valor', color_continuous_scale=['#6B7A8F', '#0A66C2'],
                                text='Valor')
                    fig.update_layout(template="plotly_white", height=500, margin=dict(l=20, r=20, t=30, b=20))
                    fig.update_traces(texttemplate='R$ %{x:,.0f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    area_show = area_data.copy()
                    area_show['Valor'] = area_show['Valor'].apply(fmt_brl)
                    st.dataframe(area_show[['Área', 'Valor']], use_container_width=True, hide_index=True)
        
        with tab2:
            if 'regiao_nome' in df_filtrado.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    reg_data = df_filtrado.groupby('regiao_nome')['valor_pago'].sum().reset_index()
                    reg_data.columns = ['Região', 'Valor']
                    
                    fig2 = px.bar(reg_data, x='Região', y='Valor', color='Valor', color_continuous_scale='Blues', text='Valor')
                    fig2.update_layout(template="plotly_white", height=450, margin=dict(l=20, r=20, t=30, b=20))
                    fig2.update_traces(texttemplate='R$ %{y:,.0f}', textposition='outside')
                    st.plotly_chart(fig2, use_container_width=True)
                
                with col2:
                    fig3 = px.pie(reg_data, values='Valor', names='Região', hole=0.35)
                    fig3.update_layout(template="plotly_white", height=450)
                    fig3.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            if 'ano' in df_filtrado.columns:
                inv_ano = df_filtrado.groupby('ano')['valor_pago'].sum().reset_index()
                inv_ano = inv_ano.dropna()
                
                if len(inv_ano) > 1:
                    fig4 = px.area(inv_ano, x='ano', y='valor_pago', markers=True)
                    fig4.update_layout(template="plotly_white", height=450)
                    fig4.update_traces(line=dict(width=2, color='#0A66C2'), fillcolor='rgba(10,102,194,0.1)')
                    st.plotly_chart(fig4, use_container_width=True)
        
        # INSIGHTS
        st.markdown("""
        <div class="section-header">
            <h2>🔍 Insights Estratégicos</h2>
            <span class="section-badge">Análise</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'regiao_nome' in df_filtrado.columns:
                inv_reg = df_filtrado.groupby('regiao_nome')['valor_pago'].sum()
                if len(inv_reg) > 0:
                    top_reg = inv_reg.idxmax()
                    pct = 100 * inv_reg.max() / total_val
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-icon">📍</div>
                        <div class="insight-title">CONCENTRAÇÃO REGIONAL</div>
                        <div class="insight-value">{top_reg}</div>
                        <div class="insight-desc"><strong>{pct:.1f}%</strong> do investimento total</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if 'grande_area' in df_filtrado.columns:
                inv_area = df_filtrado.groupby('grande_area')['valor_pago'].sum()
                if len(inv_area) > 0:
                    top_area = inv_area.idxmax()
                    pct = 100 * inv_area.max() / total_val
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-icon">🧬</div>
                        <div class="insight-title">ÁREA LÍDER</div>
                        <div class="insight-value">{top_area}</div>
                        <div class="insight-desc"><strong>{pct:.1f}%</strong> dos recursos</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col3:
            if 'ano' in df_filtrado.columns and 'inv_ano' in locals() and len(inv_ano) >= 2:
                var = ((inv_ano['valor_pago'].iloc[-1] - inv_ano['valor_pago'].iloc[-2]) / inv_ano['valor_pago'].iloc[-2] * 100)
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-icon">📈</div>
                    <div class="insight-title">VARIAÇÃO ANUAL</div>
                    <div class="insight-value">{var:+.1f}%</div>
                    <div class="insight-desc">de {int(inv_ano['ano'].iloc[-2])} para {int(inv_ano['ano'].iloc[-1])}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # EXPORTAÇÃO
        st.markdown("""
        <div class="section-header">
            <h2>📥 Exportar Dados</h2>
            <span class="section-badge">Download</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = df_filtrado.to_csv(index=False, sep=';')
            st.download_button("📄 Exportar CSV", csv_data, f"cnpq_dados_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col2:
            relatorio = f"""RELATÓRIO CNPq ANALYTICS
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

INDICADORES:
- Investimento: {fmt_brl(total_val)}
- Pesquisadores: {fmt_num(n_pesq)}
- Instituições: {fmt_num(n_inst)}
- Ticket Médio: {fmt_brl(media_val)}
- Total de Bolsas: {fmt_num(n_bolsas)}

PERÍODO: {int(df_filtrado['ano'].min()) if 'ano' in df_filtrado.columns else 'N/A'} - {int(df_filtrado['ano'].max()) if 'ano' in df_filtrado.columns else 'N/A'}
"""
            st.download_button("📝 Exportar Relatório", relatorio, f"relatorio_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")
        
        # DADOS DETALHADOS
        with st.expander("🗂️ Visualizar Dados Detalhados"):
            cols_show = [c for c in df_filtrado.columns if c not in ['ano']][:10]
            st.dataframe(df_filtrado[cols_show].head(500), use_container_width=True, height=400)
            st.caption(f"Exibindo 500 de {df_filtrado.shape[0]:,} registros")
        
        # FOOTER
        st.markdown(f"""
        <div class="footer">
            🔬 CNPq Analytics · Streamlit & Plotly · Fonte: CNPq/Governo Federal<br>
            📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("❌ Erro ao carregar o arquivo.")

else:
    # ============================================================
    # TELA INICIAL - CORRIGIDA (sem bug de HTML)
    # ============================================================
    
    # Hero
    st.markdown("""
    <div class="hero">
        <h1>🔬 CNPq Analytics</h1>
        <p>Análise estratégica de investimentos em pesquisa e desenvolvimento no Brasil</p>
        <div class="hero-badge">📊 Dashboard Interativo</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Visualização Interativa</div>
            <div class="feature-desc">Gráficos dinâmicos com Plotly, filtros por região, período e área do conhecimento</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Insights Automáticos</div>
            <div class="feature-desc">Identificação de concentração regional, áreas líderes e variações anuais</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📥</div>
            <div class="feature-title">Exportação de Dados</div>
            <div class="feature-desc">Download dos dados filtrados em CSV e relatório executivo em TXT</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-number">213.735</div>
            <div class="stat-label">Registros</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-number">R$ 1B+</div>
            <div class="stat-label">Investimento</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🏛️</div>
            <div class="stat-number">26</div>
            <div class="stat-label">Colunas</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-number">2014-2027</div>
            <div class="stat-label">Período</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Steps
    st.markdown("""
    <div class="steps-container">
        <h3 style="color:#1A2B4C; margin-bottom: 20px;">🚀 Como começar</h3>
        
        <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
                <h4>Baixe o CSV original</h4>
                <p>Utilize o link no menu lateral para baixar o arquivo com 213.735 registros de bolsas do CNPq</p>
            </div>
        </div>
        
        <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
                <h4>Faça upload do arquivo</h4>
                <p>Clique em "Upload do CSV" no menu lateral e selecione o arquivo baixado</p>
            </div>
        </div>
        
        <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
                <h4>Explore os filtros</h4>
                <p>Utilize os filtros interativos para analisar por região, período e área do conhecimento</p>
            </div>
        </div>
        
        <div class="step">
            <div class="step-number">4</div>
            <div class="step-content">
                <h4>Exporte seus resultados</h4>
                <p>Baixe os dados filtrados em CSV ou gere um relatório executivo em TXT</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Info dados
    st.markdown("""
    <div style="background:#FFFFFF; border-radius:16px; padding:24px; margin-top:20px; border:1px solid #E8ECF0;">
        <h3 style="color:#1A2B4C; margin-bottom: 16px;">📋 Sobre os dados analisados</h3>
        <p style="color:#6B7A8F; margin-bottom: 16px;">Este dashboard processa dados públicos do CNPq sobre bolsas de pesquisa, abrangendo:</p>
        
        <div class="info-grid">
            <div class="info-card">
                <strong>🎓 213.735 bolsas</strong>
                <p>Iniciação científica, mestrado, doutorado e pós-doutorado</p>
            </div>
            <div class="info-card">
                <strong>🧬 12 áreas do conhecimento</strong>
                <p>Saúde, Engenharia, Humanas, Agrárias e mais</p>
            </div>
            <div class="info-card">
                <strong>📍 5 regiões + Exterior</strong>
                <p>Distribuição geográfica completa</p>
            </div>
            <div class="info-card">
                <strong>📅 2014 a 2027</strong>
                <p>Série histórica de 14 anos</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        🔬 CNPq Analytics · Desenvolvido com Streamlit & Plotly · Fonte: CNPq/Governo Federal<br>
        Dashboard para portfólio de Análise de Dados
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FIM
# ============================================================
